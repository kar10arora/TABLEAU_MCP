# Story 1.3: Dataset Schema Profiler

## Story Details
**Epic**: Epic 1 - MVP Foundation  
**Story Points**: 5  
**Priority**: P0 (Critical)  
**Assignee**: TBD  
**Sprint**: Week 1-2

## User Story
**As a** MCP server  
**I want** to analyze CSV datasets and extract metadata without loading the entire file  
**So that** I can understand field types and support large datasets (up to 1M+ rows)

## Acceptance Criteria
- [ ] Profile CSV files by reading only first 100 rows
- [ ] Classify fields as dimensions (categorical) or measures (numeric)
- [ ] Return JSON schema with field names, types, and sample values
- [ ] Support datasets from 10 rows to 1M+ rows
- [ ] Profiling completes in <500ms for 100MB files
- [ ] Handle missing values gracefully
- [ ] Validate field names exist in schema
- [ ] Detect field cardinality for dimensions

## Technical Details

### Schema Output Format
```json
{
  "file_name": "sales.csv",
  "absolute_path": "/path/to/sales.csv",
  "dimensions": [
    {
      "name": "category",
      "type": "nominal",
      "cardinality": 5,
      "sample_values": ["Electronics", "Furniture", "Office"]
    }
  ],
  "measures": [
    {
      "name": "sales",
      "type": "quantitative",
      "default_aggregation": "Sum",
      "sample_values": [1500.50, 2300.00, 450.75]
    }
  ],
  "total_columns": 8,
  "sample_row_count": 100
}
```

### Classification Logic
```python
Dimensions (Categorical):
- String/object dtypes
- Date/datetime types
- Low-cardinality numeric fields (<10 unique values)

Measures (Quantitative):
- int64, float64 dtypes
- High-cardinality fields
- Numeric values suitable for aggregation
```

## Implementation Tasks
- [ ] Create `src/core/schema_profiler.py`
- [ ] Implement SchemaProfiler class
- [ ] Implement profile_dataset() method with pandas
- [ ] Add dimension/measure classification logic
- [ ] Calculate cardinality for dimensions
- [ ] Extract sample values (first 3 non-null)
- [ ] Implement validate_field_name() helper
- [ ] Implement get_field_type() helper
- [ ] Add error handling for:
  - File not found
  - Invalid CSV format
  - Empty files
  - Encoding issues
- [ ] Write comprehensive unit tests
- [ ] Add docstrings and type hints
- [ ] Performance testing with large files

## Testing Strategy

### Unit Tests
```python
def test_small_dataset():
    """Test with small CSV (10 rows)."""
    schema = profiler.profile_dataset("tests/fixtures/small.csv")
    assert len(schema["dimensions"]) > 0
    assert len(schema["measures"]) > 0

def test_large_dataset():
    """Test with large CSV (1M rows) - should only read 100."""
    schema = profiler.profile_dataset("tests/fixtures/large.csv")
    assert schema["sample_row_count"] == 100
    # Verify it didn't load all rows

def test_field_validation():
    """Test field name validation."""
    schema = profiler.profile_dataset("tests/fixtures/sales.csv")
    assert profiler.validate_field_name("category", schema)
    assert not profiler.validate_field_name("invalid_field", schema)

def test_missing_values():
    """Test handling of missing values."""
    schema = profiler.profile_dataset("tests/fixtures/with_nulls.csv")
    # Should still classify fields correctly
```

### Edge Cases
- Empty CSV file
- CSV with only headers
- CSV with all null values in a column
- Special characters in field names
- Very wide files (100+ columns)
- Mixed encoding (UTF-8, Latin-1)

## Performance Requirements
- Small files (<1MB): <100ms
- Medium files (10-50MB): <200ms
- Large files (100MB+): <500ms
- Memory usage: <50MB regardless of file size

## Dependencies
- pandas>=2.0.0 (CSV parsing)
- Python stdlib: os, pathlib

## Definition of Done
- [ ] Code implemented and reviewed
- [ ] All unit tests pass (>90% coverage)
- [ ] Edge cases handled
- [ ] Performance benchmarks met
- [ ] Docstrings complete
- [ ] Type hints added
- [ ] Error messages are clear and actionable
- [ ] Works with sample datasets in examples/

## Related Stories
- **Blocks**: Story 1.5 (LLM needs schema for prompts)
- **Blocks**: Story 1.4 (XML generator needs field types)
- **Depends On**: Story 1.1 (Project Setup)

## Integration Points
```python
# Used by LLM Client
schema = profiler.profile_dataset(csv_path)
llm_client.generate_blueprint(schema, user_request)

# Used by XML Generator
is_measure = profiler.get_field_type(field_name, schema) == "measure"
```

## Notes
- Only read first 100 rows (configurable via MAX_CSV_ROWS_TO_PROFILE)
- Pandas read_csv with nrows parameter is efficient
- Consider caching schemas for repeated requests (Phase 2+)
- Future: Support other formats (Excel, Parquet, databases)

## Sample Test Data
Create test fixtures:
```csv
# tests/fixtures/sample.csv
category,product,sales,quantity
Electronics,Laptop,1500.50,5
Furniture,Desk,450.00,3
Electronics,Mouse,25.99,10
```
