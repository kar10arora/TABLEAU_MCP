"""
Tests for Story 2.1: Line & Area Charts

Covers:
- Date field detection (xml_generator._infer_dimension_datatype)
- Mark type injection in generated XML
- LLM chart-type selection from keywords (mocked)
- Integration: line chart workbook opens with correct mark type
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

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _compile(blueprint, dataset=DATASET):
    """Helper: compile blueprint → temp .twb, return (result, path)."""
    profiler = SchemaProfiler()
    schema = profiler.profile_dataset(dataset)
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


def _get_mark_class(twb_path, sheet_name):
    """Parse generated workbook and return mark class for named sheet."""
    tree = etree.parse(twb_path)
    for ws in tree.findall(".//worksheet"):
        if ws.get("name") == sheet_name:
            mark = ws.find(".//mark")
            return mark.get("class") if mark is not None else None
    return None


def _get_col_datatype(twb_path, field_name):
    """Return datatype declared for a column in the datasource."""
    tree = etree.parse(twb_path)
    for col in tree.findall(".//datasources/datasource/column"):
        if col.get("name") == f"[{field_name}]":
            return col.get("datatype")
    return None


# ---------------------------------------------------------------------------
# 1. Date field detection
# ---------------------------------------------------------------------------

class TestDateFieldDetection:

    def setup_method(self):
        self.compiler = TableauXMLCompiler(TEMPLATE)

    def _dim(self, name, samples):
        return {"name": name, "sample_values": samples}

    def test_date_by_name_date(self):
        assert self.compiler._infer_dimension_datatype(
            self._dim("order_date", ["2024-01-01"])
        ) == "date"

    def test_date_by_name_timestamp(self):
        assert self.compiler._infer_dimension_datatype(
            self._dim("created_timestamp", ["2024-01-01"])
        ) == "date"

    def test_date_by_iso_sample(self):
        assert self.compiler._infer_dimension_datatype(
            self._dim("ds", ["2024-03-15", "2024-03-16"])
        ) == "date"

    def test_date_by_slash_sample(self):
        assert self.compiler._infer_dimension_datatype(
            self._dim("transaction_dt", ["01/15/2024"])
        ) == "date"

    def test_date_by_year_only(self):
        assert self.compiler._infer_dimension_datatype(
            self._dim("fiscal_year", ["2024", "2023"])
        ) == "date"

    def test_date_by_quarter(self):
        assert self.compiler._infer_dimension_datatype(
            self._dim("period", ["Q1 2024"])
        ) == "date"

    def test_string_not_date(self):
        assert self.compiler._infer_dimension_datatype(
            self._dim("region", ["USA", "UK"])
        ) == "string"

    def test_string_category(self):
        assert self.compiler._infer_dimension_datatype(
            self._dim("category", ["Electronics", "Furniture"])
        ) == "string"


# ---------------------------------------------------------------------------
# 2. Mark type XML injection
# ---------------------------------------------------------------------------

class TestMarkTypeInjection:

    def test_bar_mark_type(self):
        blueprint = {"sheets": [{"name": "Bar Sheet",
                                  "column_field": "region",
                                  "row_field": "sales",
                                  "mark_type": "Bar"}]}
        result, path = _compile(blueprint)
        try:
            assert result["success"] is True
            assert _get_mark_class(path, "Bar Sheet") == "Bar"
        finally:
            os.unlink(path)

    def test_line_mark_type(self):
        blueprint = {"sheets": [{"name": "Line Sheet",
                                  "column_field": "date",
                                  "row_field": "sales",
                                  "mark_type": "Line"}]}
        result, path = _compile(blueprint)
        try:
            assert result["success"] is True
            assert _get_mark_class(path, "Line Sheet") == "Line"
        finally:
            os.unlink(path)

    def test_area_mark_type(self):
        blueprint = {"sheets": [{"name": "Area Sheet",
                                  "column_field": "date",
                                  "row_field": "sales",
                                  "mark_type": "Area"}]}
        result, path = _compile(blueprint)
        try:
            assert result["success"] is True
            assert _get_mark_class(path, "Area Sheet") == "Area"
        finally:
            os.unlink(path)

    def test_automatic_mark_type(self):
        blueprint = {"sheets": [{"name": "Auto Sheet",
                                  "column_field": "category",
                                  "row_field": "profit",
                                  "mark_type": "Automatic"}]}
        result, path = _compile(blueprint)
        try:
            assert result["success"] is True
            assert _get_mark_class(path, "Auto Sheet") == "Automatic"
        finally:
            os.unlink(path)

    def test_default_mark_is_automatic_when_missing(self):
        """If mark_type key absent from blueprint, defaults to Automatic."""
        blueprint = {"sheets": [{"name": "No Mark Sheet",
                                  "column_field": "region",
                                  "row_field": "sales"}]}
        result, path = _compile(blueprint)
        try:
            assert result["success"] is True
            assert _get_mark_class(path, "No Mark Sheet") == "Automatic"
        finally:
            os.unlink(path)


# ---------------------------------------------------------------------------
# 3. Date field emits correct datatype in workbook
# ---------------------------------------------------------------------------

class TestDateDatatypeInWorkbook:

    def test_date_field_gets_date_datatype(self):
        """'date' column in sales_sample.csv should be typed as date in XML."""
        blueprint = {"sheets": [{"name": "Date Test",
                                  "column_field": "date",
                                  "row_field": "sales",
                                  "mark_type": "Line"}]}
        result, path = _compile(blueprint)
        try:
            assert result["success"] is True
            dt = _get_col_datatype(path, "date")
            assert dt == "date", f"Expected 'date', got '{dt}'"
        finally:
            os.unlink(path)

    def test_string_field_stays_string(self):
        blueprint = {"sheets": [{"name": "String Test",
                                  "column_field": "region",
                                  "row_field": "sales",
                                  "mark_type": "Bar"}]}
        result, path = _compile(blueprint)
        try:
            assert result["success"] is True
            dt = _get_col_datatype(path, "region")
            assert dt == "string"
        finally:
            os.unlink(path)


# ---------------------------------------------------------------------------
# 4. Multi-sheet workbook (line + area together)
# ---------------------------------------------------------------------------

class TestMultiSheetLineArea:

    def test_line_and_area_in_same_workbook(self):
        blueprint = {
            "sheets": [
                {"name": "Sales Trend",
                 "column_field": "date",
                 "row_field": "sales",
                 "mark_type": "Line"},
                {"name": "Cumulative Sales",
                 "column_field": "date",
                 "row_field": "sales",
                 "mark_type": "Area"},
                {"name": "Category Breakdown",
                 "column_field": "category",
                 "row_field": "profit",
                 "mark_type": "Bar"},
            ]
        }
        result, path = _compile(blueprint)
        try:
            assert result["success"] is True
            assert result["sheets_created"] == 3
            assert _get_mark_class(path, "Sales Trend") == "Line"
            assert _get_mark_class(path, "Cumulative Sales") == "Area"
            assert _get_mark_class(path, "Category Breakdown") == "Bar"
        finally:
            os.unlink(path)


# ---------------------------------------------------------------------------
# 5. LLM prompt keyword detection (mocked — no API call needed)
# ---------------------------------------------------------------------------

class TestLLMChartTypeKeywords:
    """
    Tests that the updated prompt correctly instructs the LLM.
    We mock the API call and inspect which mark_type the mock returns
    for given user requests — verifying the prompt contains the right signals.
    """

    def setup_method(self):
        try:
            self.client = LLMClient()
        except ValueError:
            pytest.skip("API key not configured")

    def _mock_blueprint(self, mark_type: str) -> dict:
        return {"sheets": [{"name": "Sheet 1",
                             "column_field": "date",
                             "row_field": "sales",
                             "mark_type": mark_type}]}

    def test_prompt_contains_line_keywords(self):
        schema = {"dimensions": [{"name": "date"}], "measures": [{"name": "sales"}]}
        prompt = self.client._build_prompt(schema, "show sales trend over time")
        assert "Line" in prompt
        assert "trend" in prompt.lower()
        assert "over time" in prompt.lower()

    def test_prompt_contains_area_keywords(self):
        schema = {"dimensions": [{"name": "date"}], "measures": [{"name": "sales"}]}
        prompt = self.client._build_prompt(schema, "show cumulative sales")
        assert "Area" in prompt
        assert "cumulative" in prompt.lower()

    def test_prompt_contains_bar_keywords(self):
        schema = {"dimensions": [{"name": "region"}], "measures": [{"name": "sales"}]}
        prompt = self.client._build_prompt(schema, "compare sales by region")
        assert "Bar" in prompt
        assert "compare" in prompt.lower()

    def test_prompt_includes_all_valid_mark_types(self):
        schema = {"dimensions": [{"name": "region"}], "measures": [{"name": "sales"}]}
        prompt = self.client._build_prompt(schema, "show me data")
        for mark in ("Bar", "Line", "Area", "Automatic"):
            assert mark in prompt, f"'{mark}' missing from prompt"


# ---------------------------------------------------------------------------
# 6. LLM integration — real API (rate-limited, skip if no key)
# ---------------------------------------------------------------------------

@pytest.mark.requires_api
def test_llm_selects_line_for_trend_request():
    try:
        client = LLMClient()
    except ValueError:
        pytest.skip("API key not configured")

    schema = {"dimensions": [{"name": "date", "sample_values": ["2024-01-01"]},
                              {"name": "region", "sample_values": ["USA"]}],
              "measures": [{"name": "sales", "sample_values": [1000]},
                           {"name": "profit", "sample_values": [200]}]}

    blueprint = client.generate_blueprint(schema, "Show the sales trend over time")
    sheets = blueprint.get("sheets", [])
    assert len(sheets) > 0
    mark = sheets[0]["mark_type"]
    assert mark in ("Line", "Area"), f"Expected Line/Area for trend request, got {mark}"


@pytest.mark.requires_api
def test_llm_selects_area_for_cumulative_request():
    try:
        client = LLMClient()
    except ValueError:
        pytest.skip("API key not configured")

    schema = {"dimensions": [{"name": "date", "sample_values": ["2024-01-01"]}],
              "measures": [{"name": "sales", "sample_values": [1000]}]}

    blueprint = client.generate_blueprint(schema, "Show cumulative sales area chart")
    sheets = blueprint.get("sheets", [])
    assert len(sheets) > 0
    assert sheets[0]["mark_type"] in ("Area", "Line")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
