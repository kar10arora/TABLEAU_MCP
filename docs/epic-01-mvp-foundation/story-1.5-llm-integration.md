# Story 1.5: LLM Integration

## Story Details
**Epic**: Epic 1 - MVP Foundation  
**Story Points**: 5  
**Priority**: P0 (Critical)  
**Assignee**: TBD  
**Sprint**: Week 2-3

## User Story
**As a** developer  
**I want** LLM integration that generates safe JSON blueprints  
**So that** natural language requests can be converted into Tableau specifications

## Acceptance Criteria
- [ ] LLM client supports both Gemini and OpenRouter APIs
- [ ] Blueprint generation uses dataset schema as context
- [ ] Generated blueprints contain valid field names only
- [ ] JSON output follows strict schema validation
- [ ] LLM never generates raw XML (safety rule)
- [ ] Error handling for invalid API responses
- [ ] Response parsing handles markdown code blocks
- [ ] Configuration via environment variables

## Technical Details

### Blueprint JSON Schema
```json
{
  "sheets": [
    {
      "name": "string",
      "column_field": "string (dimension from schema)",
      "row_field": "string (measure from schema)",
      "mark_type": "Bar | Line | Area | Automatic"
    }
  ]
}
```

### LLM Provider Support
- **Gemini**: `google-generativeai` library, model `gemini-pro`
- **OpenRouter**: OpenAI-compatible API, model `anthropic/claude-3-haiku`

### Prompt Engineering Strategy
1. Provide complete schema context (dimensions/measures)
2. Specify exact JSON format required
3. Enforce field name validation rules
4. Request 1-3 sheets based on request complexity
5. No explanations, JSON only

## Implementation Tasks
- [ ] Create `src/llm/client.py` module
- [ ] Implement `LLMClient` class with provider selection
- [ ] Add Gemini API integration
- [ ] Add OpenRouter API integration
- [ ] Build prompt template with schema injection
- [ ] Implement JSON extraction from LLM responses
- [ ] Add validation for field names against schema
- [ ] Add retry logic for API failures
- [ ] Create configuration via environment variables
- [ ] Add logging for debugging

## Testing Strategy
- Unit tests for prompt building
- Mock LLM responses for deterministic testing
- Integration tests with real API calls (optional)
- Test invalid JSON response handling
- Test field name validation
- Test both provider implementations

## Documentation
- API key setup instructions
- Provider selection guide
- Blueprint schema documentation
- Troubleshooting common LLM errors

## Definition of Done
- [ ] Both Gemini and OpenRouter working
- [ ] Blueprints always contain valid field names
- [ ] JSON parsing handles edge cases
- [ ] Test coverage >80%
- [ ] Documentation complete
- [ ] Code reviewed
- [ ] No raw XML generation possible

## Related Stories
- **Depends On**: Story 1.3 (Schema Profiler)
- **Blocks**: Story 1.6 (MCP Server)

## Notes
- Critical safety rule: LLM outputs JSON blueprints ONLY, never raw XML
- Python backend handles all XML manipulation
- Field names must match schema exactly (Tableau will fail otherwise)
- Keep prompts under 2000 tokens for efficiency

