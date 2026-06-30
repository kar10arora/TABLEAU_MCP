"""
Tests for MCP server integration (Story 1.6).
Requires API key to run.
"""

import pytest
import sys
import os
import json

# Add src to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from tableau_mcp.mcp.server import inspect_dataset_schema, generate_tableau_workbook


@pytest.mark.requires_api
def test_inspect_dataset_schema_tool():
    """Test inspect_dataset_schema MCP tool."""
    result = inspect_dataset_schema("examples/sample_datasets/sales_sample.csv")
    schema = json.loads(result)
    
    assert "error" not in schema
    assert "dimensions" in schema
    assert "measures" in schema
    assert len(schema["dimensions"]) > 0
    assert len(schema["measures"]) > 0


@pytest.mark.requires_api
def test_inspect_dataset_schema_missing_file():
    """Test error handling for missing file."""
    result = inspect_dataset_schema("/nonexistent/file.csv")
    response = json.loads(result)
    
    assert "error" in response


@pytest.mark.requires_api
def test_generate_tableau_workbook_simple():
    """Test generating a simple workbook."""
    import tempfile
    
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.twb') as f:
        output_path = f.name
    
    try:
        result = generate_tableau_workbook(
            dataset_path="examples/sample_datasets/sales_sample.csv",
            user_request="Create a bar chart of sales by region",
            output_path=output_path
        )
        
        response = json.loads(result)
        
        assert response["success"] is True
        assert "workbook_path" in response
        assert "sheets_created" in response
        assert response["sheets_created"] > 0
        assert os.path.exists(output_path)
        
        # Verify it's valid XML
        from lxml import etree
        tree = etree.parse(output_path)
        assert tree is not None
        
    finally:
        if os.path.exists(output_path):
            os.unlink(output_path)


@pytest.mark.requires_api
def test_generate_tableau_workbook_with_default_output():
    """Test workbook generation with default output path."""
    result = generate_tableau_workbook(
        dataset_path="examples/sample_datasets/sales_sample.csv",
        user_request="Show profit by category"
    )
    
    response = json.loads(result)
    
    assert response["success"] is True
    assert "workbook_path" in response
    assert os.path.exists(response["workbook_path"])


@pytest.mark.requires_api
def test_generate_tableau_workbook_error_handling():
    """Test error handling for invalid dataset."""
    result = generate_tableau_workbook(
        dataset_path="/nonexistent/dataset.csv",
        user_request="Create a chart"
    )
    
    response = json.loads(result)
    
    assert response["success"] is False
    assert "error" in response


@pytest.mark.requires_api  
def test_end_to_end_pipeline():
    """Test complete pipeline from request to workbook."""
    import tempfile
    
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.twb') as f:
        output_path = f.name
    
    try:
        # Step 1: Inspect schema
        schema_result = inspect_dataset_schema("examples/sample_datasets/sales_sample.csv")
        schema = json.loads(schema_result)
        assert "dimensions" in schema
        
        # Step 2: Generate workbook
        workbook_result = generate_tableau_workbook(
            dataset_path="examples/sample_datasets/sales_sample.csv",
            user_request="Create a visualization showing sales trends",
            output_path=output_path
        )
        
        result = json.loads(workbook_result)
        assert result["success"] is True
        
        # Step 3: Verify output
        assert os.path.exists(output_path)
        file_size = os.path.getsize(output_path)
        assert file_size > 1000  # Should be a reasonable size
        
        # Step 4: Validate XML
        from lxml import etree
        tree = etree.parse(output_path)
        worksheets = tree.findall(".//worksheet")
        assert len(worksheets) > 0
        
    finally:
        if os.path.exists(output_path):
            os.unlink(output_path)


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-m", "requires_api"])
