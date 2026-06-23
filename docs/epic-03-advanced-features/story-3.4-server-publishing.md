# Story 3.4: Tableau Server Publishing

## Story Details
**Epic**: Epic 3 - Advanced Features  
**Story Points**: 5  
**Priority**: P2 (Medium)  
**Assignee**: TBD  
**Sprint**: Week 12

## User Story
**As a** user  
**I want** to publish generated workbooks directly to Tableau Server/Cloud  
**So that** I can share dashboards with my team without manual upload

## Acceptance Criteria
- [ ] Publishing to Tableau Server works
- [ ] Publishing to Tableau Cloud works
- [ ] Token-based authentication supported
- [ ] Project selection functional
- [ ] Published workbooks accessible via URL
- [ ] MCP tool `publish_to_tableau_server` working
- [ ] Error handling for auth failures
- [ ] Success confirmation with workbook URL

## Technical Details

### MCP Tool Specification
```python
@mcp.tool()
def publish_to_tableau_server(
    workbook_path: str,
    server_url: str,
    site_name: str,
    project_name: str,
    token_name: str,
    token_value: str
) -> str:
    """
    Publish Tableau workbook to Tableau Server or Cloud.
    
    Args:
        workbook_path: Path to .twb file to publish
        server_url: Tableau Server URL (e.g., https://tableau.company.com)
        site_name: Site name (empty string for default site)
        project_name: Target project name
        token_name: Personal access token name
        token_value: Personal access token secret
        
    Returns:
        JSON with success status and workbook URL
    """
```

### Tableau REST API Flow
```
1. Authenticate (POST /api/3.x/auth/signin)
   → Get auth token and site ID

2. Find project ID (GET /api/3.x/sites/{site-id}/projects)
   → Match project_name to get project ID

3. Publish workbook (POST /api/3.x/sites/{site-id}/workbooks)
   → Upload .twb file with multipart request
   → Returns workbook ID

4. Get workbook details (GET /api/3.x/sites/{site-id}/workbooks/{workbook-id})
   → Extract view URL

5. Sign out (POST /api/3.x/auth/signout)
```

### Environment Configuration
```bash
# .env additions
TABLEAU_SERVER_URL=https://tableau.company.com
TABLEAU_SITE_NAME=
TABLEAU_PROJECT_NAME=Default
TABLEAU_TOKEN_NAME=your_token_name
TABLEAU_TOKEN_VALUE=your_token_secret
```

## Implementation Tasks
- [ ] Create `TableauServerClient` class
- [ ] Implement token-based authentication
- [ ] Implement project lookup
- [ ] Implement workbook upload (multipart/form-data)
- [ ] Handle REST API responses
- [ ] Add error handling (auth, network, validation)
- [ ] Create `publish_to_tableau_server` MCP tool
- [ ] Add configuration via environment variables
- [ ] Test publish to Tableau Server
- [ ] Test publish to Tableau Cloud
- [ ] Test authentication failure handling
- [ ] Test project not found handling
- [ ] Extract and return workbook URL
- [ ] Add logging for debugging

## Testing Strategy
- Unit test REST API client
- Mock REST API responses
- Integration test with test Tableau Server
- Test authentication flow
- Test project selection
- Test successful publish
- Test error scenarios (invalid token, missing project)
- Manual verification: access published workbook

## Documentation
- Publishing setup guide
- Token creation instructions
- Server vs Cloud configuration
- Troubleshooting guide
- Security best practices
- Project permissions explanation

## Definition of Done
- [ ] Publishing to Server working
- [ ] Publishing to Cloud working
- [ ] MCP tool functional
- [ ] Token authentication working
- [ ] Error handling comprehensive
- [ ] Tests passing >80% coverage
- [ ] Manual publish verification successful
- [ ] Documentation complete
- [ ] Code reviewed

## Related Stories
- **Depends On**: Story 1.6 (MCP Server)
- **Optional**: Can be skipped if server access unavailable

## Notes
- Requires Tableau Server/Cloud instance for testing
- Personal access tokens more secure than username/password
- Token creation: Server Settings → Personal Access Tokens
- Publishing requires "Publisher" role or higher
- Consider adding "overwrite existing workbook" option
- REST API version compatibility: use latest stable (3.x)
- Workbook must reference accessible datasources (server-side)

