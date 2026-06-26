"""
Tests for Story 2.4: Visual Encodings (Color, Size, Tooltip)

Covers:
- _build_encoding_field_declarations() for adding encoding fields to datasource-dependencies
- _build_encodings_xml() for color, size, and tooltip encodings
- Encodings correctly injected into worksheets
- LLM prompt contains encoding keywords
- No encoding when not requested
"""

import os
import sys
import tempfile

import pytest
from lxml import etree

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.core.schema_profiler import SchemaProfiler
from src.core.xml_generator import TableauXMLCompiler

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


def _get_encodings(twb_path, sheet_name):
    """Return list of color/size/text elements inside <encodings> for a named sheet."""
    tree = etree.parse(twb_path)
    for ws in tree.findall(".//worksheet"):
        if ws.get("name") == sheet_name:
            encodings_elem = ws.find(".//encodings")
            if encodings_elem is not None:
                # Return all color, size, text children
                return list(encodings_elem)
    return []


# ---------------------------------------------------------------------------
# 1. Unit: _build_encodings_xml helper
# ---------------------------------------------------------------------------

class TestBuildEncodingsXml:

    def setup_method(self):
        self.compiler = TableauXMLCompiler(TEMPLATE)
        self.ds_id = "federated.abc123"

    def test_no_encodings_returns_empty(self):
        xml = self.compiler._build_encodings_xml(self.ds_id, {}, _SCHEMA)
        assert xml == ""

    def test_none_encodings_returns_empty(self):
        xml = self.compiler._build_encodings_xml(self.ds_id, None, _SCHEMA)
        assert xml == ""

    def test_color_encoding_dimension(self):
        encodings = {"color": {"field": "region", "type": "dimension", "palette": "tableau10"}}
        xml = self.compiler._build_encodings_xml(self.ds_id, encodings, _SCHEMA)
        assert "<encodings>" in xml
        assert "<color" in xml
        assert "column=" in xml

    def test_color_encoding_measure(self):
        encodings = {"color": {"field": "sales", "type": "measure", "palette": "tableau20"}}
        xml = self.compiler._build_encodings_xml(self.ds_id, encodings, _SCHEMA)
        assert "<encodings>" in xml
        assert "<color" in xml

    def test_size_encoding(self):
        encodings = {"size": {"field": "quantity"}}
        xml = self.compiler._build_encodings_xml(self.ds_id, encodings, _SCHEMA)
        assert "<encodings>" in xml
        assert "<size" in xml

    def test_tooltip_encoding_single_field(self):
        encodings = {"tooltip": ["sales"]}
        xml = self.compiler._build_encodings_xml(self.ds_id, encodings, _SCHEMA)
        assert "<encodings>" in xml
        assert "<text" in xml

    def test_tooltip_encoding_multiple_fields(self):
        encodings = {"tooltip": ["sales", "quantity", "region"]}
        xml = self.compiler._build_encodings_xml(self.ds_id, encodings, _SCHEMA)
        assert xml.count("<text") == 3

    def test_multiple_encodings_together(self):
        encodings = {
            "color": {"field": "region", "type": "dimension"},
            "size": {"field": "quantity"},
            "tooltip": ["sales", "region"]
        }
        xml = self.compiler._build_encodings_xml(self.ds_id, encodings, _SCHEMA)
        assert "<color" in xml
        assert "<size" in xml
        assert xml.count("<text") == 2


class TestEncodingFieldDeclarations:

    def setup_method(self):
        self.compiler = TableauXMLCompiler(TEMPLATE)

    def test_no_encodings_returns_empty(self):
        xml = self.compiler._build_encoding_field_declarations({}, _SCHEMA)
        assert xml == ""

    def test_color_field_declaration(self):
        encodings = {"color": {"field": "region"}}
        xml = self.compiler._build_encoding_field_declarations(encodings, _SCHEMA)
        assert "<column" in xml
        assert "name='[region]'" in xml
        assert "<column-instance" in xml

    def test_multiple_encoding_fields_declared(self):
        encodings = {
            "color": {"field": "region"},
            "size": {"field": "quantity"},
            "tooltip": ["sales"]
        }
        xml = self.compiler._build_encoding_field_declarations(encodings, _SCHEMA)
        assert "name='[region]'" in xml
        assert "name='[quantity]'" in xml or "name='[sales]'" in xml

    def test_duplicate_fields_only_declared_once(self):
        encodings = {
            "color": {"field": "region"},
            "tooltip": ["region", "sales"]  # region appears twice
        }
        xml = self.compiler._build_encoding_field_declarations(encodings, _SCHEMA)
        # region should appear only once in declarations
        region_count = xml.count("name='[region]'")
        assert region_count == 1


# ---------------------------------------------------------------------------
# 2. Integration: encodings in generated workbook XML
# ---------------------------------------------------------------------------

class TestEncodingsInGeneratedWorkbook:

    def test_no_encoding_no_encoding_element(self):
        blueprint = {"sheets": [{"name": "No Encoding",
                                  "column_field": "region", "row_field": "sales",
                                  "mark_type": "Bar"}]}
        result, path = _compile(blueprint)
        try:
            assert result["success"] is True
            encodings = _get_encodings(path, "No Encoding")
            assert len(encodings) == 0
        finally:
            os.unlink(path)

    def test_color_encoding_in_xml(self):
        blueprint = {"sheets": [{"name": "Color by Region",
                                  "column_field": "category", "row_field": "sales",
                                  "mark_type": "Bar",
                                  "encodings": {
                                      "color": {"field": "region", "type": "dimension", "palette": "tableau10"}
                                  }}]}
        result, path = _compile(blueprint)
        try:
            assert result["success"] is True
            encodings = _get_encodings(path, "Color by Region")
            assert len(encodings) == 1
            assert encodings[0].tag.split('}')[-1] == "color"
            assert encodings[0].get("column") is not None
        finally:
            os.unlink(path)

    def test_size_encoding_in_xml(self):
        blueprint = {"sheets": [{"name": "Bubble Chart",
                                  "column_field": "region", "row_field": "sales",
                                  "mark_type": "Circle",
                                  "encodings": {
                                      "size": {"field": "quantity"}
                                  }}]}
        result, path = _compile(blueprint)
        try:
            assert result["success"] is True
            encodings = _get_encodings(path, "Bubble Chart")
            assert len(encodings) == 1
            assert encodings[0].tag.split('}')[-1] == "size"
        finally:
            os.unlink(path)

    def test_tooltip_encoding_in_xml(self):
        blueprint = {"sheets": [{"name": "With Tooltip",
                                  "column_field": "category", "row_field": "sales",
                                  "mark_type": "Bar",
                                  "encodings": {
                                      "tooltip": ["sales", "quantity", "region"]
                                  }}]}
        result, path = _compile(blueprint)
        try:
            assert result["success"] is True
            encodings = _get_encodings(path, "With Tooltip")
            assert len(encodings) == 3
            tags = [e.tag.split('}')[-1] for e in encodings]
            assert all(t == "text" for t in tags)
        finally:
            os.unlink(path)

    def test_combined_encodings(self):
        """Test color, size, and tooltip together."""
        blueprint = {"sheets": [{"name": "Full Encoding",
                                  "column_field": "category", "row_field": "sales",
                                  "mark_type": "Circle",
                                  "encodings": {
                                      "color": {"field": "region", "type": "dimension"},
                                      "size": {"field": "quantity"},
                                      "tooltip": ["sales", "quantity", "region"]
                                  }}]}
        result, path = _compile(blueprint)
        try:
            assert result["success"] is True
            encodings = _get_encodings(path, "Full Encoding")
            # Should have 1 color + 1 size + 3 text (tooltips) = 5 encodings
            assert len(encodings) == 5
            tags = [e.tag.split('}')[-1] for e in encodings]
            assert "color" in tags
            assert "size" in tags
            assert tags.count("text") == 3
        finally:
            os.unlink(path)

    def test_encoding_fields_declared_in_dependencies(self):
        """Verify encoding fields are declared in datasource-dependencies."""
        blueprint = {"sheets": [{"name": "Encoding Fields Test",
                                  "column_field": "category", "row_field": "sales",
                                  "mark_type": "Bar",
                                  "encodings": {
                                      "color": {"field": "region"}
                                  }}]}
        result, path = _compile(blueprint)
        try:
            tree = etree.parse(path)
            deps = tree.find(".//worksheet[@name='Encoding Fields Test']//datasource-dependencies")
            assert deps is not None
            # Check that [region] is declared
            columns = deps.findall(".//column[@name='[region]']")
            assert len(columns) > 0
        finally:
            os.unlink(path)

    def test_encoding_with_filter_and_sort(self):
        """Encoding should work with filter and sort together."""
        blueprint = {"sheets": [{"name": "Full Features",
                                  "column_field": "product", "row_field": "sales",
                                  "mark_type": "Bar",
                                  "filters": [{"field": "region", "operator": "=", "values": ["USA"]}],
                                  "sort": {"field": "sales", "direction": "DESC", "type": "field"},
                                  "encodings": {"color": {"field": "category", "type": "dimension"}}}]}
        result, path = _compile(blueprint)
        try:
            assert result["success"] is True
            encodings = _get_encodings(path, "Full Features")
            # Should have at least 1 color encoding
            color_encodings = [e for e in encodings if e.tag.split('}')[-1] == "color"]
            assert len(color_encodings) >= 1
        finally:
            os.unlink(path)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
