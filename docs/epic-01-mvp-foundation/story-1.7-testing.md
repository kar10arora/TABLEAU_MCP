# Story 1.7: Testing & Validation

## Story Details
**Epic**: Epic 1 - MVP Foundation  
**Story Points**: 3  
**Priority**: P0 (Critical)  
**Assignee**: TBD  
**Sprint**: Week 3-4

## User Story
**As a** developer  
**I want** comprehensive test coverage for all MVP components  
**So that** I can be confident the system works reliably in production

## Acceptance Criteria
- [ ] Test coverage >80% for all core modules
- [ ] Integration tests validate end-to-end workflows
- [ ] Test suite runs in CI/CD pipeline
- [ ] All tests pass before deployment
- [ ] Generated workbooks validated in Tableau Desktop
- [ ] Performance benchmarks established
- [ ] Edge cases covered (large files, invalid input, etc.)

## Technical Details

### Test Structure
```
tests/
├── test_uuid_utils.py          # UUID generation tests
├── test_schema_profiler.py     # Schema profiling tests
├── test_xml_generator.py       # XML compilation tests
├── test_llm_client.py          # LLM integration tests (mocked)
├── test_mcp_server.py          # MCP server tests
└── test_integration.py         # End-to-end tests
```

### Test Categories

**1. Unit Tests**
- UUID uniqueness and format validation
- Schema profiler with various CSV formats
- XML generator with different blueprints
- LLM client with mocked responses

**2. Integration Tests**
- Full pipeline: CSV → Schema → Blueprint → .twb
- MCP tools with real datasets
- Workbook validation in Tableau

**3. Edge Case Tests**
- Large datasets (>100k rows)
- Special characters in field names
- Missing columns in blueprint
- Invalid CSV formats
- Empty datasets
- Unicode characters

**4. Performance Tests**
- Generation time benchmarks
- Memory usage profiling
- Concurrent request handling

## Implementation Tasks
- [ ] Set up pytest configuration
- [ ] Create sample test datasets (CSV files)
- [ ] Write unit tests for uuid_utils.py
- [ ] Write unit tests for schema_profiler.py
- [ ] Write unit tests for xml_generator.py
- [ ] Write unit tests for llm_client.py (with mocks)
- [ ] Write integration tests for full pipeline
- [ ] Write MCP server tests
- [ ] Create workbook validation script (opens in Tableau)
- [ ] Add performance benchmarks
- [ ] Set up test coverage reporting
- [ ] Document testing procedures

## Testing Strategy

### Test Execution
```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=src --cov-report=html

# Run specific test file
pytest tests/test_uuid_utils.py -v

# Run integration tests only
pytest tests/test_integration.py -v
```

### Sample Test Cases

**UUID Tests**:
- Generate 1000 UUIDs and verify uniqueness
- Verify format: `{XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXX}`
- Test UUID manager reset

**Schema Profiler Tests**:
- Profile sample CSV with mixed types
- Handle missing values
- Detect dimension vs measure correctly
- Large file handling (only reads N rows)

**XML Generator Tests**:
- Generate workbook with 1 sheet
- Generate workbook with 3 sheets
- Verify XML structure validity
- Verify UUIDs in output

**Integration Tests**:
- Generate bar chart from sales data
- Open generated workbook in Tableau (manual validation)
- Verify datasource connection works

## Documentation
- Testing guide for developers
- How to add new tests
- CI/CD integration instructions
- Performance baseline documentation

## Definition of Done
- [ ] All tests written and passing
- [ ] Test coverage >80%
- [ ] Performance benchmarks documented
- [ ] Edge cases covered
- [ ] Manual Tableau validation successful
- [ ] CI/CD integration working
- [ ] Documentation complete
- [ ] Code reviewed

## Related Stories
- **Depends On**: All previous Epic 1 stories
- **Blocks**: Epic 2 work

## Notes
- Manual Tableau validation required for workbook files
- Use pytest fixtures for sample data
- Mock LLM calls to avoid API costs in tests
- Keep test execution time under 30 seconds
- Document any Tableau-specific validation steps

