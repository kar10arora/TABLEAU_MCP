# Story 1.2: UUID Generation System

## Story Details
**Epic**: Epic 1 - MVP Foundation  
**Story Points**: 2  
**Priority**: P0 (Critical)  
**Assignee**: TBD  
**Sprint**: Week 1

## User Story
**As a** XML generator  
**I want** unique identifiers for every worksheet and window  
**So that** Tableau doesn't throw duplicate UUID errors (Error Code: D2E8DA72)

## Acceptance Criteria
- [ ] UUIDManager class generates Tableau-formatted UUIDs
- [ ] All generated UUIDs are unique (no collisions)
- [ ] UUID format matches Tableau spec: `{XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXX}`
- [ ] UUIDs are uppercase (Tableau requirement)
- [ ] Can generate worksheet/window UUID pairs
- [ ] Unit tests achieve 100% coverage
- [ ] Performance: Generate 1000 UUIDs in <100ms

## Technical Details

### UUID Format Requirements
```
Tableau Format: {XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXX}
Example: {96C156E4-AF07-4C64-8FBD-1A6DC6FC7F6B}

Rules:
- Must be enclosed in curly braces { }
- Must be uppercase
- Must follow UUID v4 format
- Must be unique across all worksheets and windows
```

### Implementation Approach
```python
import uuid

class UUIDManager:
    def __init__(self):
        self._generated_uuids: List[str] = []
    
    def generate_tableau_uuid(self) -> str:
        """Generate unique Tableau-formatted UUID."""
        new_uuid = f"{{{str(uuid.uuid4()).upper()}}}"
        
        # Ensure uniqueness (collision check)
        while new_uuid in self._generated_uuids:
            new_uuid = f"{{{str(uuid.uuid4()).upper()}}}"
        
        self._generated_uuids.append(new_uuid)
        return new_uuid
    
    def generate_pair(self) -> Dict[str, str]:
        """Generate matched worksheet/window UUID pair."""
        return {
            "worksheet_uuid": self.generate_tableau_uuid(),
            "window_uuid": self.generate_tableau_uuid()
        }
```

## Implementation Tasks
- [ ] Create `src/core/uuid_utils.py`
- [ ] Implement UUIDManager class
- [ ] Implement generate_tableau_uuid() method
- [ ] Implement generate_pair() method
- [ ] Add collision detection logic
- [ ] Create convenience function for single UUID generation
- [ ] Write unit tests (test_uuid_utils.py)
- [ ] Test UUID format validation
- [ ] Test uniqueness across 10,000 generations
- [ ] Add docstrings and type hints

## Testing Strategy

### Unit Tests
```python
def test_uuid_format():
    """Verify UUID matches Tableau format."""
    uuid_str = generate_tableau_uuid()
    assert uuid_str.startswith('{')
    assert uuid_str.endswith('}')
    assert len(uuid_str) == 38
    assert uuid_str == uuid_str.upper()

def test_uuid_uniqueness():
    """Verify no UUID collisions."""
    uuids = [generate_tableau_uuid() for _ in range(1000)]
    assert len(set(uuids)) == 1000

def test_uuid_pair_generation():
    """Verify worksheet/window pairs are unique."""
    pair = uuid_manager.generate_pair()
    assert pair["worksheet_uuid"] != pair["window_uuid"]
```

### Edge Cases
- Empty UUID manager (first generation)
- Concurrent UUID generation (thread safety - optional)
- Reset functionality
- Large-scale generation (10k+ UUIDs)

## Dependencies
- Python stdlib `uuid` module
- No external dependencies

## Performance Requirements
- Generate single UUID: <1ms
- Generate 1000 UUIDs: <100ms
- Memory footprint: <1MB for 10k tracked UUIDs

## Definition of Done
- [ ] Code implemented and reviewed
- [ ] All unit tests pass
- [ ] Test coverage = 100%
- [ ] Docstrings complete
- [ ] Type hints added
- [ ] Performance benchmarks met
- [ ] Code follows style guide (black, flake8)

## Related Stories
- **Blocks**: Story 1.4 (XML Generator needs UUIDs)
- **Depends On**: Story 1.1 (Project Setup)

## Notes
- UUID collisions are extremely rare (1 in 2^122) but we check anyway
- Track generated UUIDs to prevent duplicates within same workbook
- Consider thread-safety if parallel generation needed (Phase 2+)

## References
- Tableau workbook validation error: D2E8DA72 (duplicate UUID)
- Ground-level testing: [tableau_mcp_requirement.md](../../tableau_mcp_requirement.md)
