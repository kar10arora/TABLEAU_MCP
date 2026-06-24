# Story 1.7: Testing & Validation - Missing Components & E2E Steps

## 📊 Current Status

### ✅ What's DONE:
- ✅ Pytest configuration (pytest.ini, pyproject.toml)
- ✅ Unit tests for all core modules (13 tests passing)
- ✅ Integration tests for LLM and MCP (10 tests created)
- ✅ Edge case handling in unit tests
- ✅ Error handling validation
- ✅ Sample test datasets created

### ❌ What's MISSING (Story 1.7 Acceptance Criteria):

## 1. ❌ Test Coverage Report (>80% required)

**Status**: NOT GENERATED

### E2E Steps to Complete:

```bash
# Step 1: Install coverage tools (already done)
source venv/bin/activate
pip install pytest-cov

# Step 2: Run tests with coverage report
pytest tests/ --cov=src --cov-report=html --cov-report=term

# Step 3: View the HTML report
open htmlcov/index.html

# Step 4: Document findings
# Look for:
# - Coverage per file (should be >80%)
# - Uncovered lines (if any)
# - Coverage summary
```

**Expected Output**:
```
Name                           Stmts   Miss  Cover
---------------------------------------------------
src/__init__.py                    1      0   100%
src/core/__init__.py               1      0   100%
src/core/uuid_utils.py            30      0   100%
src/core/schema_profiler.py       65      5    92%
src/core/xml_generator.py         85     10    88%
src/llm/client.py                60      8    87%
src/mcp/server.py                45      5    89%
---------------------------------------------------
TOTAL                            287     28    90%
```

---

## 2. ❌ Manual Tableau Desktop Validation

**Status**: NOT DONE

### E2E Steps to Complete:

#### Step 1: Verify Test Workbooks Exist
```bash
ls -lh examples/generated_workbooks/*.twb
```

Expected files:
- `demo_basic.twb`
- `test_mcp_output.twb`
- `mcp_tool_test.twb`

#### Step 2: Open in Tableau Desktop

**For Each Generated Workbook**:

1. **Open Tableau Desktop**
2. **File → Open**
3. **Navigate to**: `examples/generated_workbooks/`
4. **Select**: One of the `.twb` files
5. **Verify**:
   - ✅ File opens without errors
   - ✅ Worksheets visible in tabs
   - ✅ Chart displays correctly
   - ✅ Data connection works
   - ✅ Fields are properly named
   - ✅ Aggregations are correct

#### Step 3: Test Each Workbook

**demo_basic.twb**:
- Should have 2 sheets: "Sales by Region" and "Sales by Category"
- Both should show bar charts
- Check: Data loads, no errors, visualization renders

**test_mcp_output.twb**:
- Generated from LLM request: "sales by category"
- Should show 1 sheet with bar chart
- Check: Chart displays category vs profit

**mcp_tool_test.twb**:
- Generated from MCP tool call
- Should show 1 sheet with bar chart
- Check: Chart displays product vs profit

#### Step 4: Validate Data Accuracy

For each workbook:

```
Expected data from sales_sample.csv:
- Regions: USA, UK, Canada
- Categories: Electronics, Furniture, Clothing
- Products: Laptop, Chair, Phone, Shirt, Tablet, etc.
- Sales range: 80-1200
- Profit range: 25-310

In Tableau:
- Verify bar heights match data values
- Verify axis labels are correct
- Verify no null/missing data
```

#### Step 5: Document Results

Create a checklist like this:

```markdown
# Manual Tableau Validation Checklist

## demo_basic.twb
- [ ] Opens without errors
- [ ] Shows 2 sheets
- [ ] Sheet 1: "Sales by Region" - bar chart - OK/FAIL
  - Data shown: USA, UK, Canada
  - Values visible: YES/NO
- [ ] Sheet 2: "Sales by Category" - bar chart - OK/FAIL
  - Data shown: Electronics, Furniture, Clothing
  - Values visible: YES/NO
- [ ] Data connection working: YES/NO
- [ ] Filters available: YES/NO

## test_mcp_output.twb
- [ ] Opens without errors
- [ ] Shows product vs profit: OK/FAIL
- [ ] Data accurate: YES/NO

## mcp_tool_test.twb
- [ ] Opens without errors
- [ ] Shows category vs profit: OK/FAIL
- [ ] Data accurate: YES/NO
```

---

## 3. ❌ Performance Benchmarks

**Status**: NOT DOCUMENTED

### E2E Steps to Complete:

#### Step 1: Create Performance Test Script

```python
# tests/test_performance.py
import time
import pytest
from src.core.schema_profiler import SchemaProfiler
from src.llm.client import LLMClient
from src.core.xml_generator import TableauXMLCompiler

@pytest.mark.performance
def test_schema_profiling_speed():
    """Profile speed should be <500ms"""
    profiler = SchemaProfiler()
    start = time.time()
    schema = profiler.profile_dataset("examples/sample_datasets/sales_sample.csv")
    elapsed = (time.time() - start) * 1000
    
    assert elapsed < 500, f"Profiling took {elapsed}ms, should be <500ms"
    print(f"Schema profiling: {elapsed:.2f}ms")

@pytest.mark.performance
def test_xml_generation_speed():
    """XML generation should be <100ms"""
    compiler = TableauXMLCompiler("templates/base_template.twb")
    blueprint = {
        "sheets": [{"name": "Test", "column_field": "region", 
                   "row_field": "sales", "mark_type": "Bar"}]
    }
    
    start = time.time()
    result = compiler.compile_workbook(blueprint, "/tmp/test.twb")
    elapsed = (time.time() - start) * 1000
    
    assert elapsed < 100, f"XML generation took {elapsed}ms, should be <100ms"
    print(f"XML generation: {elapsed:.2f}ms")

@pytest.mark.performance
def test_llm_generation_speed():
    """LLM generation should be <5000ms"""
    schema = {"dimensions": [...], "measures": [...]}
    client = LLMClient()
    
    start = time.time()
    blueprint = client.generate_blueprint(schema, "test request")
    elapsed = (time.time() - start) * 1000
    
    assert elapsed < 5000, f"LLM took {elapsed}ms, should be <5000ms"
    print(f"LLM generation: {elapsed:.2f}ms")

@pytest.mark.performance
def test_end_to_end_speed():
    """Full pipeline should be <10000ms"""
    # Full pipeline test
    # Should complete in <10 seconds
```

#### Step 2: Run Performance Tests

```bash
pytest tests/test_performance.py -v -m performance
```

#### Step 3: Document Baseline Results

```
Performance Benchmarks:
========================

Schema Profiling (100 rows):
- Target: <500ms
- Actual: 45ms ✅
- Result: PASS

XML Generation (1 sheet):
- Target: <100ms
- Actual: 23ms ✅
- Result: PASS

LLM Generation (with API):
- Target: <5000ms
- Actual: 2340ms ✅
- Result: PASS

End-to-End Pipeline:
- Target: <10000ms
- Actual: 3200ms ✅
- Result: PASS

Memory Usage:
- Peak: ~150MB ✅
- Result: PASS
```

---

## 4. ❌ Edge Case Testing

**Status**: PARTIAL (some edge cases covered, need more)

### E2E Steps to Complete:

#### Step 1: Create Edge Case Test Script

```python
# tests/test_edge_cases.py
import pytest
import tempfile
from src.core.schema_profiler import SchemaProfiler
from src.core.xml_generator import TableauXMLCompiler

@pytest.mark.edge_cases
def test_large_dataset():
    """Test profiling large dataset (100k+ rows)"""
    # Create large CSV (100k rows)
    # Profile it (should only read first 100)
    # Verify it completes in <500ms
    pass

@pytest.mark.edge_cases
def test_special_characters_in_names():
    """Test fields with special characters"""
    # CSV with fields: "Sales $", "Revenue (USD)", etc.
    # Should handle correctly
    pass

@pytest.mark.edge_cases
def test_unicode_characters():
    """Test unicode in data"""
    # CSV with: 日本, Deutschland, España
    # Should handle correctly
    pass

@pytest.mark.edge_cases
def test_empty_csv():
    """Test empty CSV file"""
    # Should raise FileNotFoundError or ValueError
    # Should handle gracefully
    pass

@pytest.mark.edge_cases
def test_null_values():
    """Test CSV with lots of null values"""
    # Should handle NaN, None, empty cells
    pass

@pytest.mark.edge_cases
def test_single_column_csv():
    """Test CSV with only 1 column"""
    # Should still work
    pass

@pytest.mark.edge_cases
def test_100_column_csv():
    """Test CSV with 100+ columns"""
    # Should handle performance
    pass
```

#### Step 2: Run Edge Case Tests

```bash
pytest tests/test_edge_cases.py -v -m edge_cases
```

---

## 5. ❌ CI/CD Pipeline Integration

**Status**: NOT CONFIGURED

### E2E Steps to Complete:

#### Step 1: Create GitHub Actions Workflow

```yaml
# .github/workflows/test.yml
name: Test Suite

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.9'
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
    
    - name: Run tests
      run: |
        pytest tests/ -v --cov=src --cov-report=xml
    
    - name: Upload coverage
      uses: codecov/codecov-action@v3
      with:
        file: ./coverage.xml
```

#### Step 2: Push to GitHub

```bash
git add .github/workflows/test.yml
git commit -m "Add CI/CD pipeline"
git push origin main
```

#### Step 3: Verify in GitHub

- Go to repository → Actions
- Should see test run
- Coverage report should be uploaded

---

## 6. ❌ Test Documentation

**Status**: PARTIAL

### E2E Steps to Complete:

#### Step 1: Create Testing Guide

```markdown
# Testing Guide

## Running Tests

### All Tests
\`\`\`bash
pytest tests/ -v
\`\`\`

### Specific Test File
\`\`\`bash
pytest tests/test_uuid_utils.py -v
\`\`\`

### With Coverage
\`\`\`bash
pytest tests/ --cov=src --cov-report=html
open htmlcov/index.html
\`\`\`

### Performance Tests
\`\`\`bash
pytest tests/ -m performance -v
\`\`\`

### Edge Cases
\`\`\`bash
pytest tests/ -m edge_cases -v
\`\`\`

## Test Categories

- Unit tests: test_*.py files
- Integration tests: test_*_integration.py
- Performance tests: marked with @pytest.mark.performance
- Edge cases: marked with @pytest.mark.edge_cases

## Adding New Tests

1. Create test file: tests/test_feature.py
2. Import pytest and modules
3. Define test functions (prefix with test_)
4. Run: pytest tests/test_feature.py -v
5. Check coverage
```

---

## 📋 COMPLETE STORY 1.7 TODO CHECKLIST

### Phase 1: Coverage Report (1-2 hours)
- [ ] Run coverage report: `pytest tests/ --cov=src --cov-report=html`
- [ ] Check coverage >80%: `cat .coverage`
- [ ] Document coverage results
- [ ] Fix any uncovered critical paths

### Phase 2: Manual Tableau Validation (1-2 hours)
- [ ] Open Tableau Desktop
- [ ] Open each generated workbook (demo_basic.twb, test_mcp_output.twb, mcp_tool_test.twb)
- [ ] Verify no errors
- [ ] Verify charts display correctly
- [ ] Verify data accuracy
- [ ] Document results in TABLEAU_VALIDATION.md

### Phase 3: Performance Benchmarks (1-2 hours)
- [ ] Create test_performance.py with benchmarks
- [ ] Run performance tests: `pytest tests/test_performance.py -m performance -v`
- [ ] Document baseline metrics
- [ ] Create PERFORMANCE_BENCHMARKS.md

### Phase 4: Edge Case Testing (1-2 hours)
- [ ] Create test_edge_cases.py with edge cases
- [ ] Run edge case tests: `pytest tests/test_edge_cases.py -m edge_cases -v`
- [ ] Fix any failures
- [ ] Document test cases

### Phase 5: CI/CD Integration (30 minutes)
- [ ] Create .github/workflows/test.yml
- [ ] Push to GitHub
- [ ] Verify GitHub Actions runs tests
- [ ] Set up coverage tracking

### Phase 6: Documentation (30 minutes)
- [ ] Create TESTING_GUIDE.md
- [ ] Document all test procedures
- [ ] Update README with testing section
- [ ] Create STORY_1_7_COMPLETE.md

---

## 🎯 Total Effort for Story 1.7

**Total Remaining**: ~6-8 hours

- Coverage Report: 1-2 hours
- Tableau Validation: 1-2 hours
- Performance Benchmarks: 1-2 hours
- Edge Cases: 1-2 hours
- CI/CD: 0.5 hours
- Documentation: 0.5 hours

---

## ✅ Definition of Done for Story 1.7

All of the following must be complete:

- [ ] Test coverage >80% (report generated)
- [ ] All tests passing (including edge cases)
- [ ] Performance benchmarks documented
- [ ] Manual Tableau validation done (3 workbooks verified)
- [ ] CI/CD pipeline configured and working
- [ ] Testing guide documented
- [ ] Edge cases covered
- [ ] Code reviewed
- [ ] All files committed to git

Once all above are done, **Epic 1 = 100% COMPLETE** ✅

