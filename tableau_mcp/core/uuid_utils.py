"""
UUID generation utilities for Tableau workbooks.
Ensures all worksheets and windows have unique identifiers.
"""

import uuid
from typing import Dict, List


class UUIDManager:
    """Manages UUID generation and tracking for Tableau elements."""
    
    def __init__(self):
        self._generated_uuids: List[str] = []
    
    def generate_tableau_uuid(self) -> str:
        """
        Generate a unique, uppercase UUID in Tableau format.
        
        Returns:
            str: UUID in format {XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXX}
        """
        new_uuid = f"{{{str(uuid.uuid4()).upper()}}}"
        
        # Ensure uniqueness (extremely rare collision, but safe check)
        while new_uuid in self._generated_uuids:
            new_uuid = f"{{{str(uuid.uuid4()).upper()}}}"
        
        self._generated_uuids.append(new_uuid)
        return new_uuid
    
    def generate_pair(self) -> Dict[str, str]:
        """
        Generate a matched pair of UUIDs for worksheet and window.
        
        Returns:
            dict: {"worksheet_uuid": str, "window_uuid": str}
        """
        return {
            "worksheet_uuid": self.generate_tableau_uuid(),
            "window_uuid": self.generate_tableau_uuid()
        }
    
    def reset(self):
        """Clear all generated UUIDs. Use with caution."""
        self._generated_uuids.clear()


# Global instance for easy import
uuid_manager = UUIDManager()


def generate_tableau_uuid() -> str:
    """Convenience function using global UUID manager."""
    return uuid_manager.generate_tableau_uuid()
