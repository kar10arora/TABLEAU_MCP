"""
Tableau XML workbook generator.
Safely manipulates .twb files using template injection.

Root cause fix: The entire datasource section (connection, columns, metadata-records,
object-graph) must be rebuilt from the actual CSV schema so Tableau can connect.
Simply patching the file path is not enough.
"""

import os
import hashlib
import uuid as uuid_mod
from lxml import etree
from typing import Dict
from src.core.uuid_utils import generate_tableau_uuid


class TableauXMLCompiler:
    """Compiles Tableau workbooks from JSON blueprints."""

    def __init__(self, template_path: str):
        if not os.path.exists(template_path):
            raise FileNotFoundError(f"Template not found: {template_path}")

        self.template_path = template_path
        self.parser = etree.XMLParser(remove_blank_text=False, recover=True)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def compile_workbook(self,
                         blueprint: Dict,
                         output_path: str,
                         dataset_path: str = None,
                         schema: Dict = None) -> Dict:
        """
        Generate a complete .twb workbook from a blueprint.

        Args:
            blueprint:    JSON blueprint with sheets configuration
            output_path:  Where to save the generated .twb file
            dataset_path: Absolute or relative path to the CSV file
            schema:       Optional schema dict from SchemaProfiler.
                          When provided the datasource is rebuilt so that
                          every column Tableau needs is declared correctly.

        Returns:
            {"success": bool, "workbook_path": str, "sheets_created": int}
        """
        tree = etree.parse(self.template_path, self.parser)
        root = tree.getroot()

        # ── 1. Rebuild datasource from real CSV ────────────────────────
        if dataset_path:
            abs_path = os.path.abspath(dataset_path)
            if schema is None:
                # Auto-profile if no schema provided
                from src.core.schema_profiler import SchemaProfiler
                schema = SchemaProfiler().profile_dataset(abs_path)
            self._rebuild_datasource(root, abs_path, schema)

        # ── 2. Extract the (now correct) datasource id ─────────────────
        ds_elem = root.find(".//datasources/datasource")
        if ds_elem is None:
            raise ValueError("Template missing datasource element")
        ds_id = ds_elem.get("name")

        # ── 3. Replace worksheets and windows ─────────────────────────
        worksheets_parent = root.find(".//worksheets")
        windows_parent = root.find(".//windows")
        if worksheets_parent is None or windows_parent is None:
            raise ValueError("Template missing worksheets or windows container")

        worksheets_parent.clear()
        windows_parent.clear()
        windows_parent.set("source-height", "30")

        sheets_created = 0
        for index, sheet in enumerate(blueprint.get("sheets", [])):
            try:
                sheet_uuid = generate_tableau_uuid()
                window_uuid = generate_tableau_uuid()

                col_field = sheet.get("column_field", "")
                row_field = sheet.get("row_field", "")
                sort_cfg = sheet.get("sort")          # optional sort block
                filters_cfg = sheet.get("filters")    # optional filters list

                # Determine datatypes from schema
                col_datatype, col_role, col_type = self._field_meta(col_field, schema)
                row_datatype, row_role, row_type = self._field_meta(row_field, schema)

                ws_xml = self._build_worksheet(
                    name=sheet["name"],
                    ds_id=ds_id,
                    cols=col_field,
                    rows=row_field,
                    col_datatype=col_datatype,
                    col_role=col_role,
                    col_type=col_type,
                    row_datatype=row_datatype,
                    row_role=row_role,
                    row_type=row_type,
                    mark_type=sheet.get("mark_type", "Automatic"),
                    uuid=sheet_uuid,
                    sort_cfg=sort_cfg,
                    schema=schema,
                    filters_cfg=filters_cfg,
                )
                win_xml = self._build_window(
                    name=sheet["name"],
                    uuid=window_uuid,
                    maximized=(index == 0),
                )

                worksheets_parent.append(etree.fromstring(ws_xml, self.parser))
                windows_parent.append(etree.fromstring(win_xml, self.parser))
                sheets_created += 1

            except Exception as exc:
                print(f"Warning: skipped sheet '{sheet.get('name')}': {exc}")

        tree.write(output_path, encoding="utf-8", xml_declaration=True)

        return {
            "success": True,
            "workbook_path": output_path,
            "sheets_created": sheets_created,
        }

    # ------------------------------------------------------------------
    # Datasource rebuild
    # ------------------------------------------------------------------

    def _rebuild_datasource(self, root, abs_csv_path: str, schema: Dict):
        """
        Completely replace the <datasource> element so Tableau can connect to
        the target CSV and knows about all its columns.
        """
        csv_filename = os.path.basename(abs_csv_path)
        csv_dir = os.path.dirname(abs_csv_path)
        csv_base = os.path.splitext(csv_filename)[0]          # e.g. "sales_sample"

        # Stable but unique IDs derived from the CSV name
        ds_name = self._stable_id("federated", csv_filename)
        conn_name = self._stable_id("textscan", csv_filename)
        obj_id = self._stable_obj_id(csv_filename)

        ds_caption = csv_base
        table_ref = f"[{csv_base}#csv]"

        # ── Build column ordinal list from schema ──────────────────────
        all_columns = []
        for d in schema.get("dimensions", []):
            datatype = self._infer_dimension_datatype(d)
            all_columns.append({"name": d["name"], "datatype": datatype})
        for m in schema.get("measures", []):
            dt = "integer" if isinstance(m.get("sample_values", [None])[0], int) else "real"
            all_columns.append({"name": m["name"], "datatype": dt})

        # ── Assemble <datasource> XML as a string then parse ──────────
        col_ordinals = "\n".join(
            "<column datatype='{}' name='{}' ordinal='{}' />".format(
                c["datatype"], c["name"], i
            )
            for i, c in enumerate(all_columns)
        )

        metadata_records = self._build_metadata_records(all_columns, csv_base, obj_id)
        column_declarations = self._build_column_declarations(all_columns, obj_id, csv_base)
        object_graph_cols = "\n".join(
            "<column datatype='{}' name='{}' ordinal='{}' />".format(
                c["datatype"], c["name"], i
            )
            for i, c in enumerate(all_columns)
        )

        ds_xml = f"""<datasource caption='{ds_caption}' inline='true' name='{ds_name}' version='18.1'>
  <connection class='federated'>
    <named-connections>
      <named-connection caption='{ds_caption}' name='{conn_name}'>
        <connection class='textscan'
          directory='{csv_dir}'
          filename='{csv_filename}'
          password=''
          server='' />
      </named-connection>
    </named-connections>
    <relation connection='{conn_name}' name='{csv_filename}' table='{table_ref}' type='table'>
      <columns character-set='UTF-8' header='yes' locale='en_US' separator=','>
{col_ordinals}
      </columns>
    </relation>
    <metadata-records>
{metadata_records}
    </metadata-records>
  </connection>
  <aliases enabled='yes' />
{column_declarations}
  <layout dim-ordering='alphabetic' measure-ordering='alphabetic' show-structure='true' />
  <object-graph>
    <objects>
      <object caption='{csv_filename}' id='{obj_id}'>
        <properties context=''>
          <relation connection='{conn_name}' name='{csv_filename}' table='{table_ref}' type='table'>
            <columns character-set='UTF-8' header='yes' locale='en_US' separator=','>
{object_graph_cols}
            </columns>
          </relation>
        </properties>
      </object>
    </objects>
  </object-graph>
</datasource>"""

        new_ds = etree.fromstring(ds_xml, self.parser)

        datasources_elem = root.find(".//datasources")
        # Remove old datasource(s)
        for old in datasources_elem.findall("datasource"):
            datasources_elem.remove(old)
        datasources_elem.append(new_ds)

    # ------------------------------------------------------------------
    # Worksheet / window builders
    # ------------------------------------------------------------------

    def _build_worksheet(self, name, ds_id, cols, rows,
                         col_datatype, col_role, col_type,
                         row_datatype, row_role, row_type,
                         mark_type, uuid,
                         sort_cfg=None, schema=None,
                         filters_cfg=None) -> str:

        cols_ref = f"[{ds_id}].[{cols}]" if cols else ""
        rows_ref = f"[{ds_id}].[{rows}]" if rows else ""

        # ── Build column-instance declarations for sorted fields ───────
        # Always emit column-instances for both shelved fields so Tableau
        # can resolve them; additionally include the sort field if different.
        col_instances, shelf_sorts = self._build_sort_xml(
            ds_id=ds_id,
            col_field=cols,
            row_field=rows,
            col_type=col_type,
            row_type=row_type,
            sort_cfg=sort_cfg,
            schema=schema,
        )

        # ── Build filter XML ──────────────────────────────────────────
        filters_xml = self._build_filters_xml(
            ds_id=ds_id,
            filters=filters_cfg,
            schema=schema,
        ) if filters_cfg else ""

        return f"""<worksheet name='{name}'>
  <table>
    <view>
      <datasources>
        <datasource name='{ds_id}' />
      </datasources>
      <datasource-dependencies datasource='{ds_id}'>
        <column datatype='{col_datatype}' name='[{cols}]' role='{col_role}' type='{col_type}' />
        <column datatype='{row_datatype}' name='[{rows}]' role='{row_role}' type='{row_type}' />{col_instances}{filters_xml}
      </datasource-dependencies>{shelf_sorts}
      <aggregation value='true' />
    </view>
    <style />
    <panes>
      <pane selection-relaxation-option='selection-relaxation-allow'>
        <view>
          <breakdown value='auto' />
        </view>
        <mark class='{mark_type}' />
      </pane>
    </panes>
    <rows>{rows_ref}</rows>
    <cols>{cols_ref}</cols>
  </table>
  <simple-id uuid='{uuid}' />
</worksheet>"""

    def _build_window(self, name: str, uuid: str, maximized: bool = False) -> str:
        maximized_attr = "maximized='true'" if maximized else ""
        return f"""<window class='worksheet' {maximized_attr} name='{name}'>
  <cards>
    <edge name='left'>
      <strip size='160'>
        <card type='pages' />
        <card type='filters' />
        <card type='marks' />
      </strip>
    </edge>
    <edge name='top'>
      <strip size='2147483647'>
        <card type='columns' />
      </strip>
      <strip size='2147483647'>
        <card type='rows' />
      </strip>
      <strip size='31'>
        <card type='title' />
      </strip>
    </edge>
  </cards>
  <simple-id uuid='{uuid}' />
</window>"""

    # ------------------------------------------------------------------
    # Filter XML builder (Story 2.3)
    # ------------------------------------------------------------------

    def _build_filters_xml(self, ds_id: str, filters: list, schema) -> str:
        """
        Build filter XML elements to inject inside <datasource-dependencies>.

        Each filter is a dict:
            {"field": "region", "operator": "=", "values": ["USA", "UK"]}

        Only categorical (dimension) filters are supported in this MVP.
        Multiple values → multi-member groupfilter.

        Returns XML string (empty if no valid filters).
        """
        if not filters:
            return ""

        lines = []
        for f in filters:
            field = f.get("field", "")
            values = f.get("values", [])
            if not field or not values:
                continue

            # Determine the field's datatype so we can emit the right column decl
            datatype, role, ftype = self._field_meta(field, schema)

            # Column declaration for the filter field
            lines.append(
                f"\n        <column datatype='{datatype}' name='[{field}]' "
                f"role='{role}' type='{ftype}' />"
            )

            if len(values) == 1:
                # Single-value categorical filter
                member = values[0]
                lines.append(f"""
        <filter class='categorical' column='[{field}]'>
          <groupfilter function='member' level='[{field}]'>
            <groupfilter function='level-members' level='[{field}]' member='{member}' />
          </groupfilter>
        </filter>""")
            else:
                # Multi-value categorical filter
                member_elements = "\n".join(
                    f"            <groupfilter function='level-members' level='[{field}]' member='{v}' />"
                    for v in values
                )
                lines.append(f"""
        <filter class='categorical' column='[{field}]'>
          <groupfilter function='union' level='[{field}]'>
{member_elements}
          </groupfilter>
        </filter>""")

        return "".join(lines)

    # ------------------------------------------------------------------
    # Sort XML builder (Story 2.2)
    # ------------------------------------------------------------------

    def _build_sort_xml(self, ds_id, col_field, row_field,
                        col_type, row_type, sort_cfg, schema):
        """
        Build column-instance declarations and optional <shelf-sorts> XML.

        Tableau requires <column-instance> elements for every field that
        participates in shelf expressions or sorting.

        Args:
            ds_id:     datasource federated name
            col_field: dimension on Columns shelf
            row_field: measure on Rows shelf
            col_type:  Tableau type for col_field ("nominal" | "quantitative")
            row_type:  Tableau type for row_field
            sort_cfg:  Optional dict:
                         {"field": str, "direction": "ASC"|"DESC", "type": "field"|"alphabetical"}
            schema:    Full schema dict (used to check sort field role)

        Returns:
            (col_instances_xml: str, shelf_sorts_xml: str)
            Both are empty strings when no sort is requested.
        """
        if not sort_cfg:
            return "", ""

        direction = sort_cfg.get("direction", "DESC").upper()
        if direction not in ("ASC", "DESC"):
            direction = "DESC"

        sort_type = sort_cfg.get("type", "field").lower()
        sort_field = sort_cfg.get("field", "")

        # ── Derive column-instance name tokens ────────────────────────
        # Tableau column-instance naming convention:
        #   dimension  → [none:<field>:nk]
        #   measure    → [sum:<field>:qk]
        def _ci_name(field, ftype):
            if ftype == "quantitative":
                return f"[sum:{field}:qk]"
            return f"[none:{field}:nk]"

        def _derivation(ftype):
            return "Sum" if ftype == "quantitative" else "None"

        # Column-instances for the two shelved fields
        col_ci_name = _ci_name(col_field, col_type)
        row_ci_name = _ci_name(row_field, row_type)

        ci_lines = [
            f"\n        <column-instance column='[{col_field}]' derivation='{_derivation(col_type)}' "
            f"name='{col_ci_name}' pivot='key' type='{col_type}' />",
            f"\n        <column-instance column='[{row_field}]' derivation='{_derivation(row_type)}' "
            f"name='{row_ci_name}' pivot='key' type='{row_type}' />",
        ]

        # If sort field is different from both shelved fields add its CI too
        if sort_field and sort_field not in (col_field, row_field):
            _, _, sort_ftype = self._field_meta(sort_field, schema)
            sort_ci_name = _ci_name(sort_field, sort_ftype)
            ci_lines.append(
                f"\n        <column-instance column='[{sort_field}]' "
                f"derivation='{_derivation(sort_ftype)}' "
                f"name='{sort_ci_name}' pivot='key' type='{sort_ftype}' />"
            )
        else:
            # sort field is one of the shelved fields — pick the correct CI
            if sort_field == col_field:
                sort_ci_name = col_ci_name
            else:
                sort_ci_name = row_ci_name

        col_instances_xml = "".join(ci_lines)

        # ── Build <shelf-sorts> ────────────────────────────────────────
        if sort_type == "alphabetical":
            # Sort the dimension column alphabetically
            dim_ci = _ci_name(col_field, col_type)
            shelf_sorts_xml = f"""
    <shelf-sorts>
      <shelf-sort-v2 direction='{direction}' field='[{ds_id}].{dim_ci}' is-on-innermost-dimension='true' shelf='rows' />
    </shelf-sorts>"""
        else:
            # Default: sort dimension by measure value (field sort)
            # dimension-to-sort = the CI of the column (dimension) shelf
            # measure-to-sort-by = the CI of the measure (row) shelf or explicit sort field
            dim_ci = _ci_name(col_field, col_type)
            measure_ci = _ci_name(sort_field, row_type) if sort_field else row_ci_name
            shelf_sorts_xml = f"""
    <shelf-sorts>
      <shelf-sort-v2 dimension-to-sort='[{ds_id}].{dim_ci}' direction='{direction}' is-on-innermost-dimension='true' measure-to-sort-by='[{ds_id}].{measure_ci}' shelf='rows' />
    </shelf-sorts>"""

        return col_instances_xml, shelf_sorts_xml

    # ------------------------------------------------------------------
    # Schema helpers
    # ------------------------------------------------------------------

    def _field_meta(self, field_name: str, schema: Dict):
        """Return (datatype, role, type) tuple for a field name from schema."""
        if schema:
            for d in schema.get("dimensions", []):
                if d["name"] == field_name:
                    # Detect date fields by name convention or sample values
                    datatype = self._infer_dimension_datatype(d)
                    return datatype, "dimension", "nominal"
            for m in schema.get("measures", []):
                if m["name"] == field_name:
                    sample = m.get("sample_values", [None])[0]
                    dt = "integer" if isinstance(sample, int) else "real"
                    return dt, "measure", "quantitative"
        return "string", "dimension", "nominal"

    @staticmethod
    def _infer_dimension_datatype(dim: Dict) -> str:
        """
        Infer whether a dimension is a date, datetime, or plain string.
        Checks field name hints first, then sample values.
        """
        name = dim.get("name", "").lower()

        # Name-based heuristics
        date_keywords = ("date", "time", "year", "month", "day", "week",
                         "quarter", "timestamp", "created", "updated")
        if any(kw in name for kw in date_keywords):
            return "date"

        # Sample-value heuristics
        import re
        date_patterns = [
            r"^\d{4}-\d{2}-\d{2}$",            # 2024-01-15
            r"^\d{2}/\d{2}/\d{4}$",             # 01/15/2024
            r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}", # ISO datetime
            r"^\d{4}$",                          # bare year e.g. 2024
            r"^(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)",  # month names
            r"^Q[1-4] \d{4}$",                  # Q1 2024
        ]
        for val in dim.get("sample_values", []):
            s = str(val).strip()
            if any(re.match(p, s, re.IGNORECASE) for p in date_patterns):
                return "date"

        return "string"

    def _build_metadata_records(self, columns, csv_base, obj_id) -> str:
        records = []
        # capability record
        records.append(f"""      <metadata-record class='capability'>
        <remote-name />
        <remote-type>0</remote-type>
        <parent-name>[{csv_base}.csv]</parent-name>
        <remote-alias />
        <aggregation>Count</aggregation>
        <contains-null>true</contains-null>
      </metadata-record>""")

        # remote-type mapping: string=129, real=5, integer=20, date=7
        REMOTE_TYPE = {"string": "129", "real": "5", "integer": "20", "date": "7"}
        AGG = {"string": "Count", "real": "Sum", "integer": "Sum", "date": "None"}
        LOCAL_TYPE = {"string": "string", "real": "real", "integer": "integer", "date": "date"}

        for i, col in enumerate(columns):
            dt = col["datatype"]
            remote_type = REMOTE_TYPE.get(dt, "129")
            agg = AGG.get(dt, "Count")
            local_type = LOCAL_TYPE.get(dt, "string")
            is_string = dt in ("string", "date")
            extra = """
        <scale>1</scale>
        <width>1073741823</width>
        <collation flag='0' name='LEN_RGB' />""" if is_string else ""
            records.append(f"""      <metadata-record class='column'>
        <remote-name>{col['name']}</remote-name>
        <remote-type>{remote_type}</remote-type>
        <local-name>[{col['name']}]</local-name>
        <parent-name>[{csv_base}.csv]</parent-name>
        <remote-alias>{col['name']}</remote-alias>
        <ordinal>{i}</ordinal>
        <local-type>{local_type}</local-type>
        <aggregation>{agg}</aggregation>
        <contains-null>true</contains-null>{extra}
        <object-id>[{obj_id}]</object-id>
      </metadata-record>""")
        return "\n".join(records)

    def _build_column_declarations(self, columns, obj_id, csv_base) -> str:
        # internal object-id column
        lines = [f"  <column caption='{csv_base}.csv' datatype='table' "
                 f"name='[__tableau_internal_object_id__].[{obj_id}]' "
                 f"role='measure' type='quantitative' />"]
        for col in columns:
            is_measure = col["datatype"] in ("real", "integer")
            role = "measure" if is_measure else "dimension"
            col_type = "quantitative" if is_measure else "nominal"
            caption = col["name"].replace("_", " ").title()
            col_name = col["name"]
            lines.append(
                "<column caption='{}' datatype='{}' name='[{}]' role='{}' type='{}' />".format(
                    caption, col["datatype"], col_name, role, col_type
                )
            )
        return "\n".join(lines)

    # ------------------------------------------------------------------
    # ID generators — deterministic so re-running gives same IDs
    # ------------------------------------------------------------------

    @staticmethod
    def _stable_id(prefix: str, seed: str) -> str:
        h = hashlib.md5(seed.encode()).hexdigest()
        # Format like Tableau's own IDs  e.g. federated.1n9e10m...
        return f"{prefix}.{h}"

    @staticmethod
    def _stable_obj_id(seed: str) -> str:
        h = hashlib.md5(seed.encode()).hexdigest().upper()
        # Format like amazon.csv_3C161C9012F4457FB86D06CC11821000
        name = os.path.splitext(seed)[0]
        return f"{name}_{h}"
