"""
Tests for Story 2.3: Basic Filtering

Correct pattern (from working TWB):
  - <filter> is OUTSIDE <datasource-dependencies>, inside <view>
  - column attr uses fully-qualified CI name: [ds_id].[none:field:nk]
  - member values are quoted: member='&quot;USA&quot;'
  - <slices> element follows each filter
  - _build_filters_xml returns a tuple (col_decls_str, filter_view_str)
"""

import os
import sys
import tempfile

import pytest
from lxml import etree

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.core.schema_profiler import SchemaProfiler
from src.core.xml_generator import TableauXMLCompiler
from src.llm.client import LLMClient

TEMPLATE = "templates/base_template.twb"
DATASET = "examples/sample_datasets/sales_sample.csv"

_profiler = SchemaProfiler()
_SCHEMA = _profiler.profile_dataset(DATASET)


def _compile(blueprint, dataset=DATASET, schema=_SCHEMA):
    compiler = TableauXMLCompiler(TEMPLATE)
    with tempfile.NamedTemporaryFile(delete=False, suffix=".twb") as f:
        out = f.name
    result = compiler.compile_workbook(
        blueprint=blueprint,
        output_path=out,
        dataset_path=dataset,
        schema=schema,
    )
    return result, out


def _get_filters(twb_path, sheet_name):
    """Return list of <filter> elements for a named sheet."""
    tree = etree.parse(twb_path)
    for ws in tree.findall(".//worksheet"):
        if ws.get("name") == sheet_name:
            return ws.findall(".//filter")
    return []


# ---------------------------------------------------------------------------
# 1. Unit: _build_filters_xml helper — returns (col_decls, filter_view_xml)
# ---------------------------------------------------------------------------

class TestBuildFiltersXml:

    def setup_method(self):
        self.compiler = TableauXMLCompiler(TEMPLATE)
        self.ds_id = "federated.abc123"

    def _xml(self, filters):
        """Helper: join both parts of the tuple for simple string checks."""
        col_decls, filter_view = self.compiler._build_filters_xml(
            self.ds_id, filters, _SCHEMA
        )
        return col_decls + filter_view

    def test_no_filters_returns_empty(self):
        col_decls, filter_view = self.compiler._build_filters_xml(
            self.ds_id, [], _SCHEMA
        )
        assert col_decls == ""
        assert filter_view == ""

    def test_none_filters_returns_empty(self):
        col_decls, filter_view = self.compiler._build_filters_xml(
            self.ds_id, None, _SCHEMA
        )
        assert col_decls == ""
        assert filter_view == ""

    def test_single_value_filter_view_contains_filter(self):
        filters = [{"field": "region", "operator": "=", "values": ["USA"]}]
        _, filter_view = self.compiler._build_filters_xml(
            self.ds_id, filters, _SCHEMA
        )
        assert "<filter" in filter_view
        assert "class='categorical'" in filter_view
        # column attr uses fully-qualified CI name
        assert f"[{self.ds_id}].[none:region:nk]" in filter_view
        # member value is quoted
        assert "&quot;USA&quot;" in filter_view

    def test_single_value_uses_member_not_union(self):
        filters = [{"field": "region", "operator": "=", "values": ["USA"]}]
        _, filter_view = self.compiler._build_filters_xml(
            self.ds_id, filters, _SCHEMA
        )
        assert "function='union'" not in filter_view
        assert "function='member'" in filter_view

    def test_multi_value_filter_contains_union(self):
        filters = [{"field": "region", "operator": "=",
                    "values": ["USA", "UK", "Canada"]}]
        _, filter_view = self.compiler._build_filters_xml(
            self.ds_id, filters, _SCHEMA
        )
        assert "function='union'" in filter_view
        assert "&quot;USA&quot;" in filter_view
        assert "&quot;UK&quot;" in filter_view
        assert "&quot;Canada&quot;" in filter_view

    def test_multiple_filter_fields(self):
        filters = [
            {"field": "region", "operator": "=", "values": ["USA"]},
            {"field": "category", "operator": "=", "values": ["Electronics"]},
        ]
        _, filter_view = self.compiler._build_filters_xml(
            self.ds_id, filters, _SCHEMA
        )
        assert filter_view.count("<filter") == 2
        assert "&quot;USA&quot;" in filter_view
        assert "&quot;Electronics&quot;" in filter_view

    def test_col_decls_contain_column_and_ci(self):
        """col_decls must include both <column> and <column-instance> for the filter field."""
        filters = [{"field": "region", "operator": "=", "values": ["USA"]}]
        col_decls, _ = self.compiler._build_filters_xml(
            self.ds_id, filters, _SCHEMA
        )
        assert "<column" in col_decls
        assert "name='[region]'" in col_decls
        assert "<column-instance" in col_decls
        assert "[none:region:nk]" in col_decls

    def test_slices_element_present(self):
        """Each filter must be followed by a <slices> element."""
        filters = [{"field": "region", "operator": "=", "values": ["USA"]}]
        _, filter_view = self.compiler._build_filters_xml(
            self.ds_id, filters, _SCHEMA
        )
        assert "<slices>" in filter_view
        assert f"[{self.ds_id}].[none:region:nk]" in filter_view

    def test_empty_values_skipped(self):
        filters = [{"field": "region", "operator": "=", "values": []}]
        col_decls, filter_view = self.compiler._build_filters_xml(
            self.ds_id, filters, _SCHEMA
        )
        assert col_decls == ""
        assert filter_view == ""

    def test_missing_field_skipped(self):
        filters = [{"operator": "=", "values": ["USA"]}]
        col_decls, filter_view = self.compiler._build_filters_xml(
            self.ds_id, filters, _SCHEMA
        )
        assert col_decls == ""
        assert filter_view == ""


# ---------------------------------------------------------------------------
# 2. Integration: filter elements in generated workbook XML
# ---------------------------------------------------------------------------

class TestFilterInGeneratedWorkbook:

    def test_no_filter_no_filter_element(self):
        blueprint = {"sheets": [{"name": "No Filter",
                                  "column_field": "region", "row_field": "sales",
                                  "mark_type": "Bar"}]}
        result, path = _compile(blueprint)
        try:
            assert result["success"] is True
            filters = _get_filters(path, "No Filter")
            assert len(filters) == 0, "Expected no filter elements"
        finally:
            os.unlink(path)

    def test_single_value_filter_in_xml(self):
        blueprint = {"sheets": [{"name": "USA Only",
                                  "column_field": "category", "row_field": "sales",
                                  "mark_type": "Bar",
                                  "filters": [{"field": "region", "operator": "=",
                                               "values": ["USA"]}]}]}
        result, path = _compile(blueprint)
        try:
            assert result["success"] is True
            filters = _get_filters(path, "USA Only")
            assert len(filters) == 1
            assert filters[0].get("class") == "categorical"
            # column attr uses fully-qualified CI name
            assert "none:region:nk" in filters[0].get("column", "")
            # single value → member function, no union
            gfs = filters[0].findall(".//groupfilter")
            functions = [gf.get("function") for gf in gfs]
            assert "member" in functions
            assert "union" not in functions
        finally:
            os.unlink(path)

    def test_multi_value_filter_in_xml(self):
        blueprint = {"sheets": [{"name": "USA and UK",
                                  "column_field": "category", "row_field": "sales",
                                  "mark_type": "Bar",
                                  "filters": [{"field": "region", "operator": "=",
                                               "values": ["USA", "UK"]}]}]}
        result, path = _compile(blueprint)
        try:
            assert result["success"] is True
            filters = _get_filters(path, "USA and UK")
            assert len(filters) == 1
            gfs = filters[0].findall(".//groupfilter")
            functions = [gf.get("function") for gf in gfs]
            assert "union" in functions
            # member values are XML-entity encoded (&quot;USA&quot;)
            # lxml parses them back to "USA" in the member attribute
            members = [gf.get("member") for gf in gfs if gf.get("member")]
            assert any("USA" in m for m in members)
            assert any("UK" in m for m in members)
        finally:
            os.unlink(path)

    def test_multi_field_filters(self):
        blueprint = {"sheets": [{"name": "Multi Filter",
                                  "column_field": "product", "row_field": "sales",
                                  "mark_type": "Bar",
                                  "filters": [
                                      {"field": "region", "operator": "=",
                                       "values": ["USA"]},
                                      {"field": "category", "operator": "=",
                                       "values": ["Electronics"]},
                                  ]}]}
        result, path = _compile(blueprint)
        try:
            assert result["success"] is True
            filters = _get_filters(path, "Multi Filter")
            assert len(filters) == 2
            # Each filter column should contain the CI name of its field
            columns = {f.get("column") for f in filters}
            assert any("none:region:nk" in c for c in columns)
            assert any("none:category:nk" in c for c in columns)
        finally:
            os.unlink(path)

    def test_filter_is_outside_datasource_dependencies(self):
        """Filter must be a sibling of datasource-dependencies, NOT a child."""
        blueprint = {"sheets": [{"name": "Outside Deps",
                                  "column_field": "category", "row_field": "sales",
                                  "mark_type": "Bar",
                                  "filters": [{"field": "region", "operator": "=",
                                               "values": ["USA"]}]}]}
        result, path = _compile(blueprint)
        try:
            assert result["success"] is True
            tree = etree.parse(path)
            for ws in tree.findall(".//worksheet"):
                if ws.get("name") == "Outside Deps":
                    deps = ws.find(".//datasource-dependencies")
                    # filter must NOT be inside datasource-dependencies
                    assert deps.find(".//filter") is None, \
                        "<filter> must not be inside <datasource-dependencies>"
                    # filter must be a direct child of <view>
                    view = ws.find(".//view")
                    assert view.find("filter") is not None, \
                        "<filter> must be a direct child of <view>"
        finally:
            os.unlink(path)

    def test_slices_element_present_in_xml(self):
        """<slices> must follow each filter in the generated XML."""
        blueprint = {"sheets": [{"name": "Slices Check",
                                  "column_field": "category", "row_field": "sales",
                                  "mark_type": "Bar",
                                  "filters": [{"field": "region", "operator": "=",
                                               "values": ["USA"]}]}]}
        result, path = _compile(blueprint)
        try:
            assert result["success"] is True
            tree = etree.parse(path)
            for ws in tree.findall(".//worksheet"):
                if ws.get("name") == "Slices Check":
                    view = ws.find(".//view")
                    assert view.find("slices") is not None, \
                        "<slices> element must be present"
        finally:
            os.unlink(path)

    def test_filter_and_sort_together(self):
        """Filter + sort on same sheet should both work."""
        blueprint = {"sheets": [{"name": "USA Top Products",
                                  "column_field": "product", "row_field": "sales",
                                  "mark_type": "Bar",
                                  "filters": [{"field": "region", "operator": "=",
                                               "values": ["USA"]}],
                                  "sort": {"field": "sales", "direction": "DESC",
                                           "type": "field"}}]}
        result, path = _compile(blueprint)
        try:
            assert result["success"] is True
            filters = _get_filters(path, "USA Top Products")
            assert len(filters) == 1
            tree = etree.parse(path)
            sorts = tree.findall(".//shelf-sort-v2")
            assert len(sorts) == 1
            assert sorts[0].get("direction") == "DESC"
        finally:
            os.unlink(path)

    def test_filter_with_line_chart(self):
        blueprint = {"sheets": [{"name": "USA Trend",
                                  "column_field": "date", "row_field": "sales",
                                  "mark_type": "Line",
                                  "filters": [{"field": "region", "operator": "=",
                                               "values": ["USA"]}]}]}
        result, path = _compile(blueprint)
        try:
            assert result["success"] is True
            filters = _get_filters(path, "USA Trend")
            assert len(filters) == 1
        finally:
            os.unlink(path)

    def test_filter_does_not_break_unfiltered_sheets(self):
        blueprint = {
            "sheets": [
                {"name": "Filtered", "column_field": "category", "row_field": "sales",
                 "mark_type": "Bar",
                 "filters": [{"field": "region", "operator": "=", "values": ["USA"]}]},
                {"name": "Unfiltered", "column_field": "region", "row_field": "profit",
                 "mark_type": "Bar"},
            ]
        }
        result, path = _compile(blueprint)
        try:
            assert result["success"] is True
            assert result["sheets_created"] == 2
            assert len(_get_filters(path, "Filtered")) == 1
            assert len(_get_filters(path, "Unfiltered")) == 0
        finally:
            os.unlink(path)


# ---------------------------------------------------------------------------
# 3. LLM prompt keyword validation (no API call)
# ---------------------------------------------------------------------------

class TestLLMFilterPromptKeywords:

    def setup_method(self):
        try:
            self.client = LLMClient()
        except ValueError:
            pytest.skip("API key not configured")

    def test_prompt_contains_filter_keywords(self):
        prompt = self.client._build_prompt(_SCHEMA, "show sales for USA only")
        assert "only" in prompt.lower() or "filter" in prompt.lower()

    def test_prompt_contains_filters_schema(self):
        prompt = self.client._build_prompt(_SCHEMA, "show data")
        assert '"filters"' in prompt
        assert '"values"' in prompt
        assert '"field"' in prompt

    def test_prompt_says_omit_filters_when_not_requested(self):
        prompt = self.client._build_prompt(_SCHEMA, "show sales by region")
        assert "Omit" in prompt or "omit" in prompt

    def test_prompt_contains_filter_keywords_section(self):
        prompt = self.client._build_prompt(_SCHEMA, "show sales")
        assert "Filter Selection Rules" in prompt or "filter" in prompt.lower()


# ---------------------------------------------------------------------------
# 4. LLM integration (real API, rate-limited)
# ---------------------------------------------------------------------------

@pytest.mark.requires_api
def test_llm_generates_filter_for_specific_value():
    try:
        client = LLMClient()
    except ValueError:
        pytest.skip("API key not configured")

    blueprint = client.generate_blueprint(
        _SCHEMA, "Show sales by category for USA only"
    )
    sheets = blueprint.get("sheets", [])
    assert len(sheets) > 0

    filters = sheets[0].get("filters")
    assert filters is not None, "Expected filters for 'USA only' request"
    assert len(filters) > 0
    filter_fields = [f.get("field") for f in filters]
    assert any(f in ("region", "category") for f in filter_fields)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
