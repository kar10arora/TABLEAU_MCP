# Story 2.1: Line & Area Charts

## Story Details
**Epic**: Epic 2 - Enhanced Visualizations  
**Story Points**: 5  
**Priority**: P1 (High)  
**Assignee**: TBD  
**Sprint**: Week 5

## User Story
**As a** user  
**I want** to create line charts and area charts for time-series data  
**So that** I can visualize trends and changes over time

## Acceptance Criteria
- [ ] Line chart generation works from natural language
- [ ] Area chart generation works from natural language
- [ ] LLM understands temporal/trend requests → suggests Line
- [ ] Mark type correctly set in XML (`<mark class='Line' />`)
- [ ] Generated line/area charts render correctly in Tableau
- [ ] Multi-series line charts supported
- [ ] Axis formatting appropriate for trend data

## Technical Details

### Mark Types to Support
- **Line**: `<mark class='Line' />`
- **Area**: `<mark class='Area' />`
- **Automatic**: `<mark class='Automatic' />` (Tableau decides)

### Blueprint Schema Update
```json
{
  "sheets": [{
    "name": "Sales Trend",
    "mark_type": "Line",
    "column_field": "date",
    "row_field": "sales"
  }]
}
```

### XML Template Pattern
```xml
<pane>
  <view>
    <breakdown value='auto' />
  </view>
  <mark class='Line' />
  <encodings>
    <color />
  </encodings>
</pane>
```

### LLM Prompt Updates
Add chart type selection logic:
- Keywords: "trend", "over time", "time series" → Line chart
- Keywords: "area under curve", "cumulative" → Area chart
- Default for date dimensions → Line chart

## Implementation Tasks
- [ ] Update `_build_worksheet()` to accept `mark_type` parameter
- [ ] Add Line and Area mark type templates
- [ ] Update LLM prompt with chart type selection guidance
- [ ] Add chart type keyword detection logic
- [ ] Test line chart generation with date fields
- [ ] Test area chart generation
- [ ] Test multi-series line charts (color by dimension)
- [ ] Update XML validator for new mark types
- [ ] Add examples to documentation

## Testing Strategy
- Unit test for mark type injection
- Integration test: Generate line chart from sales data
- Integration test: Generate area chart
- Visual validation in Tableau Desktop
- Test with various date formats (YYYY-MM-DD, MM/DD/YYYY)
- Test multi-series (e.g., sales by region over time)

## Documentation
- Chart type selection guide
- When to use Line vs Area vs Bar
- Examples of time-series requests
- Limitations and best practices

## Definition of Done
- [ ] Line and Area mark types working
- [ ] LLM selects appropriate chart type
- [ ] Tests passing with >80% coverage
- [ ] Visual validation successful
- [ ] Documentation updated
- [ ] Code reviewed

## Related Stories
- **Depends On**: Story 1.4 (XML Generator)
- **Blocks**: Story 2.4 (Visual Encodings)

## Notes
- Date fields should be automatically recognized as temporal
- Consider adding "Combined (Area+Line)" for advanced users
- Tableau auto-sorts date fields chronologically

