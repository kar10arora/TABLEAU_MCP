"""
Tests for LLM integration (Story 1.5).
Requires API key to run.
"""

import pytest
import sys
import os

# Add src to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.llm.client import LLMClient
from src.core.schema_profiler import SchemaProfiler


@pytest.mark.requires_api
def test_llm_client_initialization():
    """Test LLM client initializes with API key."""
    try:
        client = LLMClient()
        assert client.provider in ['gemini', 'openrouter']
        assert client.api_key is not None
    except ValueError as e:
        pytest.skip(f"API key not configured: {str(e)}")


@pytest.mark.requires_api
def test_blueprint_generation_simple():
    """Test generating a simple blueprint."""
    try:
        # Create sample schema
        schema = {
            "dimensions": [
                {"name": "region", "type": "nominal"},
                {"name": "category", "type": "nominal"}
            ],
            "measures": [
                {"name": "sales", "type": "quantitative"}
            ]
        }
        
        client = LLMClient()
        blueprint = client.generate_blueprint(schema, "Create a bar chart of sales by region")
        
        # Validate structure
        assert "sheets" in blueprint
        assert len(blueprint["sheets"]) > 0
        
        sheet = blueprint["sheets"][0]
        assert "name" in sheet
        assert "column_field" in sheet
        assert "row_field" in sheet
        assert "mark_type" in sheet
        
    except ValueError as e:
        pytest.skip(f"API key not configured: {str(e)}")


@pytest.mark.requires_api
def test_blueprint_field_validation():
    """Test that blueprint only uses valid field names."""
    try:
        profiler = SchemaProfiler()
        schema = profiler.profile_dataset("examples/sample_datasets/sales_sample.csv")
        
        client = LLMClient()
        blueprint = client.generate_blueprint(schema, "Show sales by category")
        
        all_fields = [d["name"] for d in schema["dimensions"]] + \
                    [m["name"] for m in schema["measures"]]
        
        for sheet in blueprint["sheets"]:
            assert sheet["column_field"] in all_fields, \
                f"Invalid column field: {sheet['column_field']}"
            assert sheet["row_field"] in all_fields, \
                f"Invalid row field: {sheet['row_field']}"
                
    except ValueError as e:
        pytest.skip(f"API key not configured: {str(e)}")


@pytest.mark.requires_api
def test_blueprint_mark_types():
    """Test that blueprint uses valid mark types."""
    try:
        schema = {
            "dimensions": [{"name": "date", "type": "nominal"}],
            "measures": [{"name": "sales", "type": "quantitative"}]
        }
        
        client = LLMClient()
        blueprint = client.generate_blueprint(schema, "Show sales over time")
        
        valid_marks = ["Bar", "Line", "Area", "Automatic"]
        for sheet in blueprint["sheets"]:
            assert sheet["mark_type"] in valid_marks, \
                f"Invalid mark type: {sheet['mark_type']}"
                
    except ValueError as e:
        pytest.skip(f"API key not configured: {str(e)}")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-m", "requires_api"])
