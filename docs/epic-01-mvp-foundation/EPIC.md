# Epic 1: MVP Foundation

## Epic Overview
Build the foundational components required for a working proof-of-concept Tableau MCP server that can generate basic bar charts from natural language input.

## Business Value
- Validate core technical approach in production environment
- Enable first user workflows (basic dashboard generation)
- Establish foundation for all future features
- Prove 100% valid workbook generation rate

## Success Criteria
- [ ] Generate valid .twb files that open in Tableau Desktop (100% success rate)
- [ ] Support CSV datasets up to 1M rows
- [ ] <5 second generation time for simple workbooks
- [ ] Zero XML syntax errors
- [ ] MCP server integrates with Claude Desktop/Kiro
- [ ] Test coverage >80%

## Timeline
**Duration**: 4 weeks  
**Team Size**: 1-2 developers  
**Priority**: P0 (Critical)

## Dependencies
- Tableau Desktop installed for validation
- LLM API access (Gemini or OpenRouter)
- Python 3.9+ environment

## Stories in this Epic
1. [Story 1.1: Project Setup & Infrastructure](./story-1.1-project-setup.md)
2. [Story 1.2: UUID Generation System](./story-1.2-uuid-system.md)
3. [Story 1.3: Dataset Schema Profiler](./story-1.3-schema-profiler.md)
4. [Story 1.4: XML Generation Engine](./story-1.4-xml-generator.md)
5. [Story 1.5: LLM Integration](./story-1.5-llm-integration.md)
6. [Story 1.6: MCP Server Implementation](./story-1.6-mcp-server.md)
7. [Story 1.7: Testing & Validation](./story-1.7-testing.md)

## Technical Architecture
```
User Input → MCP Host → MCP Server → {
  Schema Profiler (analyze dataset)
  LLM Client (generate blueprint)
  XML Generator (safe injection)
} → .twb File → Tableau Desktop
```

## Risks & Mitigation
| Risk | Impact | Mitigation |
|------|--------|------------|
| XML syntax errors | High | Use pre-validated templates only |
| LLM hallucinations | Medium | Strict JSON schema validation |
| Template not found | High | Clear setup documentation |
| API rate limits | Low | Implement caching |

## Definition of Done
- All stories completed and accepted
- End-to-end demo works reliably
- Documentation complete (README, setup guide)
- Test suite passes with >80% coverage
- Code reviewed and merged to main
- Tagged release v1.0.0

## Related Epics
- **Next**: Epic 2 - Enhanced Visualizations
- **Depends On**: None (foundation epic)
