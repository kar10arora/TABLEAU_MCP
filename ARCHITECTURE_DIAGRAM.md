# Tableau MCP - Complete Architecture & Technical Design

## 1. SYSTEM ARCHITECTURE OVERVIEW

```
╔══════════════════════════════════════════════════════════════════╗
║                     TABLEAU MCP SYSTEM                            ║
║                  (Automatic Dashboard Generator)                  ║
╚══════════════════════════════════════════════════════════════════╝

┌────────────────────────────────────────────────────────────────┐
│ LAYER 1: USER INTERACTION                                      │
│                                                                 │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐        │
│  │   Claude     │  │     Kiro     │  │    Cursor    │        │
│  │   Desktop    │  │              │  │     IDE      │        │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘        │
│         │                  │                  │                 │
│         └──────────────────┼──────────────────┘                │
│                            │                                     │
│                   Natural Language Input                        │
│              "Create dashboard: price by category"             │
└────────────────────────────┬───────────────────────────────────┘
                             │ MCP Protocol
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│ LAYER 2: MCP SERVER (FastMCP Framework)                        │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐  │
│  │  MCP TOOL ROUTER                                         │  │
│  │  ┌────────────────┐  ┌────────────────┐                │  │
│  │  │inspect_dataset │  │generate_tableau│                │  │
│  │  │    _schema     │  │   _workbook    │                │  │
│  │  └────────┬───────┘  └───────┬────────┘                │  │
│  └───────────┼──────────────────┼──────────────────────────┘  │
│              │                   │                              │
└──────────────┼───────────────────┼──────────────────────────────┘
               │                   │
               ▼                   ▼
┌─────────────────────────────────────────────────────────────────┐
│ LAYER 3: CORE ENGINE                                            │
│                                                                 │
│  ┌─────────────────────┐     ┌──────────────────────────┐     │
│  │ Schema Profiler     │     │ LLM Integration Layer    │     │
│  │                     │     │                          │     │
│  │ • Read CSV (100     │────▶│ • OpenRouter API         │     │
│  │   rows max)         │     │ • Gemini Flash API       │     │
│  │ • Detect dimensions │     │ • Phi / Llama models     │     │
│  │ • Detect measures   │     │                          │     │
│  │ • Return metadata   │     │ Returns JSON Blueprint   │     │
│  └─────────────────────┘     └──────────┬───────────────┘     │
│                                          │                      │
│                                          ▼                      │
│  ┌─────────────────────────────────────────────────────────┐  │
│  │ XML GENERATOR (CRITICAL SAFETY LAYER)                   │  │
│  │                                                          │  │
│  │  ┌────────────────────────────────────────────────────┐│  │
│  │  │ RULE: LLM NEVER WRITES RAW XML                     ││  │
│  │  │                                                     ││  │
│  │  │ 1. Load base_template.twb (validated)             ││  │
│  │  │ 2. Parse JSON blueprint from LLM                   ││  │
│  │  │ 3. Generate unique UUIDs                           ││  │
│  │  │ 4. Inject using lxml (safe tree manipulation)     ││  │
│  │  │ 5. Validate structure                              ││  │
│  │  │ 6. Write final .twb                                ││  │
│  │  └────────────────────────────────────────────────────┘│  │
│  └─────────────────────────────────────────────────────────┘  │
│                                                                 │
│  ┌─────────────────────┐     ┌──────────────────────────┐     │
│  │ Field Resolver      │     │ UUID Manager             │     │
│  │ • Map NL to fields  │     │ • Generate unique IDs    │     │
│  │ • Validate names    │     │ • Track sheet/window IDs │     │
│  │ • Apply conventions │     │                          │     │
│  └─────────────────────┘     └──────────────────────────┘     │
└─────────────────────────────────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│ LAYER 4: OUTPUT                                                  │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │ GENERATED TABLEAU WORKBOOK (.twb)                        │  │
│  │                                                           │  │
│  │  <workbook>                                              │  │
│  │    <datasources> ... CSV metadata ...                   │  │
│  │    <worksheets>  ... Multiple sheets with unique UUIDs  │  │
│  │    <windows>     ... UI viewports ...                    │  │
│  │  </workbook>                                             │  │
│  └──────────────────────────────────────────────────────────┘  │
│                            │                                     │
│                            ▼                                     │
│                 ┌──────────────────┐                            │
│                 │ Tableau Desktop  │                            │
│                 │  Opens & Renders │                            │
│                 └──────────────────┘                            │
└─────────────────────────────────────────────────────────────────┘
```

---

## 2. DETAILED COMPONENT ARCHITECTURE

### 2.1 Schema Profiler Component

```
┌────────────────────────────────────────────────────────┐
│  schema_profiler.py                                     │
│                                                         │
│  Input: file_path (CSV)                                │
│    │                                                    │
│    ▼                                                    │
│  ┌─────────────────────────────────────┐              │
│  │ def profile_dataset(file_path):     │              │
│  │                                      │              │
│  │   # Read only first 100 rows        │              │
│  │   df = pd.read_csv(file_path,       │              │
│  │                    nrows=100)        │              │
│  │                                      │              │
│  │   schema = {                         │              │
│  │     "dimensions": [],                │              │
│  │     "measures": []                   │              │
│  │   }                                  │              │
│  │                                      │              │
│  │   for col in df.columns:             │              │
│  │     if df[col].dtype in              │              │
│  │        ['int64', 'float64']:         │              │
│  │       schema["measures"].append(     │              │
│  │         {                             │              │
│  │           "name": col,                │              │
│  │           "type": "quantitative"      │              │
│  │         }                             │              │
│  │       )                               │              │
│  │     else:                             │              │
│  │       schema["dimensions"].append(   │              │
│  │         {                             │              │
│  │           "name": col,                │              │
│  │           "type": "nominal"           │              │
│  │         }                             │              │
│  │       )                               │              │
│  │                                      │              │
│  │   return schema                      │              │
│  └─────────────────────────────────────┘              │
│                                                         │
│  Output: Metadata JSON                                 │
└────────────────────────────────────────────────────────┘
```

### 2.2 LLM Integration Layer

```
┌──────────────────────────────────────────────────────────┐
│  llm/client.py                                            │
│                                                           │
│  ┌────────────────────────────────────────────────────┐ │
│  │ class LLMClient:                                    │ │
│  │                                                     │ │
│  │   def generate_blueprint(self,                     │ │
│  │                         schema: dict,              │ │
│  │                         user_request: str):        │ │
│  │                                                     │ │
│  │     prompt = f"""                                  │ │
│  │     Dataset Schema:                                │ │
│  │     Dimensions: {schema['dimensions']}             │ │
│  │     Measures: {schema['measures']}                 │ │
│  │                                                     │ │
│  │     User Request: {user_request}                   │ │
│  │                                                     │ │
│  │     Generate JSON blueprint:                       │ │
│  │     {{                                              │ │
│  │       "sheets": [{{                                 │ │
│  │         "name": "Sheet1",                          │ │
│  │         "column_field": "<dimension>",             │ │
│  │         "row_field": "<measure>",                  │ │
│  │         "mark_type": "Bar|Line|Area"               │ │
│  │       }}]                                           │ │
│  │     }}                                              │ │
│  │     """                                            │ │
│  │                                                     │ │
│  │     response = self.call_llm_api(prompt)           │ │
│  │     return json.loads(response)                    │ │
│  └────────────────────────────────────────────────────┘ │
│                                                           │
│  Supported Providers:                                    │
│  • OpenRouter (Phi, Llama, etc.)                        │
│  • Google Gemini Flash (free tier)                      │
│  • Ollama (local models)                                │
└──────────────────────────────────────────────────────────┘
```

### 2.3 XML Generator (Core Safety Layer)

```
┌──────────────────────────────────────────────────────────────┐
│  xml_generator.py                                             │
│                                                               │
│  ┌───────────────────────────────────────────────────────┐  │
│  │ class TableauXMLCompiler:                             │  │
│  │                                                        │  │
│  │   def __init__(self, template_path):                  │  │
│  │     self.parser = etree.XMLParser(...)               │  │
│  │                                                        │  │
│  │   def compile_workbook(self,                          │  │
│  │                       blueprint: dict,                │  │
│  │                       output_path: str):              │  │
│  │                                                        │  │
│  │     # 1. Load pristine template                      │  │
│  │     tree = etree.parse(template_path, self.parser)   │  │
│  │     root = tree.getroot()                            │  │
│  │                                                        │  │
│  │     # 2. Extract datasource ID                       │  │
│  │     ds_elem = root.find(".//datasources/datasource") │  │
│  │     ds_id = ds_elem.get("name")                      │  │
│  │                                                        │  │
│  │     # 3. Get parent containers                       │  │
│  │     worksheets_parent = root.find(".//worksheets")   │  │
│  │     windows_parent = root.find(".//windows")         │  │
│  │                                                        │  │
│  │     # 4. Clear existing sheets                       │  │
│  │     worksheets_parent.clear()                        │  │
│  │     windows_parent.clear()                           │  │
│  │                                                        │  │
│  │     # 5. Generate sheets from blueprint              │  │
│  │     for sheet in blueprint["sheets"]:                │  │
│  │       sheet_uuid = generate_tableau_uuid()           │  │
│  │       window_uuid = generate_tableau_uuid()          │  │
│  │                                                        │  │
│  │       # Build worksheet XML (SAFE TEMPLATE)          │  │
│  │       worksheet_xml = self._build_worksheet(         │  │
│  │         name=sheet["name"],                          │  │
│  │         ds_id=ds_id,                                 │  │
│  │         cols=sheet["column_field"],                  │  │
│  │         rows=sheet["row_field"],                     │  │
│  │         uuid=sheet_uuid                              │  │
│  │       )                                               │  │
│  │                                                        │  │
│  │       # Inject into tree                             │  │
│  │       worksheets_parent.append(                      │  │
│  │         etree.fromstring(worksheet_xml)              │  │
│  │       )                                               │  │
│  │                                                        │  │
│  │       # Build window XML                             │  │
│  │       window_xml = self._build_window(               │  │
│  │         name=sheet["name"],                          │  │
│  │         uuid=window_uuid                             │  │
│  │       )                                               │  │
│  │       windows_parent.append(                         │  │
│  │         etree.fromstring(window_xml)                 │  │
│  │       )                                               │  │
│  │                                                        │  │
│  │     # 6. Write final XML                             │  │
│  │     tree.write(output_path, encoding='utf-8',        │  │
│  │               xml_declaration=True)                  │  │
│  └───────────────────────────────────────────────────────┘  │
└──────────────────────────────────────────────────────────────┘
```

---

## 3. DATA FLOW SEQUENCE DIAGRAMS

### 3.1 Successful Dashboard Generation Flow

```
User          MCP Host      MCP Server    Schema       LLM        XML          Tableau
              (Claude)                    Profiler     Client     Generator    Desktop
  │              │              │            │          │            │             │
  │ "Create dashboard: price by category"   │          │            │             │
  │─────────────▶│              │            │          │            │             │
  │              │ inspect_     │            │          │            │             │
  │              │ dataset_     │            │          │            │             │
  │              │ schema()     │            │          │            │             │
  │              │─────────────▶│            │          │            │             │
  │              │              │ profile_   │          │            │             │
  │              │              │ dataset()  │          │            │             │
  │              │              │───────────▶│          │            │             │
  │              │              │            │ Read 100 │            │             │
  │              │              │            │ rows CSV │            │             │
  │              │              │            │──┐       │            │             │
  │              │              │            │  │       │            │             │
  │              │              │            │◀─┘       │            │             │
  │              │              │            │          │            │             │
  │              │              │            │ Return   │            │             │
  │              │              │            │ metadata │            │             │
  │              │              │◀───────────│          │            │             │
  │              │              │            │          │            │             │
  │              │ Metadata     │            │          │            │             │
  │              │ JSON         │            │          │            │             │
  │              │◀─────────────│            │          │            │             │
  │              │              │            │          │            │             │
  │              │ generate_    │            │          │            │             │
  │              │ tableau_     │            │          │            │             │
  │              │ workbook()   │            │          │            │             │
  │              │─────────────▶│            │          │            │             │
  │              │              │ generate_  │          │            │             │
  │              │              │ blueprint()│          │            │             │
  │              │              │────────────┼─────────▶│            │             │
  │              │              │            │          │ Call API   │             │
  │              │              │            │          │ (Gemini/   │             │
  │              │              │            │          │ OpenRouter)│             │
  │              │              │            │          │──┐         │             │
  │              │              │            │          │  │         │             │
  │              │              │            │          │◀─┘         │             │
  │              │              │            │          │            │             │
  │              │              │            │          │ Return     │             │
  │              │              │            │          │ JSON       │             │
  │              │              │            │          │ blueprint  │             │
  │              │              │◀───────────┼──────────│            │             │
  │              │              │            │          │            │             │
  │              │              │ compile_   │          │            │             │
  │              │              │ workbook() │          │            │             │
  │              │              │────────────┼──────────┼───────────▶│             │
  │              │              │            │          │            │ Load        │
  │              │              │            │          │            │ template    │
  │              │              │            │          │            │ .twb        │
  │              │              │            │          │            │──┐          │
  │              │              │            │          │            │  │          │
  │              │              │            │          │            │◀─┘          │
  │              │              │            │          │            │ Generate    │
  │              │              │            │          │            │ UUIDs       │
  │              │              │            │          │            │──┐          │
  │              │              │            │          │            │  │          │
  │              │              │            │          │            │◀─┘          │
  │              │              │            │          │            │ Inject      │
  │              │              │            │          │            │ XML safely  │
  │              │              │            │          │            │──┐          │
  │              │              │            │          │            │  │          │
  │              │              │            │          │            │◀─┘          │
  │              │              │            │          │            │ Write       │
  │              │              │            │          │            │ .twb file   │
  │              │              │            │          │            │──┐          │
  │              │              │            │          │            │  │          │
  │              │              │            │          │            │◀─┘          │
  │              │              │◀───────────┼──────────┼────────────│             │
  │              │              │            │          │            │             │
  │              │ Success:     │            │          │            │             │
  │              │ workbook_    │            │          │            │             │
  │              │ path         │            │          │            │             │
  │              │◀─────────────│            │          │            │             │
  │              │              │            │          │            │             │
  │ "Workbook   │              │            │          │            │             │
  │ created at  │              │            │          │            │             │
  │ path.twb"   │              │            │          │            │             │
  │◀─────────────│              │            │          │            │             │
  │              │              │            │          │            │             │
  │ User opens file manually                 │          │            │             │
  │──────────────┼──────────────┼────────────┼──────────┼────────────┼────────────▶│
  │              │              │            │          │            │             │
  │              │              │            │          │            │             │
  │◀─────────────┼──────────────┼────────────┼──────────┼────────────┼─────────────│
  │ Dashboard renders successfully           │          │            │             │
```

### 3.2 Error Handling Flow

```
MCP Server    XML Generator    Tableau Desktop
    │              │                 │
    │ compile()    │                 │
    │─────────────▶│                 │
    │              │ Generate XML    │
    │              │──┐              │
    │              │  │              │
    │              │◀─┘              │
    │              │ Validation      │
    │              │ Check           │
    │              │──┐              │
    │              │  │ ERROR:       │
    │              │  │ Duplicate    │
    │              │  │ UUID         │
    │              │◀─┘              │
    │              │ Regenerate      │
    │              │ UUID            │
    │              │──┐              │
    │              │  │              │
    │              │◀─┘              │
    │              │ Write file      │
    │              │──┐              │
    │              │  │              │
    │              │◀─┘              │
    │◀─────────────│                 │
    │ Success      │                 │
    │              │                 │
    │              │   User opens    │
    │              │   file          │
    │              │────────────────▶│
    │              │                 │ Tableau
    │              │                 │ validates
    │              │                 │ XML
    │              │                 │──┐
    │              │                 │  │ Valid
    │              │                 │◀─┘
    │              │                 │
    │              │◀────────────────│
    │              │  Renders        │
```

---

## 4. DATABASE/STATE MANAGEMENT

### 4.1 Template Repository Structure

```
templates/
├── base_blank.twb              # Core template (single datasource)
├── multi_datasource.twb        # Multi-source template
├── dashboard_layout.twb        # Pre-configured dashboard zones
└── advanced_calcs.twb          # Template with calculated fields

Each template:
• Pre-validated XML structure
• Placeholder datasource
• Modular worksheet blocks
• Compatible with Tableau 2020.1+
```

### 4.2 Generated Workbook Cache (Optional - Phase 2)

```sql
CREATE TABLE generated_workbooks (
  id UUID PRIMARY KEY,
  user_id VARCHAR,
  dataset_path VARCHAR,
  blueprint_json JSONB,
  output_path VARCHAR,
  created_at TIMESTAMP,
  status VARCHAR, -- 'success', 'failed'
  error_message TEXT
);
```

---

## 5. API SPECIFICATIONS

### 5.1 MCP Tool: `inspect_dataset_schema`

**JSON-RPC Request**:
```json
{
  "jsonrpc": "2.0",
  "method": "tools/call",
  "params": {
    "name": "inspect_dataset_schema",
    "arguments": {
      "file_path": "/path/to/dataset.csv",
      "file_type": "csv"
    }
  },
  "id": 1
}
```

**JSON-RPC Response**:
```json
{
  "jsonrpc": "2.0",
  "result": {
    "content": [
      {
        "type": "text",
        "text": "{\"file_name\": \"dataset.csv\", \"dimensions\": [{\"name\": \"category\", \"type\": \"nominal\"}], \"measures\": [{\"name\": \"price\", \"type\": \"quantitative\"}]}"
      }
    ]
  },
  "id": 1
}
```

### 5.2 MCP Tool: `generate_tableau_workbook`

**JSON-RPC Request**:
```json
{
  "jsonrpc": "2.0",
  "method": "tools/call",
  "params": {
    "name": "generate_tableau_workbook",
    "arguments": {
      "dataset_path": "/path/to/dataset.csv",
      "blueprint": {
        "sheets": [
          {
            "name": "Sales Analysis",
            "column_field": "category",
            "row_field": "actual_price",
            "mark_type": "Bar",
            "sort": {
              "direction": "DESC",
              "by": "actual_price"
            }
          }
        ]
      },
      "output_path": "/path/to/output.twb"
    }
  },
  "id": 2
}
```

**JSON-RPC Response**:
```json
{
  "jsonrpc": "2.0",
  "result": {
    "content": [
      {
        "type": "text",
        "text": "{\"success\": true, \"workbook_path\": \"/path/to/output.twb\", \"sheets_created\": 1}"
      }
    ]
  },
  "id": 2
}
```

---

## 6. SECURITY CONSIDERATIONS

### 6.1 Input Validation
- **File Path Validation**: Check for path traversal attacks
- **File Size Limits**: Max 500MB for CSV files
- **Schema Validation**: JSON blueprint must match strict schema
- **XML Injection Prevention**: Only use pre-validated templates

### 6.2 LLM Safety
- **Prompt Injection Detection**: Filter malicious prompts
- **Output Validation**: Verify JSON structure before processing
- **Rate Limiting**: Prevent API abuse
- **API Key Management**: Secure storage of LLM API credentials

### 6.3 File System Security
- **Sandboxed Writes**: Generate files in designated output directory only
- **Permission Checks**: Verify write permissions before generation
- **Temporary File Cleanup**: Remove temp files after processing

---

## 7. PERFORMANCE OPTIMIZATION

### 7.1 Dataset Profiling
- **Chunked Reading**: Read CSV in 100-row chunks
- **Caching**: Cache schema for repeated requests
- **Parallel Processing**: Profile multiple datasets concurrently

### 7.2 XML Generation
- **Template Caching**: Load templates once, reuse in memory
- **Lazy Loading**: Only parse XML when needed
- **Streaming Writes**: Write large workbooks incrementally

### 7.3 Expected Performance Metrics
| Operation | Target Time |
|-----------|-------------|
| Schema Profiling (1MB CSV) | <200ms |
| Schema Profiling (100MB CSV) | <500ms |
| LLM Blueprint Generation | <2s |
| XML Compilation (1 sheet) | <100ms |
| XML Compilation (10 sheets) | <500ms |
| Total E2E (simple workbook) | <5s |

---

## 8. DEPLOYMENT ARCHITECTURE

### 8.1 Development Setup
```
Local Machine
├── Python 3.9+ environment
├── MCP Server running on stdio
├── Claude Desktop / Kiro as MCP host
└── Tableau Desktop for validation
```

### 8.2 Production Deployment (Phase 3+)
```
┌────────────────────────────────────────┐
│ Cloud Infrastructure (AWS/GCP)         │
│                                         │
│  ┌──────────────────────────────────┐ │
│  │ MCP Server (Docker Container)    │ │
│  │ • FastMCP app                    │ │
│  │ • Python 3.9 runtime             │ │
│  │ • lxml, pandas dependencies      │ │
│  └──────────────────────────────────┘ │
│                                         │
│  ┌──────────────────────────────────┐ │
│  │ Object Storage (S3/GCS)          │ │
│  │ • Template repository            │ │
│  │ • Generated workbook cache       │ │
│  └──────────────────────────────────┘ │
│                                         │
│  ┌──────────────────────────────────┐ │
│  │ API Gateway                      │ │
│  │ • Rate limiting                  │ │
│  │ • Authentication                 │ │
│  └──────────────────────────────────┘ │
└────────────────────────────────────────┘
         │
         ▼
┌────────────────────────────────────────┐
│ MCP Host Clients                        │
│ (Claude Desktop, Kiro, Cursor, etc.)   │
└────────────────────────────────────────┘
```

---

## 9. TESTING STRATEGY

### 9.1 Unit Tests
- Schema Profiler: Various CSV formats, edge cases
- XML Generator: Template injection, UUID generation
- Field Resolver: Name mapping accuracy

### 9.2 Integration Tests
- E2E workbook generation with real datasets
- Tableau Desktop validation (automated with Tableau CLI)
- LLM blueprint generation accuracy

### 9.3 Validation Tests
```python
def test_workbook_opens_in_tableau():
    """
    1. Generate .twb file
    2. Run Tableau CLI validation
    3. Assert no errors
    """
    workbook = generate_workbook(dataset, blueprint)
    result = subprocess.run([
        'tableau', 'validate', workbook.path
    ], capture_output=True)
    assert result.returncode == 0
```

---

## 10. MONITORING & OBSERVABILITY

### 10.1 Key Metrics
- **Success Rate**: % of generated workbooks that open successfully
- **Generation Time**: P50, P95, P99 latency
- **Error Rate**: By error type (XML validation, field not found, etc.)
- **LLM Performance**: Blueprint accuracy rate

### 10.2 Logging Strategy
```python
import logging

logger = logging.getLogger('tableau_mcp')

# Log levels:
# DEBUG: Schema profiling details
# INFO: Successful generation
# WARNING: Non-fatal errors (field name fuzzy match)
# ERROR: Generation failures
# CRITICAL: System failures
```

---

This architecture ensures a robust, scalable, and maintainable system for automated Tableau dashboard generation through MCP.
