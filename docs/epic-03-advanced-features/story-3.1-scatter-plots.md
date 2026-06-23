# Story 3.1: Scatter Plots & Measure-on-Measure

## Story Details
**Epic**: Epic 3 - Advanced Features  
**Story Points**: 5  
**Priority**: P1 (High)  
**Assignee**: TBD  
**Sprint**: Week 9

## User Story
**As a** data analyst  
**I want** to create scatter plots with measures on both axes  
**So that** I can analyze correlations and relationships between quantitative variables

## Acceptance Criteria
- [ ] Scatter plots with measure on X and Y axes work
- [ ] Circle mark type supported
- [ ] Color and size encodings work on scatter plots
- [ ] LLM recognizes correlation/comparison requests
- [ ] Detail-level granularity configurable
- [ ] Trendlines can be added (stretch goal)

## Technical Details

### Blueprint Schema for Scatter Plots
```json
{
  "sheets": [{
    "name": "Profit vs Sales",
    "mark_type": "Circle",
    "column_field": "sales",
    "row_field": "profit",
    "detail_field": "product_id",
    "encodings": {
      "color": "category",
      "size": "quantity",
      "tooltip": ["product_name", "sales", "profit"]
    }
  }]
}
```

### XML Pattern for Scatter Plots
```xml
<worksheet name='Profit vs Sales'>
  <table>
    <view>
      <datasource-dependencies datasource='federated.xxxx'>
        <column datatype='real' name='[sales]' role='measure' type='quantitative' />
        <column datatype='real' name='[profit]' role='measure' type='quantitative' />
        <column datatype='integer' name='[product_id]' role='dimension' type='nominal' />
        <column-instance column='[sales]' derivation='Sum' name='[sum:sales:qk]' pivot='key' type='quantitative' />
        <column-instance column='[profit]' derivation='Sum' name='[sum:profit:qk]' pivot='key' type='quantitative' />
        <column-instance column='[product_id]' derivation='None' name='[none:product_id:nk]' pivot='key' type='nominal' />
      </datasource-dependencies>
      <aggregation value='true' />
    </view>
    <panes>
      <pane>
        <view>
          <breakdown value='auto' />
        </view>
        <mark class='Circle' />
        <encodings>
          <color column='[federated.xxxx].[none:category:nk]' />
          <size column='[federated.xxxx].[sum:quantity:qk]' />
          <lod column='[federated.xxxx].[none:product_id:nk]' />
        </encodings>
      </pane>
    </panes>
    <rows>[federated.xxxx].[sum:profit:qk]</rows>
    <cols>[federated.xxxx].[sum:sales:qk]</cols>
  </table>
</worksheet>
```

### Key Differences from Bar Charts
1. **Both axes are measures** (not dimension + measure)
2. **Detail/LOD required** to define granularity
3. **Circle mark type** typical for scatter plots
4. **Size and color encodings** common

## Implementation Tasks
- [ ] Add Circle mark type support
- [ ] Implement measure-on-measure detection
- [ ] Add detail_field support for LOD
- [ ] Update `_build_worksheet()` for dual-measure charts
- [ ] Add LOD encoding XML generation
- [ ] Update LLM prompt for correlation detection
- [ ] Detect "X vs Y", "correlation", "relationship" keywords
- [ ] Test scatter plot with 2 measures
- [ ] Test with color encoding
- [ ] Test with size encoding
- [ ] Test detail field configuration
- [ ] Add default to Circle mark when both axes are measures

## Testing Strategy
- Unit test for measure-on-measure XML
- Test "show profit vs sales by product"
- Test "correlation between price and quantity"
- Visual validation: verify circles at correct positions
- Test with encodings (color, size)
- Test detail field affects granularity

## Documentation
- Scatter plot creation guide
- When to use scatter plots
- Detail field explanation
- Correlation analysis examples

## Definition of Done
- [ ] Scatter plots render correctly
- [ ] Measure-on-measure working
- [ ] Detail field functional
- [ ] LLM recognizes scatter plot requests
- [ ] Tests passing >80% coverage
- [ ] Visual validation successful
- [ ] Documentation complete
- [ ] Code reviewed

## Related Stories
- **Depends On**: Story 2.4 (Visual Encodings)
- **Related To**: Story 3.2 (Calculated Fields) - often used together

## Notes
- Detail field defines level of aggregation (e.g., product_id → one dot per product)
- Without detail field, get single aggregated dot
- Trendlines require additional `<trend>` XML (consider Phase 4)
- Scatter plots powerful for outlier detection

