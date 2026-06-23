# Story 3.3: Dashboard Layouts

## Story Details
**Epic**: Epic 3 - Advanced Features  
**Story Points**: 8  
**Priority**: P1 (High)  
**Assignee**: TBD  
**Sprint**: Week 11

## User Story
**As a** user  
**I want** to combine multiple worksheets into organized dashboards  
**So that** I can present comprehensive insights in a single view

## Acceptance Criteria
- [ ] Multi-sheet dashboards generate correctly
- [ ] Tiled layout supported (simple grid)
- [ ] Dashboard zones positioned correctly
- [ ] All worksheets render in dashboard
- [ ] LLM understands multi-chart requests
- [ ] Dashboard templates available (2-3 layouts)
- [ ] Dashboard opens correctly in Tableau Desktop

## Technical Details

### Blueprint Schema Update
```json
{
  "sheets": [
    {"name": "Sales Trend", "mark_type": "Line", ...},
    {"name": "Top Products", "mark_type": "Bar", ...},
    {"name": "Regional Map", "mark_type": "Map", ...}
  ],
  "dashboards": [{
    "name": "Executive Dashboard",
    "layout": "tiled",
    "size": {"width": 1200, "height": 800},
    "zones": [
      {
        "type": "worksheet",
        "name": "Sales Trend",
        "x": 0,
        "y": 0,
        "width": 1200,
        "height": 400
      },
      {
        "type": "worksheet",
        "name": "Top Products",
        "x": 0,
        "y": 400,
        "width": 600,
        "height": 400
      },
      {
        "type": "worksheet",
        "name": "Regional Map",
        "x": 600,
        "y": 400,
        "width": 600,
        "height": 400
      }
    ]
  }]
}
```

### XML Dashboard Pattern
```xml
<dashboards>
  <dashboard name='Executive Dashboard'>
    <style />
    <size maxheight='800' maxwidth='1200' minheight='800' minwidth='1200' />
    <zones>
      <!-- Top zone: Sales Trend -->
      <zone h='400' id='1' type='layout-basic' w='1200' x='0' y='0'>
        <zone h='400' id='2' name='Sales Trend' w='1200' x='0' y='0' />
      </zone>
      
      <!-- Bottom-left zone: Top Products -->
      <zone h='400' id='3' type='layout-basic' w='600' x='0' y='400'>
        <zone h='400' id='4' name='Top Products' w='600' x='0' y='400' />
      </zone>
      
      <!-- Bottom-right zone: Regional Map -->
      <zone h='400' id='5' type='layout-basic' w='600' x='600' y='400'>
        <zone h='400' id='6' name='Regional Map' w='600' x='600' y='400' />
      </zone>
    </zones>
    <devicelayouts>
      <devicelayout name='Desktop' />
      <devicelayout name='Tablet' />
      <devicelayout name='Phone' />
    </devicelayouts>
    <simple-id uuid='{DASHBOARD-UUID}' />
  </dashboard>
</dashboards>

<windows>
  <window class='dashboard' name='Executive Dashboard'>
    <simple-id uuid='{WINDOW-UUID}' />
  </window>
</windows>
```

### Dashboard Layout Types (MVP)
1. **Tiled**: Simple grid-based layout
2. **Vertical Split**: Stack sheets vertically
3. **Horizontal Split**: Place sheets side-by-side
4. **Grid 2x2**: Four equal quadrants

## Implementation Tasks
- [ ] Create `DashboardBuilder` class
- [ ] Implement zone coordinate calculation
- [ ] Generate `<dashboard>` XML containers
- [ ] Generate `<zone>` elements with positioning
- [ ] Link worksheets to dashboard zones
- [ ] Assign zone IDs sequentially
- [ ] Create dashboard UUID
- [ ] Add dashboard window XML
- [ ] Implement tiled layout algorithm
- [ ] Create 2-3 dashboard templates
- [ ] Update LLM to detect dashboard requests
- [ ] Test 2-sheet dashboard
- [ ] Test 4-sheet dashboard (grid)
- [ ] Test various layout configurations
- [ ] Validate dashboard opens in Tableau

## Testing Strategy
- Unit test zone coordinate calculation
- Unit test dashboard XML generation
- Test "create dashboard with sales trend and top products"
- Test grid layout (2x2)
- Visual validation: all sheets visible in dashboard
- Test zone sizing and positioning
- Test dashboard navigation

## Documentation
- Dashboard creation guide
- Layout types reference
- Zone positioning explanation
- Best practices for dashboard design
- Limitations (tiled only, no floating objects)

## Definition of Done
- [ ] Multi-sheet dashboards working
- [ ] Tiled layout functional
- [ ] Zone positioning correct
- [ ] LLM generates dashboard requests
- [ ] 2-3 templates available
- [ ] Tests passing >80% coverage
- [ ] Visual validation successful
- [ ] Documentation complete
- [ ] Code reviewed

## Related Stories
- **Depends On**: Story 1.4 (XML Generator), Story 2.5 (Text KPIs)
- **Related To**: All chart type stories (combined in dashboards)

## Notes
- Zone IDs must be unique within dashboard
- Zone coordinates: x, y, width, height in pixels
- Tableau supports floating and tiled objects (MVP: tiled only)
- Dashboard UUIDs separate from worksheet UUIDs
- Consider adding legend/filter zones in Phase 4

