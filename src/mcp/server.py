"""
FastMCP server for Tableau workbook generation.
"""

from fastmcp import FastMCP
from src.core.schema_profiler import SchemaProfiler
from src.core.xml_generator import TableauXMLCompiler
from src.llm.client import LLMClient
import os
import json
from src.tableau_mcp.paths import get_output_dir,get_template_path

# Initialize FastMCP server
mcp = FastMCP("tableau-mcp-server")

# Initialize components
schema_profiler = SchemaProfiler()
llm_client = LLMClient()

TEMPLATE_PATH = get_template_path()


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
    
    Args:
        dataset_path: Path to CSV dataset
        user_request: Natural language description of desired dashboard
        output_path: Where to save .twb file (optional)
        
    Returns:
        JSON string with generation result
    """
    try:
        # Step 1: Profile dataset
        schema = schema_profiler.profile_dataset(dataset_path)
        
        # Step 2: Generate blueprint with LLM
        blueprint = llm_client.generate_blueprint(schema, user_request)
        
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


if __name__ == "__main__":
    # Run the MCP server
    mcp.run()
