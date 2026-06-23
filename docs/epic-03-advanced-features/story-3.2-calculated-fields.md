# Story 3.2: Calculated Fields

## Story Details
**Epic**: Epic 3 - Advanced Features  
**Story Points**: 8  
**Priority**: P1 (High)  
**Assignee**: TBD  
**Sprint**: Week 10

## User Story
**As a** user  
**I want** to create custom calculated fields with formulas  
**So that** I can perform custom business logic and derived metrics

## Acceptance Criteria
- [ ] Basic arithmetic calculations work (+, -, *, /)
- [ ] IF/THEN/ELSE logic supported
- [ ] Calculated fields appear in generated workbooks
- [ ] LLM understands calculation requests
- [ ] Calculated fields can be used in visualizations
- [ ] LOD expressions supported (FIXED)
- [ ] Aggregation functions work (SUM, AVG, etc.)

## Technical Details

### Blueprint Schema Update
```json
{
  "calculated_fields": [{
    "name": "Profit Ratio",
    "formula": "[Profit] / [Sales]",
    "datatype": "real",
    "role": "measure"
  }, {
    "name": "Category Label",
    "formula": "IF [Sales] > 1000 THEN 'High' ELSE 'Low' END",
    "datatype": "string",
    "role": "dimension"
  }],
  "sheets": [{
    "name": "Analysis",
    "row_field": "Profit Ratio",
    "column_field": "Category"
  }]
}
```

### XML Calculation Pattern
```xml
<datasource-dependencies datasource='federated.xxxx'>
  <column datatype='real' name='[profit]' role='measure' type='quantitative' />
  <column datatype='real' name='[sales]' role='measure' type='quantitative' />
  
  <!-- Calculated field definition -->
  <column caption='Profit Ratio' datatype='real' name='[Calculation_123456789]' role='measure' type='quantitative'>
    <calculation class='tableau' formula='[profit] / [sales]' />
  </column>
  
  <column-instance column='[Calculation_123456789]' derivation='User' name='[none:Calculation_123456789:ok]' pivot='key' type='ordinal' />
</datasource-dependencies>
```

### Supported Operations (MVP)
1. **Arithmetic**: +, -, *, /
2. **Comparisons**: >, <, >=, <=, =, !=
3. **Logical**: IF/THEN/ELSE, AND, OR
4. **Aggregations**: SUM, AVG, MIN, MAX, COUNT
5. **LOD**: FIXED (INCLUDE/EXCLUDE in Phase 4)

### Formula Syntax Examples
```
Basic arithmetic:
  [Profit] / [Sales]
  [Price] * [Quantity]
  [Revenue] - [Cost]

Conditional logic:
  IF [Sales] > 1000 THEN 'High' ELSE 'Low' END
  IF [Region] = 'USA' THEN [Sales] * 1.0 ELSE [Sales] * 0.9 END

LOD Expression:
  {FIXED [Category] : SUM([Sales])}
```

## Implementation Tasks
- [ ] Create `CalculatedFieldGenerator` class
- [ ] Implement formula parser (basic validation)
- [ ] Generate `<calculation>` XML elements
- [ ] Assign unique calculation IDs
- [ ] Inject calculated fields into datasource-dependencies
- [ ] Support arithmetic operations
- [ ] Support IF/THEN/ELSE logic
- [ ] Support LOD expressions (FIXED)
- [ ] Update LLM prompt to detect calculation requests
- [ ] Add field name validation (references must exist)
- [ ] Test arithmetic calculations
- [ ] Test conditional logic
- [ ] Test LOD expressions
- [ ] Test using calculated fields in charts

## Testing Strategy
- Unit test formula parsing
- Unit test calculation XML generation
- Test "show profit margin (profit / sales)"
- Test "categorize sales as high or low"
- Test "{FIXED [Region] : SUM([Sales])}"
- Visual validation: calculated fields work in Tableau
- Test calculated field in bar chart
- Test calculated field in filter

## Documentation
- Calculated field syntax guide
- Supported functions reference
- LOD expression examples
- Formula best practices
- Limitations (no regex, no complex nested logic)

## Definition of Done
- [ ] Arithmetic calculations working
- [ ] IF/THEN/ELSE logic functional
- [ ] LOD FIXED expressions working
- [ ] LLM generates calculation requests
- [ ] Calculated fields usable in charts
- [ ] Tests passing >80% coverage
- [ ] Visual validation successful
- [ ] Documentation complete
- [ ] Code reviewed

## Related Stories
- **Depends On**: Story 1.3 (Schema Profiler)
- **Related To**: Story 3.1 (Scatter Plots) - often used together

## Notes
- Calculated field names must be unique
- Use generated IDs (Calculation_<timestamp>) for uniqueness
- LLM should suggest calculations based on request context
- Tableau formulas are case-insensitive
- Field references must be wrapped in brackets: [field_name]

