# Implementation Guide: Bug Fixes & Feature Completion

**Estimated Effort**: 2-3 days  
**Risk Level**: Low (backward compatible)  
**Priority**: P0 (Critical)

---

## Quick Start

### Phase 1: Fix Multi-Dimension Bug (2 hours)

**File**: `tableau_mcp/core/xml_generator.py`

**Changes Required**:
1. Add `_build_field_reference()` method (40 lines)
2. Update `_build_worksheet()` to call it (20 lines)
3. Update datasource-dependencies generation (15 lines)

**Verification**:
```bash
pytest tests/test_multi_dimension_grouping.py -v
```

### Phase 2: Implement Aggregation Support (4 hours)

**Files**: 
- `tableau_mcp/llm/client.py` (update prompt)
- `tableau_mcp/core/xml_generator.py` (add aggregation handling)

**Changes Required**:
1. Update LLM prompt with aggregation rules (25 lines)
2. Add `_get_aggregation_abbrev()` method (15 lines)
3. Update `_build_worksheet()` aggregation parameter (20 lines)

**Verification**:
```bash
pytest tests/test_aggregation_functions.py -v
```

### Phase 3: Verify Story 2.4 (2 hours)

**Actions**:
1. Create test prompts with size encoding
2. Verify color gradient encoding
3. Document any issues found

---

## Detailed Implementation

### Step 1: Add Field Reference Helper

**File**: `tableau_mcp/core/xml_generator.py`

**Location**: Add before `_build_worksheet()` method

```python
def _build_field_reference(self, field_or_fields, ds_id, field_type="dimension", aggregation=None):
    """
    Build Tableau field reference(s) for XML.
    
    Handles both single fields and arrays of fields that need concatenation.
    
    Args:
        field_or_fields: str or list - Field name(s)
        ds_id: str - Datasource ID
        field_type: str - "dimension" for nk, "measure" for qk
        aggregation: str - Aggregation function name (Sum, Avg, etc.)
    
    Returns:
        str: Single field reference or concatenated references
        
    Examples:
        Single dimension: "[ds].[none:Region:nk]"
        Multi dimension: "[ds].[none:Category:nk] + [ds].[none:Region:nk]"
        Single measure: "[ds].[sum:Sales:qk]"
        Multi measure: "[ds].[avg:Sales:qk] + [ds].[sum:Quantity:qk]"
    """
    if isinstance(field_or_fields, list):
        # Multiple fields - concatenate with " + "
        refs = []
        for field in field_or_fields:
            if field_type == "dimension":
                ref = f'[{ds_id}].[none:{field}:nk]'
            else:  # measure
                agg_abbrev = self._get_aggregation_abbrev(aggregation or "Sum")
                ref = f'[{ds_id}].[{agg_abbrev}:{field}:qk]'
            refs.append(ref)
        return ' + '.join(refs)
    else:
        # Single field
        if field_type == "dimension":
            return f'[{ds_id}].[none:{field_or_fields}:nk]'
        else:
            agg_abbrev = self._get_aggregation_abbrev(aggregation or "Sum")
            return f'[{ds_id}].[{agg_abbrev}:{field_or_fields}:qk]'
```

### Step 2: Add Aggregation Mapping

**File**: `tableau_mcp/core/xml_generator.py`

**Location**: Add before `_build_field_reference()` method

```python
def _get_aggregation_abbrev(self, agg_name):
    """
    Map aggregation function name to Tableau abbreviation.
    
    Args:
        agg_name: str - Aggregation name (Sum, Avg, Min, Max, etc.)
    
    Returns:
        str - Tableau abbreviation (sum, avg, min, max, etc.)
    """
    mapping = {
        "Sum": "sum",
        "Avg": "avg",
        "Min": "min",
        "Max": "max",
        "Median": "median",
        "Count": "cnt",
        "CountD": "countd",
        "StdDev": "stdev",
    }
    return mapping.get(agg_name, "sum")
```

### Step 3: Update _build_worksheet Signature

**File**: `tableau_mcp/core/xml_generator.py`

**Current**:
```python
def _build_worksheet(self, name, ds_id, cols, rows, col_datatype, row_datatype,
                     col_role, row_role, col_type, row_type,
                     sort_cfg=None, filters_cfg=None, encodings_cfg=None):
```

**Updated**:
```python
def _build_worksheet(self, name, ds_id, cols, rows, col_datatype, row_datatype,
                     col_role, row_role, col_type, row_type,
                     sort_cfg=None, filters_cfg=None, encodings_cfg=None,
                     aggregation=None):  # ← NEW PARAMETER
    """Build worksheet XML with multi-dimension and custom aggregation support."""
```

### Step 4: Update Column/Row Field Extraction

**File**: `tableau_mcp/core/xml_generator.py`

**Location**: In `_build_worksheet()`, find where cols/rows are extracted (around line 320)

**Replace**:
```python
# OLD CODE - BROKEN:
cols_xml = f'[{ds_id}].[none:{col_field}:nk]'
rows_xml = f'[{ds_id}].[sum:{row_field}:qk]'
```

**With**:
```python
# NEW CODE - FIXED:
# Handle column field(s) - support both string and list
col_field_value = sheet.get("column_field")
col_fields_value = sheet.get("column_fields")

if col_fields_value:
    # Use column_fields array for multi-dimension
    cols_xml = self._build_field_reference(col_fields_value, ds_id, "dimension")
elif col_field_value:
    # Use column_field (string or list from LLM)
    cols_xml = self._build_field_reference(col_field_value, ds_id, "dimension")
else:
    cols_xml = ""

# Handle row field(s) - support both string and list with aggregation
row_field_value = sheet.get("row_field")
row_fields_value = sheet.get("row_fields")
agg = sheet.get("aggregation", "Sum")

if row_fields_value:
    # Multiple row measures
    rows_xml = self._build_field_reference(row_fields_value, ds_id, "measure", agg)
elif row_field_value:
    # Single row field
    rows_xml = self._build_field_reference(row_field_value, ds_id, "measure", agg)
else:
    rows_xml = ""
```

### Step 5: Update Column-Instance Derivation

**File**: `tableau_mcp/core/xml_generator.py`

**Location**: Where column-instance is generated (around line 330-340)

**Replace**:
```python
# OLD CODE - HARDCODED SUM:
col_instance_xml = f'<column-instance column="[{col_field}]" derivation="Sum" name="[sum:{col_field}:qk]" pivot="key" type="quantitative"/>'
```

**With**:
```python
# NEW CODE - DYNAMIC AGGREGATION:
agg = sheet.get("aggregation", "Sum")
agg_abbrev = self._get_aggregation_abbrev(agg)

col_instance_xml = f'<column-instance column="[{col_field}]" derivation="{agg}" name="[{agg_abbrev}:{col_field}:qk]" pivot="key" type="quantitative"/>'
```

### Step 6: Update Compiler Call Site

**File**: `tableau_mcp/core/xml_generator.py`

**Location**: In `compile_workbook()`, where `_build_worksheet()` is called (around line 95)

**Update call to pass aggregation**:
```python
ws_xml = self._build_worksheet(
    name=sheet["name"],
    ds_id=ds_id,
    cols=col_field,
    rows=row_field,
    col_datatype=col_datatype,
    col_role=col_role,
    col_type=col_type,
    row_datatype=row_datatype,
    row_role=row_role,
    row_type=row_type,
    sort_cfg=sort_cfg,
    filters_cfg=filters_cfg,
    encodings_cfg=encodings_cfg,
    aggregation=sheet.get("aggregation")  # ← ADD THIS
)
```

### Step 7: Update LLM Prompt

**File**: `tableau_mcp/llm/client.py`

**Location**: In `_build_prompt()` method, after "Sort Selection Rules" section

**Add**:
```python
prompt = f"""...

## Aggregation Function Selection Rules

Extract the aggregation function keyword from the user request and include in blueprint:

Keyword Mapping:
- "average", "avg", "mean", "typical" → "Avg"
- "median", "mid", "midpoint" → "Median"
- "minimum", "min", "lowest", "least" → "Min"
- "maximum", "max", "highest", "most" → "Max"
- "total", "sum", "combined" → "Sum" (default)
- "count", "number of" → "Count"
- "distinct count", "unique count" → "CountD"
- "std dev", "standard deviation" → "StdDev"

Default to "Sum" if no metric keyword is present.

Example Output:
Input: "Average sales by region"
Output: {{"aggregation": "Avg", "column_field": "Region", "row_field": "Sales_Amount"}}

Include "aggregation" in blueprint when user specifies a metric function.
"""
```

---

## Testing Strategy

### Create Test File: `tests/test_bug_fixes.py`

```python
import pytest
from tableau_mcp.core.xml_generator import TableauXMLCompiler
from tableau_mcp.core.schema_profiler import SchemaProfiler

class TestMultiDimensionFix:
    def test_single_dimension_backward_compat(self):
        """Ensure existing single-dimension workbooks still work"""
        blueprint = {
            "sheets": [{
                "name": "Sales by Region",
                "column_field": "Region",
                "row_field": "Sales_Amount"
            }]
        }
        # Should work without errors
        compiled = self.compile_blueprint(blueprint)
        assert compiled["success"]
        
    def test_multi_dimension_concatenation(self):
        """Multi-dimension fields should concatenate with +"""
        blueprint = {
            "sheets": [{
                "name": "Sales by Category and Region",
                "column_field": ["Product_Category", "Region"],
                "row_field": "Sales_Amount"
            }]
        }
        compiled = self.compile_blueprint(blueprint)
        twb_xml = self.read_workbook(compiled["workbook_path"])
        
        # Check for proper concatenation
        assert "[none:Product_Category:nk] + [none:Region:nk]" in twb_xml
        # Should NOT have Python list syntax
        assert "[none:['Product_Category'" not in twb_xml
        
    def test_three_dimension_grouping(self):
        """Three dimensions should concatenate properly"""
        blueprint = {
            "sheets": [{
                "name": "Sales by Dims",
                "column_fields": ["Region", "Product_Category", "Customer_Type"],
                "row_field": "Sales_Amount"
            }]
        }
        compiled = self.compile_blueprint(blueprint)
        twb_xml = self.read_workbook(compiled["workbook_path"])
        
        assert "[none:Region:nk] + [none:Product_Category:nk] + [none:Customer_Type:nk]" in twb_xml

class TestAggregationFix:
    def test_default_sum_aggregation(self):
        """Without aggregation specified, default to Sum"""
        blueprint = {
            "sheets": [{
                "name": "Sales by Region",
                "column_field": "Region",
                "row_field": "Sales_Amount"
            }]
        }
        compiled = self.compile_blueprint(blueprint)
        twb_xml = self.read_workbook(compiled["workbook_path"])
        assert "[sum:Sales_Amount:qk]" in twb_xml
        
    @pytest.mark.parametrize("agg_name,expected_abbrev", [
        ("Sum", "sum"),
        ("Avg", "avg"),
        ("Min", "min"),
        ("Max", "max"),
        ("Median", "median"),
        ("Count", "cnt"),
        ("CountD", "countd"),
        ("StdDev", "stdev"),
    ])
    def test_all_aggregation_types(self, agg_name, expected_abbrev):
        """All aggregation types should work"""
        blueprint = {
            "sheets": [{
                "name": f"{agg_name} Sales",
                "column_field": "Region",
                "row_field": "Sales_Amount",
                "aggregation": agg_name
            }]
        }
        compiled = self.compile_blueprint(blueprint)
        twb_xml = self.read_workbook(compiled["workbook_path"])
        assert f"[{expected_abbrev}:Sales_Amount:qk]" in twb_xml
        
    def test_aggregation_with_multi_dimension(self):
        """Custom aggregation + multi-dimension should work together"""
        blueprint = {
            "sheets": [{
                "name": "Avg Sales by Category and Region",
                "column_field": ["Product_Category", "Region"],
                "row_field": "Sales_Amount",
                "aggregation": "Avg"
            }]
        }
        compiled = self.compile_blueprint(blueprint)
        twb_xml = self.read_workbook(compiled["workbook_path"])
        
        # Check both features work together
        assert "[avg:Sales_Amount:qk]" in twb_xml
        assert "[none:Product_Category:nk] + [none:Region:nk]" in twb_xml
```

### Run Tests

```bash
# Run all bug fix tests
pytest tests/test_bug_fixes.py -v

# Run with coverage
pytest tests/test_bug_fixes.py -v --cov=tableau_mcp

# Run specific test
pytest tests/test_bug_fixes.py::TestMultiDimensionFix::test_multi_dimension_concatenation -v
```

---

## Validation Checklist

- [ ] **Code Changes Complete**
  - [ ] `_get_aggregation_abbrev()` method added
  - [ ] `_build_field_reference()` method added
  - [ ] `_build_worksheet()` signature updated with `aggregation` parameter
  - [ ] Column/row field extraction updated
  - [ ] Column-instance derivation updated
  - [ ] Compiler call site updated
  - [ ] LLM prompt updated with aggregation rules

- [ ] **Backward Compatibility Verified**
  - [ ] Existing single-dimension blueprints work
  - [ ] Existing non-aggregation requests work
  - [ ] All 5 original test workbooks still generate correctly

- [ ] **New Functionality Tested**
  - [ ] Multi-dimension concatenation works (2 dimensions)
  - [ ] Multi-dimension concatenation works (3+ dimensions)
  - [ ] Avg aggregation works
  - [ ] Min/Max aggregation works
  - [ ] Median aggregation works
  - [ ] Count aggregation works
  - [ ] Multi-dimension + custom aggregation together

- [ ] **XML Validation**
  - [ ] Generated workbooks open in Tableau Desktop
  - [ ] No Tableau validation errors
  - [ ] Multi-dimension fields properly concatenated with "+"
  - [ ] Aggregation derivation attributes correct

- [ ] **Documentation**
  - [ ] Code comments updated
  - [ ] Commit message clear and detailed
  - [ ] CHANGELOG.md updated
  - [ ] README updated with new features

---

## Rollout Plan

**Day 1**: Implement multi-dimension fix + aggregation support  
**Day 2**: Comprehensive testing + validation  
**Day 3**: Story 2.4 verification + documentation

---

## Support & Questions

For implementation questions, refer to:
- `docs/BUGS_AND_FIXES.md` - Detailed issue documentation
- `tableau_mcp/core/xml_generator.py` - Current implementation
- `tests/test_bug_fixes.py` - Test examples
