# Epic 2: Enhanced Visualizations

## Epic Overview
Expand chart type support beyond basic bar charts to include line charts, area charts, sorting, filtering, and visual encodings (color, size, tooltip). Enable users to create rich, interactive visualizations through natural language.

## Business Value
- Support more use cases beyond simple comparisons
- Enable trend analysis and time-series visualizations
- Provide data filtering and sorting capabilities
- Allow visual encoding for multi-dimensional analysis
- Increase product utility and user satisfaction

## Success Criteria
- [ ] Support 5+ chart types (Bar, Line, Area, Text, Combination)
- [ ] Sorting works correctly (ascending/descending)
- [ ] Basic filtering functional (dimension filters)
- [ ] Color encoding by dimension works
- [ ] Size encoding works (bubbles, circles)
- [ ] Tooltip configuration functional
- [ ] Generation time <10s for complex workbooks
- [ ] Test coverage maintained >80%

## Timeline
**Duration**: 4 weeks  
**Team Size**: 2 developers  
**Priority**: P1 (High)

## Dependencies
- Epic 1 (MVP Foundation) must be complete
- Template library needs expansion for new chart types
- LLM prompts require updates for new features

## Stories in this Epic
1. [Story 2.1: Line & Area Charts](./story-2.1-line-area-charts.md)
2. [Story 2.2: Sorting & Ordering](./story-2.2-sorting-ordering.md)
3. [Story 2.3: Basic Filtering](./story-2.3-basic-filtering.md)
4. [Story 2.4: Visual Encodings (Color, Size, Tooltip)](./story-2.4-visual-encodings.md)
5. [Story 2.5: Text KPIs & Summary Numbers](./story-2.5-text-kpis.md)

## Technical Architecture

### Chart Type System
```
Blueprint Schema (Extended):
{
  "sheets": [{
    "name": "string",
    "mark_type": "Bar | Line | Area | Text | Automatic",
    "column_field": "string",
    "row_field": "string",
    "sort": {
      "field": "string",
      "direction": "ASC | DESC"
    },
    "filters": [{
      "field": "string",
      "operator": "=",
      "values": ["string"]
    }],
    "encodings": {
      "color": "field_name",
      "size": "field_name",
      "tooltip": ["field1", "field2"]
    }
  }]
}
```

### XML Extensions Required
- `<mark class='Line' />` support
- `<mark class='Area' />` support
- `<shelf-sorts>` elements for sorting
- `<filter>` elements for dimension filters
- `<encoding>` elements for color/size/tooltip

## Risks & Mitigation
| Risk | Impact | Mitigation |
|------|--------|------------|
| Chart type complexity | Medium | Start simple, iterate |
| Filter syntax errors | High | Pre-validated filter templates |
| LLM chart selection | Medium | Provide clear examples in prompt |
| Performance degradation | Low | Profile and optimize |

## Definition of Done
- All stories completed and accepted
- 5+ chart types working reliably
- Sorting and filtering functional
- Visual encodings render correctly
- Test suite passes with >80% coverage
- Documentation updated with new features
- Demo showcasing all new capabilities
- Tagged release v2.0.0

## Related Epics
- **Depends On**: Epic 1 - MVP Foundation
- **Next**: Epic 3 - Advanced Features

