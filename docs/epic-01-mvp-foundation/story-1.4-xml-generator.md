# Story 1.4: XML Generation Engine

## Story Details
**Epic**: Epic 1 - MVP Foundation  
**Story Points**: 8  
**Priority**: P0 (Critical)  
**Assignee**: TBD  
**Sprint**: Week 2

## User Story
**As a** MCP server  
**I want** to safely generate Tableau .twb files from JSON blueprints  
**So that** workbooks open successfully in Tableau Desktop with 100% success rate

## Acceptance Criteria
- [ ] Load and parse base template .twb file
- [ ] Inject worksheets based on JSON blueprint
- [ ] Generate unique UUIDs for all elements
- [ ] Inject window declarations for all sheets
- [ ] Update datasource path to point to user's CSV
- [ ] Write valid XML with proper formatting
- [ ] Handle multiple sheets in single workbook
- [ ] Zero XML syntax errors (validated with Tableau Desktop)
- [ ] Support bar charts (MVP), extensible for other types

## Technical Details

### Core Architecture
```
CRITICAL RULE: LLM NEVER WRITES RAW XML

Flow:
1. Load base_blank.twb (pre-validated template)
2. Parse JSON blueprint from LLM
3. Generate unique UUIDs
4. Inject using lxml (safe tree manipulation)
5. Validate structure
6. Write final .twb file
```

### XML Injection Points
```xml
<workbook>
  <datasources>
    <!-- Update CSV path here -->
    <datasource>
      <connection directory="?" filename="?" />
    </datasource>
  </datasources>
  
  <worksheets>
    <!-- Inject worksheet blocks here -->
    <worksheet name="Sheet1" uuid="{...}">
      <rows>[datasource_id].[field]</rows>
      <cols>[datasource_id].[field]</cols>
    </worksheet>
  </worksheets>
  
  <windows>
    <!-- Inject window blocks here -->
    <window name="Sheet1" uuid="{...}">
      ...
    </window>
  </windows>
</workbook>
```

### Blueprint Input Format
```json
{
  "sheets": [
    {
      "name": "Sales by Category",
      "column_field": "category",
      "row_field": "sales",
      "mark_type": "Bar"
    }
  ]
}
```

## Implementation Tasks
- [ ] Create `src/core/xml_generator.py`
- [ ] Implement TableauXMLCompiler class
- [ ] Implement compile_workbook() main method
- [ ] Implement _build_worksheet() private method
- [ ] Implement _build_window() private method
- [ ] Implement _update_datasource_path() method
- [ ] Integrate with UUIDManager
- [ ] Add lxml tree manipulation logic
- [ ] Create pre-validated XML template strings
- [ ] Handle datasource ID extraction
- [ ] Implement error handling and validation
- [ ] Write integration tests
- [ ] Test with Tableau Desktop validation

## XML Template Strings

### Worksheet Template
```python
def _build_worksheet(self, name: str, ds_id: str, 
                    cols: str, rows: str, 
                    mark_type: str, uuid: str) -> str:
    """Build worksheet XML using safe template."""
    
    cols_ref = f"[{ds_id}].[{cols}]" if cols else ""
    rows_ref = f"[{ds_id}].[{rows}]" if rows else ""
    
    return f"""
    <worksheet name='{name}'>
      <table>
        <view>
          <datasources>
            <datasource name='{ds_id}' />
          </datasources>
          <datasource-dependencies datasource='{ds_id}'>
            <column datatype='string' name='[{cols}]' 
                    role='dimension' type='nominal' />
            <column datatype='real' name='[{rows}]' 
                    role='measure' type='quantitative' />
          </datasource-dependencies>
          <aggregation value='true' />
        </view>
        <style />
        <panes>
          <pane>
            <view><breakdown value='auto' /></view>
            <mark class='{mark_type}' />
          </pane>
        </panes>
        <rows>{rows_ref}</rows>
        <cols>{cols_ref}</cols>
      </table>
      <simple-id uuid='{uuid}' />
    </worksheet>
    """
```

## Testing Strategy

### Unit Tests
```python
def test_template_loading():
    """Test template file loads successfully."""
    compiler = TableauXMLCompiler("templates/base_blank.twb")
    assert compiler.template_path.exists()

def test_datasource_extraction():
    """Test extracting datasource ID from template."""
    compiler = TableauXMLCompiler("templates/base_blank.twb")
    tree = etree.parse(compiler.template_path)
    ds_id = tree.find(".//datasource").get("name")
    assert ds_id.startswith("federated.")

def test_simple_workbook_generation():
    """Test generating workbook with one sheet."""
    blueprint = {
        "sheets": [{
            "name": "Test Sheet",
            "column_field": "category",
            "row_field": "sales",
            "mark_type": "Bar"
        }]
    }
    
    result = compiler.compile_workbook(
        blueprint=blueprint,
        output_path="tests/output/test.twb"
    )
    
    assert result["success"] == True
    assert result["sheets_created"] == 1
    assert os.path.exists("tests/output/test.twb")
```

### Integration Tests
```python
def test_workbook_opens_in_tableau():
    """CRITICAL: Test generated workbook opens in Tableau."""
    # Generate workbook
    compiler.compile_workbook(blueprint, "test.twb", dataset_path)
    
    # Validate with Tableau (if available)
    # Or manual validation documented
    assert file_is_valid_xml("test.twb")
```

### Validation Checklist
- [ ] Generated XML is well-formed
- [ ] All UUIDs are unique
- [ ] Datasource path is correct
- [ ] Worksheet/window names match
- [ ] Field references use correct syntax
- [ ] Opens in Tableau Desktop without errors

## Error Handling
```python
# Template not found
raise FileNotFoundError(f"Template not found: {template_path}")

# Invalid blueprint
raise ValueError("Blueprint missing required 'sheets' key")

# Datasource not found in template
raise ValueError("Template missing datasource element")

# Write failure
raise IOError(f"Failed to write workbook: {output_path}")
```

## Performance Requirements
- Load template: <50ms
- Generate 1 sheet: <100ms
- Generate 10 sheets: <500ms
- Write file: <100ms

## Dependencies
- lxml>=4.9.0 (XML parsing/manipulation)
- src.core.uuid_utils (UUID generation)
- os, pathlib (file operations)

## Definition of Done
- [ ] Code implemented and reviewed
- [ ] All unit tests pass (>85% coverage)
- [ ] Integration test with real template passes
- [ ] Generated workbooks open in Tableau Desktop
- [ ] Zero XML syntax errors
- [ ] Docstrings complete
- [ ] Type hints added
- [ ] Performance benchmarks met
- [ ] Error messages are actionable

## Related Stories
- **Blocks**: Story 1.6 (MCP Server needs XML generator)
- **Depends On**: Story 1.1 (Project Setup)
- **Depends On**: Story 1.2 (UUID System)

## Integration Points
```python
# Called by MCP Server
from src.core.xml_generator import TableauXMLCompiler
from src.core.uuid_utils import generate_tableau_uuid

compiler = TableauXMLCompiler("templates/base_blank.twb")
result = compiler.compile_workbook(
    blueprint=llm_blueprint,
    output_path="output.twb",
    dataset_path=user_csv_path
)
```

## Critical Notes
- **NEVER** let LLM generate raw XML strings
- **ALWAYS** use pre-validated template blocks
- **ALWAYS** generate unique UUIDs for each element
- **ALWAYS** validate output with Tableau Desktop
- Template must exist before running (user provides base_blank.twb)

## References
- Ground-level validation: [tableau_mcp_requirement.md](../../tableau_mcp_requirement.md)
- XML structure analysis from manual testing
- Tableau XML schema (implicit, no official spec)
