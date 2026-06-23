"""
Dataset schema profiling module.
Extracts metadata from CSV files without loading entire dataset.
"""

import pandas as pd
from typing import Dict, List, Optional
import os


class SchemaProfiler:
    """Profiles datasets to extract dimensions and measures."""
    
    def __init__(self, max_rows: int = 100):
        """
        Initialize profiler.
        
        Args:
            max_rows: Maximum rows to read for schema detection
        """
        self.max_rows = max_rows
    
    def profile_dataset(self, file_path: str) -> Dict:
        """
        Extract schema metadata from CSV file.
        
        Args:
            file_path: Path to CSV file
            
        Returns:
            dict: Schema metadata with dimensions and measures
            
        Raises:
            FileNotFoundError: If file doesn't exist
            ValueError: If file cannot be parsed
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Dataset not found: {file_path}")
        
        try:
            # Read only first N rows for efficiency
            df = pd.read_csv(file_path, nrows=self.max_rows)
        except Exception as e:
            raise ValueError(f"Failed to parse CSV: {str(e)}")
        
        schema = {
            "file_name": os.path.basename(file_path),
            "absolute_path": os.path.abspath(file_path),
            "dimensions": [],
            "measures": [],
            "total_columns": len(df.columns),
            "sample_row_count": len(df)
        }
        
        for column in df.columns:
            column_info = {
                "name": column,
                "sample_values": df[column].dropna().head(3).tolist()
            }
            
            # Classify as measure or dimension based on dtype
            if df[column].dtype in ['int64', 'float64']:
                column_info["type"] = "quantitative"
                column_info["default_aggregation"] = "Sum"
                schema["measures"].append(column_info)
            else:
                column_info["type"] = "nominal"
                column_info["cardinality"] = df[column].nunique()
                schema["dimensions"].append(column_info)
        
        return schema
    
    def validate_field_name(self, field_name: str, schema: Dict) -> bool:
        """
        Check if field name exists in schema.
        
        Args:
            field_name: Name of field to validate
            schema: Schema dict from profile_dataset()
            
        Returns:
            bool: True if field exists
        """
        all_fields = [d["name"] for d in schema["dimensions"]] + \
                    [m["name"] for m in schema["measures"]]
        
        return field_name in all_fields
    
    def get_field_type(self, field_name: str, schema: Dict) -> Optional[str]:
        """
        Get type of field (dimension or measure).
        
        Args:
            field_name: Name of field
            schema: Schema dict from profile_dataset()
            
        Returns:
            str: "dimension", "measure", or None if not found
        """
        if any(d["name"] == field_name for d in schema["dimensions"]):
            return "dimension"
        if any(m["name"] == field_name for m in schema["measures"]):
            return "measure"
        return None


# Convenience function
def profile_dataset(file_path: str) -> Dict:
    """Quick schema profiling with defaults."""
    profiler = SchemaProfiler()
    return profiler.profile_dataset(file_path)
