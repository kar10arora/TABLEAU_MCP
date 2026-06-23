# Story 1.6: MCP Server Implementation

## Story Details
**Epic**: Epic 1 - MVP Foundation  
**Story Points**: 5  
**Priority**: P0 (Critical)  
**Assignee**: TBD  
**Sprint**: Week 3

## User Story
**As a** user of Claude Desktop or Kiro  
**I want** an MCP server that generates Tableau workbooks from natural language  
**So that** I can create dashboards without manual Tableau work

## Acceptance Criteria
- [ ] FastMCP server exposes 2 tools: `inspect_dataset_schema` and `generate_tableau_workbook`
- [ ] Server integrates with Claude Desktop and Kiro
- [ ] End-to-end pipeline works: request → schema → LLM → XML → .twb
- [ ] Generated workbooks open successfully in Tableau Desktop
- [ ] Error messages are clear and actionable
- [ ] Server handles concurrent requests safely
- [ ] Configuration via environment variables
- [ ] Logging for debugging and monitoring

## Technical Details

### MCP Tools Specification

**Tool 1**: `inspect_dataset_schema`
- **Purpose**: Analyze dataset and return metadata
- **Input**: `file_path: str`
- **Output**: JSON with dimensions, measures, sample values
- **Use Case**: User wants to understand dataset before generating

**Tool 2**: `generate_tableau_workbook`
- **Purpose**: End-to-end workbook generation
- **Inputs**:
  - `dataset_path: str` - Path to CSV file
  - `user_request: str` - Natural language request
  - `output_path: str` (optional) - Custom output location
- **Output**: JSON with success status, workbook path, sheets created
- **Use Case**: Primary tool for dashboard generation

### End-to-End Pipeline
```
User Request
    ↓
MCP Tool Call
    ↓
Schema Profiler (analyze dataset)
    ↓
LLM Client (generate blueprint)
    ↓
XML Generator (compile workbook)
    ↓
.twb File Output
    ↓
Return Success + Path
```

## Implementation Tasks
- [ ] Create `src/mcp/server.py` with FastMCP initialization
- [ ] Implement `inspect_dataset_schema` tool
- [ ] Implement `generate_tableau_workbook` tool
- [ ] Integrate SchemaProfiler, LLMClient, XMLGenerator
- [ ] Add error handling for each pipeline stage
- [ ] Add input validation (file exists, valid paths)
- [ ] Create default output directory structure
- [ ] Add logging for each pipeline step
- [ ] Write integration configuration docs
- [ ] Test with Claude Desktop
- [ ] Test with Kiro IDE

## Testing Strategy
- Integration tests for full pipeline
- Test with sample datasets (sales, products, etc.)
- Test error scenarios (missing file, invalid request)
- Test output workbook validity in Tableau Desktop
- Load testing with concurrent requests
- Test both MCP tools independently

## Documentation
- MCP server setup guide
- Claude Desktop integration instructions
- Kiro IDE integration instructions
- Tool usage examples
- Troubleshooting guide
- Configuration reference

## Definition of Done
- [ ] Both MCP tools working end-to-end
- [ ] Integration with Claude Desktop verified
- [ ] Integration with Kiro verified
- [ ] Generated workbooks open in Tableau successfully
- [ ] Error handling comprehensive
- [ ] Documentation complete with examples
- [ ] Code reviewed
- [ ] Demo video recorded

## Related Stories
- **Depends On**: Story 1.4 (XML Generator), Story 1.5 (LLM Integration)
- **Blocks**: Story 1.7 (Testing)

## Notes
- FastMCP version >=0.2.0 required
- Server must run in Python environment with all dependencies
- Template file (base_blank.twb) must exist before first use
- Output directory created automatically if missing
- Server logs to stdout for MCP host visibility

