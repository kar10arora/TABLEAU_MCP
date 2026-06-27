import importlib.resources as resources
from pathlib import Path
import os

def get_template_path() -> str:
    """Find template whether installed or in dev."""
    try:
        if hasattr(resources, 'files'):
            return str(resources.files('tableau_mcp').joinpath(
                'templates', 'base_template.twb'
            ))
    except:
        pass
    
    dev_path = Path(__file__).parent.parent / 'templates' / 'base_template.twb'
    if dev_path.exists():
        return str(dev_path)
    
    raise FileNotFoundError(
        "Install with: pip install tableau-mcp-server"
    )

def get_output_dir(create: bool = True) -> str:
    """Get output dir (default: ~/.tableau-mcp/workbooks)."""
    if env_dir := os.getenv("TABLEAU_OUTPUT_DIR"):
        output_path = Path(env_dir)
    else:
        output_path = Path.home() / '.tableau-mcp' / 'workbooks'
    
    if create:
        output_path.mkdir(parents=True, exist_ok=True)
    
    return str(output_path)