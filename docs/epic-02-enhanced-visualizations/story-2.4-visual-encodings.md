# Story 2.4: Visual Encodings (Color, Size, Tooltip)

## Story Details
**Epic**: Epic 2 - Enhanced Visualizations  
**Story Points**: 5  
**Priority**: P1 (High)  
**Assignee**: TBD  
**Sprint**: Week 7

## User Story
**As a** user  
**I want** to encode additional dimensions using color, size, and tooltips  
**So that** I can visualize multi-dimensional data in a single chart

## Acceptance Criteria
- [ ] Color encoding by dimension works
- [ ] Color encoding by measure works (gradient)
- [ ] Size encoding works (bubble charts)
- [ ] Tooltip configuration functional
- [ ] LLM understands encoding requests ("color by region")
- [ ] Encodings render correctly in Tableau
- [ ] Legend displays correctly

## Technical Details

### Blueprint Schema Update
```json
{
  "sheets": [{
    "name": "Sales Analysis",
    "mark_type": "Bar",
    "column_field": "category",
    "row_field": "sales",
    "encodings": {
      "color": {
        "field": "region",
        "type": "dimension"
      },
      "size": {
        "field": "quantity",
        "type": "measure"
      },
      "tooltip": ["sales", "quantity", "region"]
    }
  }]
}
```

### XML Encoding Patterns

**Color by Dimension**:
```xml
<encoding clabel='true' field='[Federated.xxxx].[none:region:nk]' palette='tableau10' type='color' />
```

**Size by Measure**:
```xml
<encoding field='[Federated.xxxx].[sum:quantity:qk]' type='size' />
<style>
  <style-rule element='mark'>
    <format attr='size' value='1.5' />
  </style-rule>
</style>
```

**Tooltip Configuration**:
```xml
<encoding field='[Federated.xxxx].[none:category:nk]' type='tooltip' />
<encoding field='[Federated.xxxx].[sum:sales:qk]' type='tooltip' />
```

## Implementation Tasks
- [ ] Extend blueprint schema with encodings object
- [ ] Implement `_build_encoding_xml()` method
- [ ] Add color encoding (dimension)
- [ ] Add color encoding (measure with gradient)
- [ ] Add size encoding
- [ ] Add tooltip encoding
- [ ] Update LLM prompt to understand encoding requests
- [ ] Detect "color by X", "size by Y" patterns
- [ ] Test color-coded bar charts
- [ ] Test bubble charts (size encoding)
- [ ] Test tooltips with multiple fields
- [ ] Add default color palettes

## Testing Strategy
- Unit test for encoding XML generation
- Test "sales by category, color by region"
- Test "bubble chart with size = quantity"
- Test tooltip configuration
- Visual validation: verify colors and sizes in Tableau
- Test legend rendering

## Documentation
- Encoding types guide
- Color palette options
- Size scaling best practices
- Tooltip customization examples

## Definition of Done
- [ ] Color, size, and tooltip encodings work
- [ ] LLM understands encoding requests
- [ ] Tests passing >80% coverage
- [ ] Visual validation successful
- [ ] Legends render correctly
- [ ] Documentation complete
- [ ] Code reviewed

## Related Stories
- **Depends On**: Story 2.1 (Chart Types)
- **Blocks**: Story 3.1 (Scatter Plots)

## Notes
- Tableau uses "encoding" XML elements for visual properties
- Color palette: "tableau10" is default, "tableau20" for more categories
- Size encoding typically for scatter/bubble charts
- Tooltip encoding adds fields to hover display

