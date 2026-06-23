# Story 4.1: Multi-Datasource Support

## Story Details
**Epic**: Epic 4 - Enterprise & Scale  
**Story Points**: 8  
**Priority**: P2 (Medium)  
**Assignee**: TBD  
**Sprint**: Week 13

## User Story
**As an** enterprise user  
**I want** to create workbooks using multiple data sources  
**So that** I can blend data from different systems for comprehensive analysis

## Acceptance Criteria
- [ ] Support 2+ CSV datasets in one workbook
- [ ] Data relationships configurable
- [ ] Cross-datasource calculations work
- [ ] Database connections supported (Postgres, MySQL)
- [ ] Live connections vs extracts configurable
- [ ] LLM understands multi-source requests
- [ ] Blended visualizations render correctly

## Technical Details

### Blueprint Schema Update
```json
{
  "datasources": [{
    "name": "Sales Data",
    "type": "csv",
    "path": "/path/to/sales.csv",
    "is_primary": true
  }, {
    "name": "Customer Data",
    "type": "csv",
    "path": "/path/to/customers.csv",
    "is_primary": false
  }],
  "relationships": [{
    "primary_datasource": "Sales Data",
    "primary_field": "customer_id",
    "secondary_datasource": "Customer Data",
    "secondary_field": "id",
    "type": "left"
  }],
  "sheets": [{
    "name": "Sales by Customer Segment",
    "column_field": "Sales Data.product",
    "row_field": "Sales Data.revenue",
    "color_field": "Customer Data.segment"
  }]
}
```

### XML Multi-Datasource Pattern
```xml
<datasources>
  <!-- Primary datasource -->
  <datasource caption='Sales Data' inline='true' name='federated.0abc123' version='18.1'>
    <connection class='federated'>
      <named-connections>
        <named-connection caption='sales' name='textscan.0def456'>
          <connection class='textscan' directory='/path/to' filename='sales.csv' server='' />
        </named-connection>
      </named-connections>
    </connection>
    <column datatype='integer' name='[customer_id]' role='dimension' type='nominal' />
    <column datatype='real' name='[revenue]' role='measure' type='quantitative' />
  </datasource>
  
  <!-- Secondary datasource -->
  <datasource caption='Customer Data' inline='true' name='federated.1ghi789' version='18.1'>
    <connection class='federated'>
      <named-connections>
        <named-connection caption='customers' name='textscan.1jkl012'>
          <connection class='textscan' directory='/path/to' filename='customers.csv' server='' />
        </named-connection>
      </named-connections>
    </connection>
    <column datatype='integer' name='[id]' role='dimension' type='nominal' />
    <column datatype='string' name='[segment]' role='dimension' type='nominal' />
  </datasource>
</datasources>

<worksheet name='Sales by Segment'>
  <table>
    <view>
      <datasources>
        <datasource name='federated.0abc123' />
        <datasource name='federated.1ghi789' />
      </datasources>
      <datasource-dependencies datasource='federated.0abc123'>
        <column datatype='real' name='[revenue]' role='measure' type='quantitative' />
      </datasource-dependencies>
      <datasource-dependencies datasource='federated.1ghi789'>
        <column datatype='string' name='[segment]' role='dimension' type='nominal' />
      </datasource-dependencies>
    </view>
  </table>
</worksheet>
```

### Database Connection Support
```xml
<!-- Postgres connection -->
<connection class='postgres' dbname='analytics' odbc-connect-string-extras='' one-time-sql='' port='5432' server='db.company.com' username='tableau_user' />

<!-- MySQL connection -->
<connection class='mysql' dbname='sales' odbc-connect-string-extras='' one-time-sql='' port='3306' server='mysql.company.com' username='tableau_user' />
```

## Implementation Tasks
- [ ] Update `SchemaProfiler` to handle multiple datasets
- [ ] Create `DatasourceManager` class
- [ ] Implement multi-datasource XML generation
- [ ] Add datasource relationship configuration
- [ ] Support CSV multi-source
- [ ] Add database connection support (Postgres)
- [ ] Add database connection support (MySQL)
- [ ] Implement field referencing with datasource prefix
- [ ] Update LLM prompt for multi-source detection
- [ ] Test 2-source CSV workbook
- [ ] Test CSV + database blend
- [ ] Test cross-datasource calculations
- [ ] Add connection pooling for databases
- [ ] Add credential management

## Testing Strategy
- Unit test multi-datasource XML generation
- Test "combine sales.csv and customers.csv"
- Test "blend sales data with customer demographics"
- Test database connection (Postgres)
- Visual validation: blended fields work in Tableau
- Test relationship configuration
- Test cross-datasource filtering

## Documentation
- Multi-datasource setup guide
- Database connection configuration
- Relationship types explanation
- Security best practices (credentials)
- Supported database types
- Limitations and known issues

## Definition of Done
- [ ] Multi-CSV workbooks working
- [ ] Database connections functional
- [ ] Relationships configurable
- [ ] Cross-datasource calculations work
- [ ] LLM handles multi-source requests
- [ ] Tests passing >80% coverage
- [ ] Visual validation successful
- [ ] Documentation complete
- [ ] Code reviewed

## Related Stories
- **Depends On**: Story 1.3 (Schema Profiler), Story 1.4 (XML Generator)
- **Complex**: High complexity story

## Notes
- Datasource names must be unique
- Relationships define join keys between sources
- Tableau supports data blending and joins (start with blending)
- Database credentials should be encrypted
- Consider adding support for cloud data warehouses (Snowflake, BigQuery) in future
- Live connections require network accessibility from Tableau
- Extract mode downloads data locally (safer for demos)

