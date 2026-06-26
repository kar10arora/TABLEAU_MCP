# Story 2.3: Basic Filtering

## Story Details
**Epic**: Epic 2 - Enhanced Visualizations  
**Story Points**: 5  
**Priority**: P1 (High)  
**Assignee**: TBD  
**Sprint**: Week 6

## User Story
**As a** user  
**I want** to filter data in visualizations by specific criteria  
**So that** I can focus on relevant subsets of data

## Acceptance Criteria
- [x] Dimension filtering works (e.g., "only show USA")
- [x] Multiple filter values supported (e.g., "USA, Canada, UK")
- [ ] LLM extracts filter criteria from requests
- [x] Filter XML correctly injected into workbooks
- [ ] Filtered views render correctly in Tableau
- [x] Filter UI visible in generated workbook

## Technical Details

### Blueprint Schema Update
```json
{
  "sheets": [{
    "name": "USA Sales",
    "mark_type": "Bar",
    "column_field": "category",
    "row_field": "sales",
    "filters": [{
      "field": "country",
      "operator": "=",
      "values": ["USA"]
    }]
  }]
}
```

### XML Filter Pattern
```xml
<datasource-dependencies datasource='federated.xxxx'>
  <column datatype='string' name='[country]' role='dimension' type='nominal' />
  <filter class='categorical' column='[country]'>
    <groupfilter function='member' level='[country]'>
      <groupfilter function='level-members' level='[country]' member='USA' />
    </groupfilter>
  </filter>
</datasource-dependencies>
```

### Filter Types to Support (MVP)
1. **Categorical (Dimension)**: Exact match filtering
2. **Multi-Select**: Multiple values (IN operator)
3. **Exclude**: NOT operator (Phase 3)

## Implementation Tasks
- [ ] Extend blueprint schema with filters array
- [ ] Implement `_build_filter_xml()` method
- [ ] Inject filter XML into datasource-dependencies
- [ ] Update LLM prompt to extract filter criteria
- [ ] Add natural language filter detection ("only", "just", "excluding")
- [ ] Handle multi-value filters (comma-separated)
- [ ] Test single-value filter
- [ ] Test multi-value filter
- [ ] Test filter + sort combination
- [ ] Add filter validation (field exists, values valid)

## Testing Strategy
- Unit test for filter XML generation
- Test "show sales for USA only"
- Test "show sales for USA, Canada, Mexico"
- Test "sales by category in 2023"
- Visual validation: verify filtered data in Tableau
- Test interaction with sorting

## Documentation
- Filter syntax guide
- Natural language filter examples
- Supported operators (= only in MVP)
- Multi-value filter syntax

## Definition of Done
- [x] Dimension filtering works
- [x] Multi-value filters supported
- [ ] LLM extracts filters correctly
- [ ] Tests passing >80% coverage
- [ ] Visual validation successful
- [ ] Documentation complete
- [ ] Code reviewed

## Related Stories
- **Depends On**: Story 1.4 (XML Generator)
- **Related To**: Story 2.2 (Sorting)
- **Blocks**: Story 3.2 (Calculated Fields)

## Notes
- Start with dimension filters only (measure filters in Phase 3)
- Filter XML is injected into datasource-dependencies
- Consider adding "top N" filter (combines filter + sort)
- Tableau filter UI should be visible by default

