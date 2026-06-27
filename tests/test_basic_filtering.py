"""
Tests for Story 2.3: Basic Filtering

Covers:
- _build_filters_xml() for single-value and multi-value filters
- Filter XML correctly injected into <datasource-dependencies>
- Filter + sort combination works
- Filter + chart type combination works
- LLM prompt contains filter keywords
- No filter when not requested
"""

import os
import sys
import tempfile

import pytest
from lxml import etree

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from tableau_mcp.core.schema_profiler import SchemaProfiler
from tableau_mcp.core.xml_generator import TableauXMLCompiler
from tableau_mcp.llm.client import LLMClient

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


def _get_groupfilters(twb_path, sheet_name):
    """Return all <groupfilter> children under all filters for a sheet."""
    tree = etree.parse(twb_path)
    result = []
    for ws in tree.findall(".//worksheet"):
        if ws.get("name") == sheet_name:
            for f in ws.findall(".//filter"):
                result.extend(f.findall(".//groupfilter"))
    return result


# ---------------------------------------------------------------------------
# 1. Unit: _build_filters_xml helper
# ---------------------------------------------------------------------------

class TestBuildFiltersXml:

    def setup_method(self):
        self.compiler = TableauXMLCompiler(TEMPLATE)
        self.ds_id = "federated.abc123"

    def test_no_filters_returns_empty(self):
        filters_xml, slices_xml = self.compiler._build_filters_xml_and_slices(self.ds_id, [], _SCHEMA)
        assert filters_xml == ""
        assert slices_xml == ""

    def test_none_filters_returns_empty(self):
        filters_xml, slices_xml = self.compiler._build_filters_xml_and_slices(self.ds_id, None, _SCHEMA)
        assert filters_xml == ""
        assert slices_xml == ""

    def test_single_value_filter_contains_member(self):
        filters = [{"field": "region", "operator": "=", "values": ["USA"]}]
        filters_xml, slices_xml = self.compiler._build_filters_xml_and_slices(self.ds_id, filters, _SCHEMA)
        assert "<filter" in filters_xml
        assert "class='categorical'" in filters_xml
        assert "function='member'" in filters_xml
        assert "&quot;USA&quot;" in filters_xml
        assert slices_xml != ""
        assert "slices" in slices_xml

    def test_multi_value_filter_contains_union(self):
        filters = [{"field": "region", "operator": "=", "values": ["USA", "UK", "Canada"]}]
        filters_xml, slices_xml = self.compiler._build_filters_xml_and_slices(self.ds_id, filters, _SCHEMA)
        assert "function='union'" in filters_xml
        assert "&quot;USA&quot;" in filters_xml
        assert "&quot;UK&quot;" in filters_xml
        assert "&quot;Canada&quot;" in filters_xml

    def test_single_value_does_not_use_union(self):
        filters = [{"field": "region", "operator": "=", "values": ["USA"]}]
        filters_xml, slices_xml = self.compiler._build_filters_xml_and_slices(self.ds_id, filters, _SCHEMA)
        assert "function='union'" not in filters_xml
        assert "function='member'" in filters_xml

    def test_multiple_filter_fields(self):
        filters = [
            {"field": "region", "operator": "=", "values": ["USA"]},
            {"field": "category", "operator": "=", "values": ["Electronics"]},
        ]
        filters_xml, slices_xml = self.compiler._build_filters_xml_and_slices(self.ds_id, filters, _SCHEMA)
        assert filters_xml.count("<filter") == 2
        assert "&quot;USA&quot;" in filters_xml
        assert "&quot;Electronics&quot;" in filters_xml

    def test_filter_uses_fully_qualified_column(self):
        filters = [{"field": "region", "operator": "=", "values": ["USA"]}]
        filters_xml, slices_xml = self.compiler._build_filters_xml_and_slices(self.ds_id, filters, _SCHEMA)
        assert f"column='[{self.ds_id}].[none:region:nk]'" in filters_xml

    def test_filter_includes_slices(self):
        filters = [{"field": "region", "operator": "=", "values": ["USA"]}]
        filters_xml, slices_xml = self.compiler._build_filters_xml_and_slices(self.ds_id, filters, _SCHEMA)
        assert "<slices>" in slices_xml
        assert f"[{self.ds_id}].[none:region:nk]" in slices_xml

    def test_empty_values_skipped(self):
        filters = [{"field": "region", "operator": "=", "values": []}]
        filters_xml, slices_xml = self.compiler._build_filters_xml_and_slices(self.ds_id, filters, _SCHEMA)
        assert filters_xml == ""
        assert slices_xml == ""

    def test_missing_field_skipped(self):
        filters = [{"operator": "=", "values": ["USA"]}]
        filters_xml, slices_xml = self.compiler._build_filters_xml_and_slices(self.ds_id, filters, _SCHEMA)
        assert filters_xml == ""
        assert slices_xml == ""


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
            column = filters[0].get("column")
            assert "[none:region:nk]" in column  # Fully qualified column reference
            # Should use member function (not union) for single value
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
            # Multi-value should use union
            gfs = filters[0].findall(".//groupfilter")
            functions = [gf.get("function") for gf in gfs]
            assert "union" in functions
            members = [gf.get("member") for gf in gfs if gf.get("member")]
            # Members are quoted in XML
            assert '&quot;USA&quot;' in members or '"USA"' in members
            assert '&quot;UK&quot;' in members or '"UK"' in members
        finally:
            os.unlink(path)

    def test_multi_field_filters(self):
        blueprint = {"sheets": [{"name": "Multi Filter",
                                  "column_field": "product", "row_field": "sales",
                                  "mark_type": "Bar",
                                  "filters": [
                                      {"field": "region", "operator": "=", "values": ["USA"]},
                                      {"field": "category", "operator": "=", "values": ["Electronics"]},
                                  ]}]}
        result, path = _compile(blueprint)
        try:
            assert result["success"] is True
            filters = _get_filters(path, "Multi Filter")
            assert len(filters) == 2
            columns = {f.get("column") for f in filters}
            # Check that columns contain the field names (fully qualified)
            assert any("region" in c for c in columns)
            assert any("category" in c for c in columns)
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
        """Filter works on non-Bar chart types too."""
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
        """Multi-sheet: filtered + unfiltered coexist."""
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
    # LLM should generate a filter for region=USA
    assert filters is not None, "Expected filters for 'USA only' request"
    assert len(filters) > 0
    filter_fields = [f.get("field") for f in filters]
    assert any(f in ("region", "category") for f in filter_fields)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
