"""
Tests for XML generation functionality.
"""

import pytest
import sys
import os
import tempfile

# Add src to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from tableau_mcp.core.xml_generator import TableauXMLCompiler


def test_xml_compiler_init():
    """Test XML compiler initialization with template."""
    template_path = "templates/base_template.twb"
    
    if not os.path.exists(template_path):
        pytest.skip("Template file not found - user needs to create it")
    
    compiler = TableauXMLCompiler(template_path)
    assert compiler.template_path == template_path


def test_xml_compiler_init_missing_template():
    """Test error handling for missing template."""
    with pytest.raises(FileNotFoundError):
        TableauXMLCompiler("/path/to/nonexistent/template.twb")


def test_compile_simple_workbook():
    """Test compiling a simple workbook with one sheet."""
    template_path = "templates/base_template.twb"
    
    if not os.path.exists(template_path):
        pytest.skip("Template file not found - user needs to create it")
    
    # Create blueprint
    blueprint = {
        "sheets": [
            {
                "name": "Sales by Category",
                "column_field": "category",
                "row_field": "sales",
                "mark_type": "Bar"
            }
        ]
    }
    
    # Create temporary output file
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.twb') as f:
        output_path = f.name
    
    try:
        compiler = TableauXMLCompiler(template_path)
        result = compiler.compile_workbook(
            blueprint=blueprint,
            output_path=output_path,
            dataset_path="examples/sample_datasets/sales_sample.csv"
        )
        
        # Check result
        assert result["success"] is True
        assert result["sheets_created"] == 1
        assert os.path.exists(output_path)
        
        # Verify output is valid XML
        from lxml import etree
        tree = etree.parse(output_path)
        root = tree.getroot()
        
        # Check for worksheet
        worksheets = root.findall(".//worksheet")
        assert len(worksheets) == 1
        assert worksheets[0].get("name") == "Sales by Category"
        
    finally:
        if os.path.exists(output_path):
            os.unlink(output_path)


def test_compile_multi_sheet_workbook():
    """Test compiling a workbook with multiple sheets."""
    template_path = "templates/base_template.twb"
    
    if not os.path.exists(template_path):
        pytest.skip("Template file not found - user needs to create it")
    
    # Create blueprint with 3 sheets
    blueprint = {
        "sheets": [
            {
                "name": "Sales by Region",
                "column_field": "region",
                "row_field": "sales",
                "mark_type": "Bar"
            },
            {
                "name": "Sales by Category",
                "column_field": "category",
                "row_field": "sales",
                "mark_type": "Bar"
            },
            {
                "name": "Profit Analysis",
                "column_field": "product",
                "row_field": "profit",
                "mark_type": "Bar"
            }
        ]
    }
    
    # Create temporary output file
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.twb') as f:
        output_path = f.name
    
    try:
        compiler = TableauXMLCompiler(template_path)
        result = compiler.compile_workbook(
            blueprint=blueprint,
            output_path=output_path,
            dataset_path="examples/sample_datasets/sales_sample.csv"
        )
        
        # Check result
        assert result["success"] is True
        assert result["sheets_created"] == 3
        
        # Verify output
        from lxml import etree
        tree = etree.parse(output_path)
        root = tree.getroot()
        
        worksheets = root.findall(".//worksheet")
        assert len(worksheets) == 3
        
    finally:
        if os.path.exists(output_path):
            os.unlink(output_path)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
