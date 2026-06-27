"""
Tests for schema profiling functionality.
"""

import pytest
import sys
import os
import tempfile

# Add src to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from tableau_mcp.core.schema_profiler import SchemaProfiler


def test_profile_simple_dataset():
    """Test profiling a simple CSV dataset."""
    # Create temporary CSV
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.csv') as f:
        f.write("category,product,price,quantity\n")
        f.write("Electronics,Laptop,1200,5\n")
        f.write("Furniture,Chair,450,10\n")
        f.write("Clothing,Shirt,80,20\n")
        temp_path = f.name
    
    try:
        profiler = SchemaProfiler()
        schema = profiler.profile_dataset(temp_path)
        
        # Check basic structure
        assert "dimensions" in schema
        assert "measures" in schema
        assert "total_columns" in schema
        
        # Check column classification
        assert len(schema["dimensions"]) == 2  # category, product
        assert len(schema["measures"]) == 2    # price, quantity
        
        # Check dimension details
        dim_names = [d["name"] for d in schema["dimensions"]]
        assert "category" in dim_names
        assert "product" in dim_names
        
        # Check measure details
        measure_names = [m["name"] for m in schema["measures"]]
        assert "price" in measure_names
        assert "quantity" in measure_names
        
    finally:
        os.unlink(temp_path)


def test_validate_field_name():
    """Test field name validation."""
    # Create temporary CSV
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.csv') as f:
        f.write("name,age,salary\n")
        f.write("John,30,50000\n")
        temp_path = f.name
    
    try:
        profiler = SchemaProfiler()
        schema = profiler.profile_dataset(temp_path)
        
        # Valid fields
        assert profiler.validate_field_name("name", schema) is True
        assert profiler.validate_field_name("age", schema) is True
        assert profiler.validate_field_name("salary", schema) is True
        
        # Invalid fields
        assert profiler.validate_field_name("invalid", schema) is False
        
    finally:
        os.unlink(temp_path)


def test_get_field_type():
    """Test field type detection."""
    # Create temporary CSV
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.csv') as f:
        f.write("region,sales\n")
        f.write("USA,1000\n")
        temp_path = f.name
    
    try:
        profiler = SchemaProfiler()
        schema = profiler.profile_dataset(temp_path)
        
        assert profiler.get_field_type("region", schema) == "dimension"
        assert profiler.get_field_type("sales", schema) == "measure"
        assert profiler.get_field_type("invalid", schema) is None
        
    finally:
        os.unlink(temp_path)


def test_file_not_found():
    """Test error handling for missing file."""
    profiler = SchemaProfiler()
    
    with pytest.raises(FileNotFoundError):
        profiler.profile_dataset("/path/to/nonexistent/file.csv")


def test_invalid_csv():
    """Test error handling for invalid CSV."""
    # Create invalid CSV
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.csv') as f:
        f.write("This is not a valid CSV\n")
        f.write("Just random text\n")
        temp_path = f.name
    
    try:
        profiler = SchemaProfiler()
        # Should still work, pandas is forgiving
        schema = profiler.profile_dataset(temp_path)
        assert schema is not None
        
    finally:
        os.unlink(temp_path)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
