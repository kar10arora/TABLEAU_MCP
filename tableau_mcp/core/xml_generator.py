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
from tableau_mcp.core.uuid_utils import generate_tableau_uuid


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
                from tableau_mcp.core.schema_profiler import SchemaProfiler
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

                mark_type = sheet.get("mark_type", "Automatic")
                aggregation = sheet.get("aggregation")  # optional aggregation function

                if mark_type == "Text":
                    # ── KPI / Text-mark path (Story 2.5) ──────────────────────
                    row_field = sheet.get("row_field", "")
                    row_field_primary = row_field[0] if isinstance(row_field, list) else row_field
                    row_datatype, row_role, row_type = self._field_meta(row_field_primary, schema)

                    ws_xml = self._build_kpi_worksheet(
                        name=sheet["name"],
                        ds_id=ds_id,
                        row_field=row_field_primary,
                        row_datatype=row_datatype,
                        row_role=row_role,
                        row_type=row_type,
                        uuid=sheet_uuid,
                        aggregation=aggregation,
                        format_cfg=sheet.get("format"),
                    )
                else:
                    # ── Regular chart path ─────────────────────────────────────
                    col_field = sheet.get("column_field") or ""
                    row_field = sheet.get("row_field", "")
                    sort_cfg = sheet.get("sort")
                    filters_cfg = sheet.get("filters")
                    encodings_cfg = sheet.get("encodings")

                    # Use primary field for metadata lookup (handles both string and list)
                    col_field_primary = col_field[0] if isinstance(col_field, list) else col_field
                    row_field_primary = row_field[0] if isinstance(row_field, list) else row_field

                    # Determine datatypes from schema
                    col_datatype, col_role, col_type = self._field_meta(col_field_primary, schema)
                    row_datatype, row_role, row_type = self._field_meta(row_field_primary, schema)

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
                        mark_type=mark_type,
                        uuid=sheet_uuid,
                        sort_cfg=sort_cfg,
                        schema=schema,
                        filters_cfg=filters_cfg,
                        encodings_cfg=encodings_cfg,
                        aggregation=aggregation,
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
                         filters_cfg=None, encodings_cfg=None,
                         aggregation=None) -> str:

        agg = self._normalize_aggregation(aggregation)
        agg_abbrev = self._get_aggregation_abbrev(agg)

        # Normalize fields to lists for uniform processing
        cols_list = cols if isinstance(cols, list) else ([cols] if cols else [])
        rows_list = rows if isinstance(rows, list) else ([rows] if rows else [])

        cols_primary = cols_list[0] if cols_list else ""
        rows_primary = rows_list[0] if rows_list else ""

        # ── Column-instance name helpers (use current aggregation) ─────
        def _ci_name(field, ftype):
            return f"[{agg_abbrev}:{field}:qk]" if ftype == "quantitative" else f"[none:{field}:nk]"

        def _derivation(ftype):
            return agg if ftype == "quantitative" else "None"

        # ── Shelf references (cols_ref / rows_ref) ─────────────────────
        if len(cols_list) > 1:
            cols_ref = self._build_field_reference(cols_list, ds_id, "dimension")
        elif cols_list:
            cols_ref = f"[{ds_id}].{_ci_name(cols_primary, col_type)}"
        else:
            cols_ref = ""

        if len(rows_list) > 1:
            rows_ref = self._build_field_reference(rows_list, ds_id, "measure", agg)
        elif rows_list:
            rows_ref = f"[{ds_id}].{_ci_name(rows_primary, row_type)}"
        else:
            rows_ref = ""

        # ── Column declarations for datasource-dependencies ────────────
        # One <column> per field (handles multi-dimension arrays)
        col_field_decls = ""
        for field in cols_list:
            if field:
                dt, role, ftype = self._field_meta(field, schema)
                col_field_decls += (
                    f"\n        <column datatype='{dt}' name='[{field}]' "
                    f"role='{role}' type='{ftype}' />"
                )
        for field in rows_list:
            if field:
                dt, role, ftype = self._field_meta(field, schema)
                col_field_decls += (
                    f"\n        <column datatype='{dt}' name='[{field}]' "
                    f"role='{role}' type='{ftype}' />"
                )

        # ── Column-instance declarations + shelf-sorts XML ─────────────
        col_instances, shelf_sorts_xml = self._build_sort_xml(
            ds_id=ds_id,
            col_field=cols_primary,
            row_field=rows_primary,
            col_type=col_type,
            row_type=row_type,
            sort_cfg=sort_cfg,
            schema=schema,
            aggregation=agg,
        )

        # Build column-instances for all fields (augment sort-provided or build from scratch)
        if not col_instances:
            ci_parts = []
            for field in cols_list:
                if field:
                    _, _, ftype = self._field_meta(field, schema)
                    ci_parts.append(
                        f"\n        <column-instance column='[{field}]' "
                        f"derivation='{_derivation(ftype)}' "
                        f"name='{_ci_name(field, ftype)}' pivot='key' type='{ftype}' />"
                    )
            for field in rows_list:
                if field:
                    _, _, ftype = self._field_meta(field, schema)
                    ci_parts.append(
                        f"\n        <column-instance column='[{field}]' "
                        f"derivation='{_derivation(ftype)}' "
                        f"name='{_ci_name(field, ftype)}' pivot='key' type='{ftype}' />"
                    )
            col_instances = "".join(ci_parts)
        elif len(cols_list) > 1:
            # Sort gave instances for the primary field; prepend extras for additional dims
            extra_ci = []
            for field in cols_list[1:]:
                if field:
                    _, _, ftype = self._field_meta(field, schema)
                    extra_ci.append(
                        f"\n        <column-instance column='[{field}]' "
                        f"derivation='{_derivation(ftype)}' "
                        f"name='{_ci_name(field, ftype)}' pivot='key' type='{ftype}' />"
                    )
            col_instances = "".join(extra_ci) + col_instances

        # ── Add declarations for filtered fields ───────────────────────
        filter_field_decls = self._build_filter_field_declarations(filters_cfg, schema)

        # ── Add declarations for encoded fields ────────────────────────
        encoding_field_decls = self._build_encoding_field_declarations(encodings_cfg, schema)

        # ── Build filter XML ───────────────────────────────────────────
        filters_xml, slices_xml = self._build_filters_xml_and_slices(
            ds_id=ds_id,
            filters=filters_cfg,
            schema=schema,
        ) if filters_cfg else ("", "")

        # ── Build encoding XML ─────────────────────────────────────────
        encodings_xml = self._build_encodings_xml(
            ds_id=ds_id,
            encodings=encodings_cfg,
            schema=schema,
            aggregation=agg,
        )

        return f"""<worksheet name='{name}'>
  <table>
    <view>
      <datasources>
        <datasource name='{ds_id}' />
      </datasources>
      <datasource-dependencies datasource='{ds_id}'>{col_field_decls}{col_instances}{filter_field_decls}{encoding_field_decls}
      </datasource-dependencies>{filters_xml}{shelf_sorts_xml}{slices_xml}
      <aggregation value='true' />
    </view>
    <style />
    <panes>
      <pane selection-relaxation-option='selection-relaxation-allow'>
        <view>
          <breakdown value='auto' />
        </view>
        <mark class='{mark_type}' />{encodings_xml}
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
    # KPI / Text-mark builder (Story 2.5)
    # ------------------------------------------------------------------

    def _build_kpi_worksheet(self, name: str, ds_id: str,
                              row_field: str, row_datatype: str,
                              row_role: str, row_type: str,
                              uuid: str,
                              aggregation: str = None,
                              format_cfg: dict = None) -> str:
        """
        Build a Text-mark KPI worksheet.

        Unlike regular charts, KPI sheets:
        - Have no column shelf dimension (rows/cols are empty)
        - Show a single aggregated number via <encodings><text>
        - Use a <style> block so the number renders large and visible
        - Support optional number formatting via format_cfg["number_format"]
        - Support optional font-size override via format_cfg["font_size"]

        Blueprint example:
            {"mark_type": "Text", "row_field": "sales",
             "aggregation": "Sum",
             "format": {"number_format": "$#,##0", "font_size": 24}}
        """
        agg = self._normalize_aggregation(aggregation)
        agg_abbrev = self._get_aggregation_abbrev(agg)

        ci_name = f"[{agg_abbrev}:{row_field}:qk]"
        fq_column = f"[{ds_id}].{ci_name}"

        # Optional number format attribute on the column declaration
        num_format_attr = ""
        if format_cfg and format_cfg.get("number_format"):
            num_format_attr = f" default-format='{format_cfg['number_format']}'"

        # Optional font-size style rule
        font_style_rule = ""
        if format_cfg and format_cfg.get("font_size"):
            font_style_rule = (
                f"\n      <style-rule element='label'>"
                f"\n        <format attr='font-size' value='{format_cfg['font_size']}' />"
                f"\n      </style-rule>"
            )

        return f"""<worksheet name='{name}'>
  <table>
    <view>
      <datasources>
        <datasource name='{ds_id}' />
      </datasources>
      <datasource-dependencies datasource='{ds_id}'>
        <column datatype='{row_datatype}' name='[{row_field}]' role='{row_role}' type='{row_type}'{num_format_attr} />
        <column-instance column='[{row_field}]' derivation='{agg}' name='{ci_name}' pivot='key' type='{row_type}' />
      </datasource-dependencies>
      <aggregation value='true' />
    </view>
    <style>
      <style-rule element='mark'>
        <format attr='size' value='2' />
        <format attr='mark-labels-show' value='true' />
        <format attr='mark-labels-cull' value='false' />
      </style-rule>{font_style_rule}
    </style>
    <panes>
      <pane>
        <view>
          <breakdown value='auto' />
        </view>
        <mark class='Text' />
        <encodings>
          <text column='{fq_column}' />
        </encodings>
      </pane>
    </panes>
    <rows />
    <cols />
  </table>
  <simple-id uuid='{uuid}' />
</worksheet>"""

    # ------------------------------------------------------------------
    # Filter XML builder (Story 2.3)
    # ------------------------------------------------------------------

    def _build_encoding_field_declarations(self, encodings: dict, schema) -> str:
        """
        Build <column> and <column-instance> declarations for encoding fields.
        These must be added to <datasource-dependencies> so that encodings can reference them.

        Returns XML string (empty if no valid encodings).
        """
        if not encodings:
            return ""

        lines = []
        seen_fields = set()

        # Extract all fields from encodings (color, size, tooltip)
        fields_to_declare = set()
        if encodings.get("color") and encodings["color"].get("field"):
            fields_to_declare.add(encodings["color"]["field"])
        if encodings.get("size") and encodings["size"].get("field"):
            fields_to_declare.add(encodings["size"]["field"])
        if encodings.get("tooltip"):
            tooltip_fields = encodings["tooltip"]
            if isinstance(tooltip_fields, list):
                fields_to_declare.update(tooltip_fields)
            elif isinstance(tooltip_fields, str):
                fields_to_declare.add(tooltip_fields)

        for field in fields_to_declare:
            if not field or field in seen_fields:
                continue
            seen_fields.add(field)

            datatype, role, ftype = self._field_meta(field, schema)
            ci_name = f"[none:{field}:nk]" if ftype != "quantitative" else f"[sum:{field}:qk]"
            derivation = "None" if ftype != "quantitative" else "Sum"

            # Add column declaration
            lines.append(
                f"\n        <column datatype='{datatype}' name='[{field}]' role='{role}' type='{ftype}' />"
            )
            # Add column-instance declaration
            lines.append(
                f"\n        <column-instance column='[{field}]' derivation='{derivation}' "
                f"name='{ci_name}' pivot='key' type='{ftype}' />"
            )

        return "".join(lines)

    def _build_filter_field_declarations(self, filters: list, schema) -> str:
        """
        Build <column> and <column-instance> declarations for filter fields.
        These must be added to <datasource-dependencies> so that filters can reference them.

        Returns XML string (empty if no valid filters).
        """
        if not filters:
            return ""

        lines = []
        seen_fields = set()

        for f in filters:
            field = f.get("field", "")
            if not field or field in seen_fields:
                continue
            seen_fields.add(field)

            datatype, role, ftype = self._field_meta(field, schema)
            ci_name = f"[none:{field}:nk]" if ftype != "quantitative" else f"[sum:{field}:qk]"
            derivation = "None" if ftype != "quantitative" else "Sum"

            # Add column declaration
            lines.append(
                f"\n        <column datatype='{datatype}' name='[{field}]' role='{role}' type='{ftype}' />"
            )
            # Add column-instance declaration
            lines.append(
                f"\n        <column-instance column='[{field}]' derivation='{derivation}' "
                f"name='{ci_name}' pivot='key' type='{ftype}' />"
            )

        return "".join(lines)

    def _build_filters_xml_and_slices(self, ds_id: str, filters: list, schema):
        """
        Build filter XML elements and slices for <view> (outside datasource-dependencies).

        Each filter is a dict:
            {"field": "region", "operator": "=", "values": ["USA", "UK"]}

        Returns (filters_xml, slices_xml) tuple. Both empty if no valid filters.

        Filter structure:
          <filter class='categorical' column='[ds_id].[none:field:nk]'>
            <groupfilter function='union' user:ui-domain='database' ...>
              <groupfilter function='member' level='[none:field:nk]' member='&quot;USA&quot;'/>
            </groupfilter>
          </filter>
          <slices>
            <column>[ds_id].[none:field:nk]</column>
          </slices>
        """
        if not filters:
            return "", ""

        filter_lines = []
        slice_columns = []

        for f in filters:
            field = f.get("field", "")
            values = f.get("values", [])
            if not field or not values:
                continue

            # Determine field's type to construct column-instance name
            datatype, role, ftype = self._field_meta(field, schema)
            ci_name = f"[none:{field}:nk]" if ftype != "quantitative" else f"[sum:{field}:qk]"
            fq_column = f"[{ds_id}].{ci_name}"

            # Track for slices element
            slice_columns.append(fq_column)

            if len(values) == 1:
                # Single-value: use function='member'
                member = values[0]
                member_quoted = f"&quot;{member}&quot;"
                filter_lines.append(f"""
      <filter class='categorical' column='{fq_column}'>
        <groupfilter function='member' level='{ci_name}' member='{member_quoted}'>
        </groupfilter>
      </filter>""")
            else:
                # Multi-value: use function='union'
                member_elements = "\n".join(
                    f"        <groupfilter function='member' level='{ci_name}' member='&quot;{v}&quot;'/>"
                    for v in values
                )
                filter_lines.append(f"""
      <filter class='categorical' column='{fq_column}'>
        <groupfilter function='union' user:ui-domain='database' user:ui-enumeration='inclusive' user:ui-marker='enumerate'>
{member_elements}
        </groupfilter>
      </filter>""")

        filters_xml = "".join(filter_lines)

        # Build slices element
        if slice_columns:
            slice_items = "\n".join(f"        <column>{col}</column>" for col in slice_columns)
            slices_xml = f"""
      <slices>
{slice_items}
      </slices>"""
        else:
            slices_xml = ""

        return filters_xml, slices_xml

    def _build_encodings_xml(self, ds_id: str, encodings: dict, schema,
                             aggregation: str = None) -> str:
        """
        Build <encodings> element with <color>, <size>, <text> children (Story 2.4).

        Encodings go inside <pane>, after <mark> element.

        Returns XML string with wrapper (empty if no valid encodings).
        """
        if not encodings:
            return ""

        agg_abbrev = self._get_aggregation_abbrev(self._normalize_aggregation(aggregation))

        def _ci(field, ftype):
            return f"[none:{field}:nk]" if ftype != "quantitative" else f"[{agg_abbrev}:{field}:qk]"

        lines = []

        # Color encoding
        if encodings.get("color"):
            field = encodings["color"].get("field", "")
            if field:
                _, _, ftype = self._field_meta(field, schema)
                lines.append(f"\n        <color column='[{ds_id}].{_ci(field, ftype)}' />")

        # Size encoding
        if encodings.get("size"):
            field = encodings["size"].get("field", "")
            if field:
                _, _, ftype = self._field_meta(field, schema)
                lines.append(f"\n        <size column='[{ds_id}].{_ci(field, ftype)}' />")

        # Tooltip encoding (stored as 'text' in Tableau XML)
        if encodings.get("tooltip"):
            tooltip_fields = encodings["tooltip"]
            if not isinstance(tooltip_fields, list):
                tooltip_fields = [tooltip_fields]
            for field in tooltip_fields:
                if field:
                    _, _, ftype = self._field_meta(field, schema)
                    lines.append(f"\n        <text column='[{ds_id}].{_ci(field, ftype)}' />")

        if not lines:
            return ""

        return f"\n      <encodings>{''.join(lines)}\n      </encodings>"

    # ------------------------------------------------------------------
    # Sort XML builder (Story 2.2)
    # ------------------------------------------------------------------

    def _build_sort_xml(self, ds_id, col_field, row_field,
                        col_type, row_type, sort_cfg, schema,
                        aggregation=None):
        """
        Build column-instance declarations and shelf-sort XML.

        Pattern taken directly from a working Tableau TWB (automated_test.twb):

          <datasource-dependencies datasource='...'>
            <column-instance column='[product_id]' derivation='None'
                             name='[none:product_id:nk]' pivot='key' type='nominal'/>
            <column-instance column='[rating]' derivation='Avg'
                             name='[avg:rating:qk]' pivot='key' type='quantitative'/>
          </datasource-dependencies>
          <shelf-sorts>
            <shelf-sort-v2
              dimension-to-sort='[ds_id].[none:product_id:nk]'
              direction='ASC'
              is-on-innermost-dimension='true'
              measure-to-sort-by='[ds_id].[avg:rating:qk]'
              shelf='columns' />
          </shelf-sorts>

        Key rules:
        - Uses <shelf-sorts>/<shelf-sort-v2>, NOT <sort>
        - dimension-to-sort  = fully qualified: [ds_id].[none:col_field:nk]
        - measure-to-sort-by = fully qualified: [ds_id].[sum:row_field:qk]
        - shelf = 'columns' because the DIMENSION is on the Columns shelf
        - <rows> and <cols> also reference CI names, not raw field names
        - <shelf-sorts> sits INSIDE <view>, sibling of <datasource-dependencies>

        Alphabetical sort: same structure but omit measure-to-sort-by.

        Returns:
            (col_instances_xml: str, shelf_sorts_xml: str)
            Both are empty strings when no sort is requested.
        """
        if not sort_cfg:
            return "", ""

        agg = self._normalize_aggregation(aggregation)
        agg_abbrev = self._get_aggregation_abbrev(agg)

        direction = sort_cfg.get("direction", "DESC").upper()
        if direction not in ("ASC", "DESC"):
            direction = "DESC"

        sort_type = sort_cfg.get("type", "field").lower()
        sort_field = sort_cfg.get("field", "")

        # ── Column-instance name helpers (use current aggregation) ────
        def _ci_name(field, ftype):
            if ftype == "quantitative":
                return f"[{agg_abbrev}:{field}:qk]"
            return f"[none:{field}:nk]"

        def _derivation(ftype):
            return agg if ftype == "quantitative" else "None"

        # Column-instances for the two shelved fields
        col_ci_name = _ci_name(col_field, col_type)   # dim on Columns shelf
        row_ci_name = _ci_name(row_field, row_type)   # measure on Rows shelf

        ci_lines = [
            f"\n        <column-instance column='[{col_field}]' derivation='{_derivation(col_type)}' "
            f"name='{col_ci_name}' pivot='key' type='{col_type}' />",
            f"\n        <column-instance column='[{row_field}]' derivation='{_derivation(row_type)}' "
            f"name='{row_ci_name}' pivot='key' type='{row_type}' />",
        ]

        # Add CI for explicit sort field if different from both shelved fields
        if sort_field and sort_field not in (col_field, row_field):
            _, _, sort_ftype = self._field_meta(sort_field, schema)
            sort_ci_name = _ci_name(sort_field, sort_ftype)
            ci_lines.append(
                f"\n        <column-instance column='[{sort_field}]' "
                f"derivation='{_derivation(sort_ftype)}' "
                f"name='{sort_ci_name}' pivot='key' type='{sort_ftype}' />"
            )
        else:
            sort_ci_name = col_ci_name if sort_field == col_field else row_ci_name

        col_instances_xml = "".join(ci_lines)

        # ── Build <shelf-sorts> ────────────────────────────────────────
        # The dimension (col_field) lives on the Columns shelf → shelf='columns'
        dim_fq  = f"[{ds_id}].{col_ci_name}"    # fully qualified dim CI

        if sort_type == "alphabetical":
            # Alphabetical sort — measure-to-sort-by is still required by DTD
            # Point it to the row measure (the aggregated field on the Rows shelf)
            meas_fq = f"[{ds_id}].{row_ci_name}"
            shelf_sorts_xml = (
                f"\n    <shelf-sorts>\n"
                f"      <shelf-sort-v2 dimension-to-sort='{dim_fq}' "
                f"direction='{direction}' "
                f"is-on-innermost-dimension='true' "
                f"measure-to-sort-by='{meas_fq}' "
                f"shelf='columns' />\n"
                f"    </shelf-sorts>"
            )
        else:
            # Field / measure sort
            if sort_field and sort_field != col_field:
                _, _, sf_type = self._field_meta(sort_field, schema)
                meas_fq = f"[{ds_id}].{_ci_name(sort_field, sf_type)}"
            else:
                meas_fq = f"[{ds_id}].{row_ci_name}"   # e.g. [ds].[sum:sales:qk]

            shelf_sorts_xml = (
                f"\n    <shelf-sorts>\n"
                f"      <shelf-sort-v2 dimension-to-sort='{dim_fq}' "
                f"direction='{direction}' "
                f"is-on-innermost-dimension='true' "
                f"measure-to-sort-by='{meas_fq}' "
                f"shelf='columns' />\n"
                f"    </shelf-sorts>"
            )

        return col_instances_xml, shelf_sorts_xml

    # ------------------------------------------------------------------
    # Schema helpers
    # ------------------------------------------------------------------

    def _normalize_aggregation(self, agg_name: str) -> str:
        """
        Normalize an aggregation name to Tableau's display form regardless of input casing.
        e.g. "SUM" → "Sum", "avg" → "Avg", "COUNTD" → "CountD"
        """
        display_map = {
            "sum": "Sum", "avg": "Avg", "min": "Min", "max": "Max",
            "median": "Median", "count": "Count", "countd": "CountD",
            "stdev": "StdDev", "stddev": "StdDev",
        }
        if not agg_name:
            return "Sum"
        return display_map.get(agg_name.lower(), agg_name)

    def _get_aggregation_abbrev(self, agg_name: str) -> str:
        """Map aggregation display name to Tableau XML abbreviation (case-insensitive)."""
        abbrev_map = {
            "sum": "sum", "avg": "avg", "min": "min", "max": "max",
            "median": "median", "count": "cnt", "countd": "countd",
            "stdev": "stdev", "stddev": "stdev",
        }
        if not agg_name:
            return "sum"
        return abbrev_map.get(agg_name.lower(), "sum")

    def _build_field_reference(self, field_or_fields, ds_id: str,
                                field_type: str = "dimension",
                                aggregation: str = None) -> str:
        """
        Build Tableau shelf reference(s) for XML.

        Handles single fields (str) and multi-field arrays that get concatenated
        with " + " so Tableau renders them as a combined axis.

        field_type: "dimension" → nk suffix, "measure" → qk suffix + aggregation
        """
        agg_abbrev = self._get_aggregation_abbrev(aggregation or "Sum")

        if isinstance(field_or_fields, list):
            refs = []
            for field in field_or_fields:
                if field_type == "dimension":
                    refs.append(f'[{ds_id}].[none:{field}:nk]')
                else:
                    refs.append(f'[{ds_id}].[{agg_abbrev}:{field}:qk]')
            return ' + '.join(refs)
        else:
            if field_type == "dimension":
                return f'[{ds_id}].[none:{field_or_fields}:nk]'
            else:
                return f'[{ds_id}].[{agg_abbrev}:{field_or_fields}:qk]'

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
