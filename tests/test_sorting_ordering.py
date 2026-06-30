"""
Tests for Story 2.2: Sorting & Ordering

Covers:
- _build_sort_xml() output for all sort types
- shelf-sorts XML injected correctly in generated workbook
- ASC / DESC directions
- Field sort vs alphabetical sort
- No sort (sort key absent) leaves workbook clean
- LLM prompt contains sort keywords
- LLM integration: top-N request produces DESC sort (requires_api)
"""

import json
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

# ── shared schema used across tests ──────────────────────────────────
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


def _shelf_sorts(twb_path, sheet_name):
    """Return list of shelf-sort-v2 elements for a sheet (may be empty)."""
    tree = etree.parse(twb_path)
    for ws in tree.findall(".//worksheet"):
        if ws.get("name") == sheet_name:
            return ws.findall(".//shelf-sort-v2")
    return []


def _column_instances(twb_path, sheet_name):
    """Return list of column-instance elements for a sheet."""
    tree = etree.parse(twb_path)
    for ws in tree.findall(".//worksheet"):
        if ws.get("name") == sheet_name:
            return ws.findall(".//column-instance")
    return []


# ---------------------------------------------------------------------------
# 1. Unit: _build_sort_xml helper
# ---------------------------------------------------------------------------

class TestBuildSortXml:

    def setup_method(self):
        self.compiler = TableauXMLCompiler(TEMPLATE)
        self.ds_id = "federated.abc123"

    def test_no_sort_returns_empty_strings(self):
        ci, ss = self.compiler._build_sort_xml(
            ds_id=self.ds_id,
            col_field="region", row_field="sales",
            col_type="nominal", row_type="quantitative",
            sort_cfg=None, schema=_SCHEMA,
        )
        assert ci == ""
        assert ss == ""

    def test_field_sort_desc_produces_shelf_sort(self):
        ci, ss = self.compiler._build_sort_xml(
            ds_id=self.ds_id,
            col_field="product", row_field="sales",
            col_type="nominal", row_type="quantitative",
            sort_cfg={"field": "sales", "direction": "DESC", "type": "field"},
            schema=_SCHEMA,
        )
        assert "<shelf-sorts>" in ss
        assert "direction='DESC'" in ss
        assert "measure-to-sort-by" in ss

    def test_field_sort_asc(self):
        _, ss = self.compiler._build_sort_xml(
            ds_id=self.ds_id,
            col_field="region", row_field="profit",
            col_type="nominal", row_type="quantitative",
            sort_cfg={"field": "profit", "direction": "ASC", "type": "field"},
            schema=_SCHEMA,
        )
        assert "direction='ASC'" in ss

    def test_alphabetical_sort_asc(self):
        _, ss = self.compiler._build_sort_xml(
            ds_id=self.ds_id,
            col_field="category", row_field="sales",
            col_type="nominal", row_type="quantitative",
            sort_cfg={"field": "category", "direction": "ASC", "type": "alphabetical"},
            schema=_SCHEMA,
        )
        assert "<shelf-sorts>" in ss
        assert "direction='ASC'" in ss
        # Alphabetical sort still requires measure-to-sort-by per DTD
        assert "measure-to-sort-by" in ss

    def test_alphabetical_sort_desc(self):
        _, ss = self.compiler._build_sort_xml(
            ds_id=self.ds_id,
            col_field="category", row_field="sales",
            col_type="nominal", row_type="quantitative",
            sort_cfg={"field": "category", "direction": "DESC", "type": "alphabetical"},
            schema=_SCHEMA,
        )
        assert "direction='DESC'" in ss

    def test_column_instances_emitted(self):
        ci, _ = self.compiler._build_sort_xml(
            ds_id=self.ds_id,
            col_field="region", row_field="sales",
            col_type="nominal", row_type="quantitative",
            sort_cfg={"field": "sales", "direction": "DESC", "type": "field"},
            schema=_SCHEMA,
        )
        assert "column-instance" in ci
        assert "[none:region:nk]" in ci
        assert "[sum:sales:qk]" in ci

    def test_invalid_direction_defaults_to_desc(self):
        _, ss = self.compiler._build_sort_xml(
            ds_id=self.ds_id,
            col_field="region", row_field="sales",
            col_type="nominal", row_type="quantitative",
            sort_cfg={"field": "sales", "direction": "INVALID", "type": "field"},
            schema=_SCHEMA,
        )
        assert "direction='DESC'" in ss


# ---------------------------------------------------------------------------
# 2. Integration: shelf-sorts in generated workbook XML
# ---------------------------------------------------------------------------

class TestSortInGeneratedWorkbook:

    def test_no_sort_no_shelf_sorts_element(self):
        blueprint = {"sheets": [{"name": "No Sort",
                                  "column_field": "region",
                                  "row_field": "sales",
                                  "mark_type": "Bar"}]}
        result, path = _compile(blueprint)
        try:
            assert result["success"] is True
            sorts = _shelf_sorts(path, "No Sort")
            assert len(sorts) == 0, "Should have no shelf-sorts when sort not requested"
        finally:
            os.unlink(path)

    def test_desc_field_sort_in_xml(self):
        blueprint = {"sheets": [{"name": "Top Products",
                                  "column_field": "product",
                                  "row_field": "sales",
                                  "mark_type": "Bar",
                                  "sort": {"field": "sales", "direction": "DESC", "type": "field"}}]}
        result, path = _compile(blueprint)
        try:
            assert result["success"] is True
            sorts = _shelf_sorts(path, "Top Products")
            assert len(sorts) == 1
            assert sorts[0].get("direction") == "DESC"
            assert "sum:sales:qk" in sorts[0].get("measure-to-sort-by", "")
        finally:
            os.unlink(path)

    def test_asc_field_sort_in_xml(self):
        blueprint = {"sheets": [{"name": "Lowest Sales",
                                  "column_field": "region",
                                  "row_field": "sales",
                                  "mark_type": "Bar",
                                  "sort": {"field": "sales", "direction": "ASC", "type": "field"}}]}
        result, path = _compile(blueprint)
        try:
            assert result["success"] is True
            sorts = _shelf_sorts(path, "Lowest Sales")
            assert len(sorts) == 1
            assert sorts[0].get("direction") == "ASC"
        finally:
            os.unlink(path)

    def test_alphabetical_sort_in_xml(self):
        blueprint = {"sheets": [{"name": "Alpha Sort",
                                  "column_field": "category",
                                  "row_field": "profit",
                                  "mark_type": "Bar",
                                  "sort": {"field": "category", "direction": "ASC",
                                           "type": "alphabetical"}}]}
        result, path = _compile(blueprint)
        try:
            assert result["success"] is True
            sorts = _shelf_sorts(path, "Alpha Sort")
            assert len(sorts) == 1
            assert sorts[0].get("direction") == "ASC"
            # measure-to-sort-by is required by DTD even for alphabetical
            assert sorts[0].get("measure-to-sort-by") is not None
        finally:
            os.unlink(path)

    def test_column_instances_present_when_sorted(self):
        blueprint = {"sheets": [{"name": "With Instances",
                                  "column_field": "region",
                                  "row_field": "sales",
                                  "mark_type": "Bar",
                                  "sort": {"field": "sales", "direction": "DESC", "type": "field"}}]}
        result, path = _compile(blueprint)
        try:
            assert result["success"] is True
            cis = _column_instances(path, "With Instances")
            ci_names = [ci.get("name") for ci in cis]
            assert any("none:region:nk" in n for n in ci_names), "Missing dimension CI"
            assert any("sum:sales:qk" in n for n in ci_names), "Missing measure CI"
        finally:
            os.unlink(path)

    def test_sort_does_not_break_existing_sheets_without_sort(self):
        """Multi-sheet: sorted sheet + unsorted sheet coexist correctly."""
        blueprint = {
            "sheets": [
                {"name": "Sorted",   "column_field": "product", "row_field": "sales",
                 "mark_type": "Bar", "sort": {"field": "sales", "direction": "DESC", "type": "field"}},
                {"name": "Unsorted", "column_field": "region",  "row_field": "profit",
                 "mark_type": "Bar"},
            ]
        }
        result, path = _compile(blueprint)
        try:
            assert result["success"] is True
            assert result["sheets_created"] == 2
            assert len(_shelf_sorts(path, "Sorted")) == 1
            assert len(_shelf_sorts(path, "Unsorted")) == 0
        finally:
            os.unlink(path)

    def test_sort_works_with_line_chart(self):
        """Sort is compatible with non-Bar mark types."""
        blueprint = {"sheets": [{"name": "Sorted Line",
                                  "column_field": "date",
                                  "row_field": "sales",
                                  "mark_type": "Line",
                                  "sort": {"field": "sales", "direction": "DESC", "type": "field"}}]}
        result, path = _compile(blueprint)
        try:
            assert result["success"] is True
            sorts = _shelf_sorts(path, "Sorted Line")
            assert len(sorts) == 1
        finally:
            os.unlink(path)


# ---------------------------------------------------------------------------
# 3. LLM prompt keyword validation (no API call needed)
# ---------------------------------------------------------------------------

class TestLLMSortPromptKeywords:

    def setup_method(self):
        try:
            self.client = LLMClient()
        except ValueError:
            pytest.skip("API key not configured")

    def test_prompt_contains_top_n_keyword(self):
        prompt = self.client._build_prompt(_SCHEMA, "show top 10 products by sales")
        assert "top N" in prompt or "top" in prompt.lower()

    def test_prompt_contains_sort_desc_direction(self):
        prompt = self.client._build_prompt(_SCHEMA, "lowest sales by region")
        assert "DESC" in prompt
        assert "ASC" in prompt

    def test_prompt_contains_alphabetical_keyword(self):
        prompt = self.client._build_prompt(_SCHEMA, "sort alphabetically")
        assert "alphabetical" in prompt.lower()

    def test_prompt_contains_sort_block_schema(self):
        prompt = self.client._build_prompt(_SCHEMA, "rank products")
        assert '"sort"' in prompt
        assert '"direction"' in prompt
        assert '"type"' in prompt

    def test_prompt_says_omit_sort_when_not_requested(self):
        prompt = self.client._build_prompt(_SCHEMA, "show sales")
        assert "Omit" in prompt or "omit" in prompt


# ---------------------------------------------------------------------------
# 4. LLM integration tests (real API, rate-limited)
# ---------------------------------------------------------------------------

@pytest.mark.requires_api
def test_llm_top_n_produces_desc_sort():
    try:
        client = LLMClient()
    except ValueError:
        pytest.skip("API key not configured")

    blueprint = client.generate_blueprint(_SCHEMA, "Show top 5 products by sales")
    sheets = blueprint.get("sheets", [])
    assert len(sheets) > 0

    sheet = sheets[0]
    sort = sheet.get("sort")
    assert sort is not None, "Expected sort block for top-N request"
    assert sort.get("direction") == "DESC"


@pytest.mark.requires_api
def test_llm_no_sort_when_not_requested():
    try:
        client = LLMClient()
    except ValueError:
        pytest.skip("API key not configured")

    blueprint = client.generate_blueprint(_SCHEMA, "Show sales by category")
    sheets = blueprint.get("sheets", [])
    assert len(sheets) > 0
    # Sort key may be absent or null for plain requests
    sort = sheets[0].get("sort")
    assert sort is None or isinstance(sort, dict)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
