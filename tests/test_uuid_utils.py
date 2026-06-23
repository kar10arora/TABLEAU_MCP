"""
Tests for UUID generation utilities.
"""

import pytest
import sys
import os

# Add src to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.core.uuid_utils import generate_tableau_uuid, UUIDManager


def test_uuid_format():
    """Test UUID format is correct."""
    uuid = generate_tableau_uuid()
    
    # Check format: {XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXX}
    assert uuid.startswith('{')
    assert uuid.endswith('}')
    assert len(uuid) == 38  # 36 chars + 2 braces
    assert uuid.count('-') == 4
    assert uuid.isupper()


def test_uuid_uniqueness():
    """Test that generated UUIDs are unique."""
    uuids = [generate_tableau_uuid() for _ in range(1000)]
    
    # All should be unique
    assert len(uuids) == len(set(uuids))


def test_uuid_manager_pair():
    """Test UUID pair generation."""
    manager = UUIDManager()
    pair = manager.generate_pair()
    
    assert "worksheet_uuid" in pair
    assert "window_uuid" in pair
    assert pair["worksheet_uuid"] != pair["window_uuid"]
    assert pair["worksheet_uuid"].startswith('{')
    assert pair["window_uuid"].startswith('{')


def test_uuid_manager_reset():
    """Test UUID manager reset."""
    manager = UUIDManager()
    
    # Generate some UUIDs
    manager.generate_tableau_uuid()
    manager.generate_tableau_uuid()
    
    assert len(manager._generated_uuids) == 2
    
    # Reset
    manager.reset()
    assert len(manager._generated_uuids) == 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
