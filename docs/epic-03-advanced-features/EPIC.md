# Epic 3: Advanced Features

## Epic Overview
Implement advanced Tableau capabilities including scatter plots, calculated fields, dashboard layouts, and Tableau Server publishing. These features enable sophisticated analytical workflows and production deployment.

## Business Value
- Support complex analytical use cases (correlation, comparison)
- Enable custom business logic through calculated fields
- Provide professional multi-sheet dashboard layouts
- Enable sharing and collaboration via Tableau Server
- Position product for enterprise adoption

## Success Criteria
- [ ] Scatter plots with measure-on-measure rendering
- [ ] Calculated fields working (basic arithmetic, IF/THEN)
- [ ] Multi-sheet dashboards with tiled layouts
- [ ] Tableau Server publishing functional
- [ ] LOD expressions supported (FIXED, INCLUDE, EXCLUDE)
- [ ] Dashboard templates available (2-3 layouts)
- [ ] Publishing success rate >90%
- [ ] Test coverage maintained >80%

## Timeline
**Duration**: 4 weeks  
**Team Size**: 2-3 developers  
**Priority**: P1 (High)

## Dependencies
- Epic 2 (Enhanced Visualizations) complete
- Tableau Server/Cloud access for publishing tests
- REST API credentials configured

## Stories in this Epic
1. [Story 3.1: Scatter Plots & Measure-on-Measure](./story-3.1-scatter-plots.md)
2. [Story 3.2: Calculated Fields](./story-3.2-calculated-fields.md)
3. [Story 3.3: Dashboard Layouts](./story-3.3-dashboard-layouts.md)
4. [Story 3.4: Tableau Server Publishing](./story-3.4-server-publishing.md)

## Technical Architecture

### Extended Blueprint Schema
```json
{
  "sheets": [{
    "name": "Profit vs Sales",
    "mark_type": "Circle",
    "column_field": "sales",
    "row_field": "profit",
    "encodings": {
      "color": "region",
      "size": "quantity"
    }
  }],
  "calculated_fields": [{
    "name": "Profit Ratio",
    "formula": "[Profit] / [Sales]",
    "datatype": "real"
  }],
  "dashboards": [{
    "name": "Executive Dashboard",
    "layout": "tiled",
    "zones": [
      {"worksheet": "Sheet 1", "x": 0, "y": 0, "width": 600, "height": 400},
      {"worksheet": "Sheet 2", "x": 600, "y": 0, "width": 600, "height": 400}
    ]
  }]
}
```

### New XML Components
- `<calculation>` elements for calculated fields
- `<dashboard>` containers for layouts
- `<zone>` elements for worksheet positioning
- LOD expression syntax in calculations

## Risks & Mitigation
| Risk | Impact | Mitigation |
|------|--------|------------|
| Calculated field syntax errors | High | Pre-validated formula templates |
| Dashboard layout complexity | Medium | Start with simple tiled layouts |
| Publishing authentication issues | Medium | Clear setup documentation |
| LOD expression complexity | High | Limit to basic FIXED expressions |

## Definition of Done
- All stories completed and accepted
- Scatter plots render correctly
- Calculated fields functional
- Dashboards with multiple sheets working
- Publishing to Tableau Server successful
- Test suite passes with >80% coverage
- Documentation complete with examples
- Demo video showcasing advanced features
- Tagged release v3.0.0

## Related Epics
- **Depends On**: Epic 2 - Enhanced Visualizations
- **Next**: Epic 4 - Enterprise & Scale

