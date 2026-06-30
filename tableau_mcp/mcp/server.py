"""
FastMCP server for Tableau workbook generation.
"""

from fastmcp import FastMCP
from tableau_mcp.core.schema_profiler import SchemaProfiler
from tableau_mcp.core.xml_generator import TableauXMLCompiler
from tableau_mcp.llm.client import LLMClient
import os
import json
from tableau_mcp.paths import get_output_dir,get_template_path

# Initialize FastMCP server
mcp = FastMCP("tableau-mcp-server")

# Initialize components
schema_profiler = SchemaProfiler()
_llm_client = None
TEMPLATE_PATH = get_template_path()


def _get_llm_client():
    """Lazy-load LLM client only when needed."""
    global _llm_client
    if _llm_client is None:
        _llm_client = LLMClient()
    return _llm_client


@mcp.tool()
def inspect_dataset_schema(file_path: str) -> str:
    """
    Analyze dataset and return schema metadata.
    
    Args:
        file_path: Path to CSV dataset file
        
    Returns:
        JSON string with dimensions and measures
    """
    try:
        schema = schema_profiler.profile_dataset(file_path)
        return json.dumps(schema, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e)})


@mcp.tool()
def generate_tableau_workbook(
    dataset_path: str,
    user_request: str,
    output_path: str = None
) -> str:
    """
    Generate complete Tableau workbook from natural language request.

    This tool reads and analyzes the CSV file at dataset_path entirely on its own —
    it profiles the schema, infers field types, and calls an LLM internally.
    DO NOT use filesystem tools (read_file, read_text_file, etc.) to pre-read the CSV
    before calling this tool; that is redundant and unnecessary.

    Handles internally without any extra steps:
    - Schema inference: dimensions, measures, data types, sample values
    - Aggregations: Sum (default), Avg, Min, Max, Median, Count, CountD, StdDev
    - Multiple worksheets (Bar, Line, Area, Circle, Text/KPI mark types)
    - Sorting: ascending/descending by field value or alphabetically
    - Categorical filters: include/exclude specific dimension values
    - Visual encodings: color-by, size-by, tooltip fields
    - Multi-dimension grouped charts

    Args:
        dataset_path: Absolute path to the CSV file on the local filesystem
        user_request: Natural language description of the desired dashboard
        output_path: Where to save the .twb file (optional)

    Returns:
        JSON string with generation result
    """
    try:
        # Step 1: Profile dataset
        schema = schema_profiler.profile_dataset(dataset_path)
        
        # Step 2: Generate blueprint with LLM
        blueprint = _get_llm_client().generate_blueprint(schema, user_request)
        
        # Step 3: Compile workbook
        if output_path is None:
            output_dir = get_output_dir(create=True)
            os.makedirs(output_dir, exist_ok=True)
            output_path = os.path.join(output_dir, "generated_workbook.twb")
        
        compiler = TableauXMLCompiler(TEMPLATE_PATH)
        result = compiler.compile_workbook(
            blueprint=blueprint,
            output_path=output_path,
            dataset_path=dataset_path,
            schema=schema,
        )
        
        result["blueprint_used"] = blueprint
        return json.dumps(result, indent=2)
        
    except Exception as e:
        return json.dumps({
            "success": False,
            "error": str(e)
        })


def main():
    """Entry point for MCP server (used by PyInstaller and CLI)."""
    mcp.run()


if __name__ == "__main__":
    main()
