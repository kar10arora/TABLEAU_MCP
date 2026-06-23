# Story 2.5: Text KPIs & Summary Numbers

## Story Details
**Epic**: Epic 2 - Enhanced Visualizations  
**Story Points**: 3  
**Priority**: P2 (Medium)  
**Assignee**: TBD  
**Sprint**: Week 8

## User Story
**As a** user  
**I want** to display single summary numbers (KPIs) as text  
**So that** I can highlight key metrics prominently

## Acceptance Criteria
- [ ] Text mark type supported
- [ ] Single number KPIs display correctly
- [ ] Number formatting works (currency, percentage, decimals)
- [ ] LLM recognizes KPI requests ("total sales", "average price")
- [ ] Text KPIs can be combined with other charts
- [ ] Font size and styling appropriate

## Technical Details

### Blueprint Schema Update
```json
{
  "sheets": [{
    "name": "Total Sales",
    "mark_type": "Text",
    "column_field": null,
    "row_field": "sales",
    "aggregation": "SUM",
    "format": {
      "number_format": "$#,##0",
      "font_size": 24,
      "align": "center"
    }
  }]
}
```

### XML Text Mark Pattern
```xml
<worksheet name='Total Sales KPI'>
  <table>
    <view>
      <datasources>
        <datasource name='federated.xxxx' />
      </datasources>
      <datasource-dependencies datasource='federated.xxxx'>
        <column datatype='real' name='[sales]' role='measure' type='quantitative' />
        <column-instance column='[sales]' derivation='Sum' name='[sum:sales:qk]' pivot='key' type='quantitative' />
      </datasource-dependencies>
      <aggregation value='true' />
    </view>
    <style>
      <style-rule element='mark'>
        <format attr='size' value='2' />
        <format attr='mark-labels-show' value='true' />
        <format attr='mark-labels-cull' value='false' />
      </style-rule>
    </style>
    <panes>
      <pane>
        <view>
          <breakdown value='auto' />
        </view>
        <mark class='Text' />
        <encodings>
          <text column='[federated.xxxx].[sum:sales:qk]' />
        </encodings>
      </pane>
    </panes>
    <rows />
    <cols />
  </table>
</worksheet>
```

### Aggregation Types to Support
- SUM
- AVG
- MIN
- MAX
- COUNT

## Implementation Tasks
- [ ] Add Text mark type support
- [ ] Implement KPI-specific worksheet builder
- [ ] Add number formatting options
- [ ] Update LLM prompt to recognize KPI requests
- [ ] Detect aggregation type from natural language
- [ ] Add text encoding XML generation
- [ ] Test SUM aggregation KPI
- [ ] Test AVG aggregation KPI
- [ ] Test currency formatting
- [ ] Test percentage formatting
- [ ] Add font size configuration

## Testing Strategy
- Unit test for text mark XML generation
- Test "show total sales"
- Test "average price"
- Test "count of customers"
- Visual validation: verify large, readable numbers
- Test number formatting display

## Documentation
- KPI creation guide
- Aggregation types reference
- Number formatting options
- Best practices for KPI dashboards

## Definition of Done
- [ ] Text mark type working
- [ ] KPIs display correctly
- [ ] Number formatting functional
- [ ] LLM recognizes KPI requests
- [ ] Tests passing >80% coverage
- [ ] Visual validation successful
- [ ] Documentation complete
- [ ] Code reviewed

## Related Stories
- **Depends On**: Story 1.4 (XML Generator)
- **Related To**: Story 3.3 (Dashboard Layouts) - KPIs common in dashboards

## Notes
- Text marks don't use columns/rows shelves
- Aggregation happens in encoding, not shelf
- Consider adding trend indicators (↑↓) in Phase 3
- KPIs often combined with sparklines in dashboards

