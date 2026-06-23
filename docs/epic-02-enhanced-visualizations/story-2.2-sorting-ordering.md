# Story 2.2: Sorting & Ordering

## Story Details
**Epic**: Epic 2 - Enhanced Visualizations  
**Story Points**: 3  
**Priority**: P1 (High)  
**Assignee**: TBD  
**Sprint**: Week 6

## User Story
**As a** user  
**I want** charts to be sorted by specific fields in ascending or descending order  
**So that** I can identify top/bottom performers and patterns easily

## Acceptance Criteria
- [ ] Sorting by dimension works (alphabetical)
- [ ] Sorting by measure works (numerical)
- [ ] Ascending and descending order supported
- [ ] LLM understands "top 10", "highest", "lowest" requests
- [ ] Default sorting applied intelligently
- [ ] Multiple sorts supported (primary, secondary)

## Technical Details

### Blueprint Schema Update
```json
{
  "sheets": [{
    "name": "Top 10 Products",
    "mark_type": "Bar",
    "column_field": "product",
    "row_field": "sales",
    "sort": {
      "field": "sales",
      "direction": "DESC",
      "type": "field"
    }
  }]
}
```

### XML Sort Pattern
```xml
<datasource-dependencies datasource='federated.xxxx'>
  <column-instance column='[product]' derivation='None' name='[none:product:nk]' pivot='key' type='nominal' />
  <column-instance column='[sales]' derivation='Sum' name='[sum:sales:qk]' pivot='key' type='quantitative' />
</datasource-dependencies>
<shelf-sorts>
  <shelf-sort-v2 dimension-to-sort='[federated.xxxx].[none:product:nk]' direction='DESC' is-on-innermost-dimension='true' measure-to-sort-by='[federated.xxxx].[sum:sales:qk]' shelf='rows' />
</shelf-sorts>
```

### Sort Types
1. **Alphabetical**: Sort dimension alphabetically
2. **Manual**: Custom order (Phase 3 feature)
3. **Field**: Sort by another field's value
4. **Nested**: Multiple level sorting

## Implementation Tasks
- [ ] Extend blueprint schema with sort configuration
- [ ] Implement `_build_sort_xml()` method
- [ ] Inject `<shelf-sorts>` into worksheet XML
- [ ] Update LLM prompt to understand sort keywords
- [ ] Add sort direction detection (ASC/DESC)
- [ ] Handle "top N" and "bottom N" requests
- [ ] Test alphabetical sorting
- [ ] Test numerical sorting
- [ ] Test combined with filters

## Testing Strategy
- Unit test for sort XML generation
- Test "top 10 products by sales"
- Test "lowest sales by region"
- Test alphabetical sorting
- Visual validation: bars appear in correct order
- Test interaction with filtering

## Documentation
- Sorting syntax guide
- Natural language examples
- Limitations (e.g., no multi-field nested sorts in MVP)

## Definition of Done
- [ ] Sorting works for dimensions and measures
- [ ] ASC and DESC directions supported
- [ ] LLM understands sort requests
- [ ] Tests passing
- [ ] Visual validation successful
- [ ] Documentation updated
- [ ] Code reviewed

## Related Stories
- **Depends On**: Story 1.4 (XML Generator)
- **Related To**: Story 2.3 (Filtering)

## Notes
- Tableau's `<shelf-sorts>` require correct column-instance references
- Sort direction: DESC = descending (high to low)
- Consider caching sort patterns for common requests

