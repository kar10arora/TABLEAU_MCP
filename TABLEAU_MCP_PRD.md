# Tableau MCP - Complete Product Requirements Document

## Executive Summary

### Product Vision
Create a custom Model Context Protocol (MCP) server that enables automatic Tableau dashboard creation through natural language interaction, leveraging XML manipulation of `.twb` files and free/open-source LLM models.

### Value Proposition
- **Eliminates 20-30% of repetitive dashboard scaffold work**
- **Enables rapid prototyping** of multiple dashboard variations
- **Automates complex calculations** and field configurations
- **Competitive edge** over Tableau's official MCP (focused on consumption vs. creation)

### Technical Feasibility: ✅ PROVEN
Ground-level validation completed through manual XML manipulation tests. Core concept validated through successful programmatic chart generation.

---

## 1. PRODUCT OVERVIEW

### 1.1 Core Concept
**XML File Manipulation Strategy**: Tableau `.twb` files are structured XML documents. The MCP server acts as an intelligent XML Generator/Modifier rather than using unsupported official APIs.

### 1.2 Architecture Philosophy
```
┌─────────────────────────────────────────────────────────────┐
│  LLM NEVER WRITES RAW XML                                   │
│  ↓                                                           │
│  LLM generates JSON configuration blueprints                │
│  ↓                                                           │
│  Python MCP backend safely injects into XML templates       │
└─────────────────────────────────────────────────────────────┘
```

### 1.3 Target Users
- **Data Analysts**: Rapid dashboard scaffolding
- **BI Developers**: Template automation
- **Business Users**: Self-service dashboard generation

---

## 2. TECHNICAL REQUIREMENTS

### 2.1 Core Components

#### Component 1: Dataset Schema Profiler
**Purpose**: Extract metadata without loading massive datasets

**Requirements**:
- Read only first 100 rows for schema detection
- Identify dimensions (string/categorical)  vs. measures (numeric)
- Handle small (<50MB) and large (>10GB) datasets
- Support CSV initially, extensible to other formats

**Input**: File path (local or remote)
**Output**: Lightweight metadata JSON
```json
{
  "file_name": "amazon.csv",
  "dimensions": [{"name": "category", "type": "nominal"}],
  "measures": [{"name": "actual_price", "type": "quantitative"}]
}
```

#### Component 2: XML Template Generator
**Purpose**: Safe, zero-failure XML manipulation

**Critical Architecture Rules**:
1. **Never let LLM generate raw XML**
2. Use pre-validated string templates
3. Programmatic UUID generation for all elements
4. lxml library for safe tree manipulation

**Key Patterns**:
- **Data Layer**: `<datasources>` - Schema definitions
- **Visual Layer**: `<worksheets>` - Field bindings to rows/cols
- **Presentation Layer**: `<windows>`/`<dashboards>` - Layout coordinates

#### Component 3: Field Name Resolver
**Purpose**: Map natural language to exact Tableau field syntax

**Rules Discovered**:
- **Dimensions**: Use raw bracketed names `[category]`
- **Measures**: Use raw names, Tableau auto-aggregates `[actual_price]`
- **Never guess** aggregation tokens like `[sum:field:qk]` upfront
- **Datasource Declaration**: Must declare in `<view><datasources>` block

#### Component 4: UUID Manager
**Purpose**: Generate unique identifiers for all worksheets/windows

**Implementation**:
```python
import uuid

def generate_tableau_uuid() -> str:
    return f"{{{str(uuid.uuid4()).upper()}}}"
```

**Critical**: Every worksheet and window must have unique UUIDs to avoid `D2E8DA72` errors.

### 2.2 Supported Chart Types (MVP)

| Chart Type | Implementation Strategy |
|------------|------------------------|
| **Bar Chart** | `<rows>[measure]</rows><cols>[dimension]</cols>` |
| **Line Chart** | Same as bar, mark class differs |
| **Area Chart** | Same structure, mark variation |
| **Scatter Plot** | `<rows>[measure1]</rows><cols>[measure2]</cols>` with LOD encoding |
| **Text KPI** | Blank rows/cols, measure in text mark |

**Advanced Features (Phase 2)**:
- Treemaps, Pie charts
- Dual-axis charts
- Dashboard layouts with zones
- Sorting (`<shelf-sorts>`)
- Tooltips/Color/Size encodings

---

## 3. DATA FLOW ARCHITECTURE

### 3.1 End-to-End Pipeline

```
┌──────────────────────────────────────────────────────────────┐
│ USER INPUT                                                   │
│ "Create dashboard: actual price by category"                │
└────────────────────┬─────────────────────────────────────────┘
                     │
                     ▼
┌──────────────────────────────────────────────────────────────┐
│ MCP HOST CLIENT (Claude Desktop / Cursor / Kiro)            │
└────────────────────┬─────────────────────────────────────────┘
                     │ invokes tool
                     ▼
┌──────────────────────────────────────────────────────────────┐
│ CUSTOM TABLEAU MCP SERVER                                    │
│                                                              │
│  Step 1: profile_dataset_schema()                           │
│          ├─► Read CSV metadata (100 rows max)               │
│          └─► Return {dimensions, measures} JSON             │
│                                                              │
│  Step 2: Call Free LLM (Gemini/OpenRouter)                  │
│          ├─► Send: schema + user request                    │
│          └─► Receive: JSON blueprint                        │
│              {                                               │
│                "sheets": [{                                  │
│                  "name": "Sheet1",                           │
│                  "column_field": "category",                 │
│                  "row_field": "actual_price",                │
│                  "mark_type": "Bar"                          │
│                }]                                            │
│              }                                               │
│                                                              │
│  Step 3: compile_workbook()                                  │
│          ├─► Load base_template.twb                         │
│          ├─► Inject datasource references                   │
│          ├─► Generate worksheets with unique UUIDs          │
│          ├─► Sync window declarations                       │
│          └─► Write final .twb file                          │
└────────────────────┬─────────────────────────────────────────┘
                     │
                     ▼
┌──────────────────────────────────────────────────────────────┐
│ OUTPUT: Generated .twb file                                  │
│ User opens in Tableau Desktop                               │
└──────────────────────────────────────────────────────────────┘
```

### 3.2 Error Handling & Validation

#### Error Type 1: XML Schema Violation (Error Code: D2E8DA72)
**Cause**: Structural hierarchy broken (duplicate UUIDs, wrong tag order)
**Prevention**: 
- Unique UUID generation for all elements
- Strict template-based injection
- Pre-validated XML block library

#### Error Type 2: Field Not Found (Error Code: 9CA7205B)
**Cause**: Field name doesn't match datasource
**Prevention**:
- Schema profiling before generation
- Field name validation against datasource metadata
- Raw field names (no premature aggregation tokens)

---

## 4. MCP TOOL DEFINITIONS

### Tool 1: `inspect_dataset_schema`
**Description**: Analyzes dataset structure and returns lightweight metadata

**Input Parameters**:
```json
{
  "file_path": "string (required)",
  "file_type": "string (default: 'csv')"
}
```

**Output**:
```json
{
  "file_name": "string",
  "absolute_path": "string",
  "dimensions": [{"name": "string", "type": "nominal|ordinal"}],
  "measures": [{"name": "string", "type": "quantitative"}],
  "row_count_sample": "integer"
}
```

### Tool 2: `generate_tableau_workbook`
**Description**: Creates complete .twb file from JSON blueprint

**Input Parameters**:
```json
{
  "dataset_path": "string (required)",
  "blueprint": {
    "sheets": [
      {
        "name": "string (required)",
        "column_field": "string (required)",
        "row_field": "string (required)",
        "mark_type": "Bar|Line|Area|Automatic (default: Automatic)",
        "aggregation": "sum|avg|min|max|count|none (default: none)",
        "sort": {
          "direction": "ASC|DESC",
          "by": "string (field name)"
        }
      }
    ]
  },
  "output_path": "string (required)"
}
```

**Output**:
```json
{
  "success": "boolean",
  "workbook_path": "string",
  "sheets_created": "integer",
  "message": "string"
}
```

### Tool 3: `publish_to_tableau_server` (Phase 2)
**Description**: Uploads generated workbook to Tableau Server/Cloud

**Input Parameters**:
```json
{
  "workbook_path": "string (required)",
  "server_url": "string (required)",
  "site_id": "string",
  "project_name": "string (required)",
  "credentials": {
    "token_name": "string",
    "token_value": "string"
  }
}
```

---

## 5. IMPLEMENTATION PHASES

### Phase 1: MVP (Weeks 1-4)
**Goal**: Working proof-of-concept with basic bar charts

**Deliverables**:
1. ✅ Ground-level validation (COMPLETED)
2. Python core framework
   - `schema_profiler.py`
   - `xml_generator.py`
   - `uuid_utils.py`
3. MCP server with 2 tools:
   - `inspect_dataset_schema`
   - `generate_tableau_workbook`
4. Support for:
   - CSV datasets only
   - Bar charts (vertical/horizontal)
   - Single datasource per workbook
   - Local file output

**Success Criteria**:
- Generate valid .twb file that opens in Tableau Desktop
- Handle datasets from 100 rows to 1M+ rows
- Zero XML syntax errors
- Create 3+ sheets in single workbook

### Phase 2: Enhanced Visualizations (Weeks 5-8)
**Additions**:
- Line charts, area charts, scatter plots
- Text KPIs
- Basic sorting and filtering
- Color/size/tooltip encodings
- Dashboard layouts (basic zones)

### Phase 3: Advanced Features (Weeks 9-12)
**Additions**:
- Calculated fields
- LOD expressions
- Dual-axis charts
- Treemaps, pie charts
- Complex dashboard layouts (floating containers)
- Tableau Server publishing

### Phase 4: Enterprise Features (Weeks 13-16)
**Additions**:
- Multi-datasource workbooks
- Data blending
- Parameters and actions
- Live database connections (not just CSV)
- Workbook templates library

---

## 6. TECHNOLOGY STACK

### 6.1 Core Technologies

| Component | Technology | Justification |
|-----------|-----------|---------------|
| **MCP Server** | Python 3.9+ | FastMCP SDK official support |
| **XML Manipulation** | lxml | Safe tree parsing, validation |
| **Schema Analysis** | pandas | Efficient CSV profiling |
| **LLM Integration** | OpenRouter API / Gemini API | Free-tier models (Gemini Flash, Phi, Llama) |
| **MCP SDK** | `mcp.server.fastmcp` | Official Python MCP framework |
| **UUID Generation** | stdlib `uuid` | Built-in, reliable |

### 6.2 Project Structure
```
tableau-mcp-server/
│
├── README.md
├── requirements.txt
├── setup.py
│
├── templates/
│   └── base_blank.twb          # Pristine template file
│
├── src/
│   ├── __init__.py
│   │
│   ├── core/
│   │   ├── __init__.py
│   │   ├── schema_profiler.py  # Dataset metadata extraction
│   │   ├── xml_generator.py    # Safe XML manipulation
│   │   ├── uuid_utils.py       # UUID generation
│   │   └── field_resolver.py   # Natural language → field mapping
│   │
│   ├── mcp/
│   │   ├── __init__.py
│   │   ├── server.py           # FastMCP server definition
│   │   └── tools.py            # MCP tool implementations
│   │
│   └── llm/
│       ├── __init__.py
│       └── client.py           # LLM API integration
│
├── tests/
│   ├── test_schema_profiler.py
│   ├── test_xml_generator.py
│   └── test_integration.py
│
└── examples/
    ├── sample_datasets/
    │   └── amazon.csv
    └── generated_workbooks/
```

---

## 7. RISK ANALYSIS & MITIGATION

### Risk 1: XML Syntax Errors (HIGH)
**Impact**: Generated files fail to open in Tableau
**Mitigation**:
- Use pre-validated template blocks
- Comprehensive test suite with Tableau Desktop validation
- Never allow LLM to write raw XML

### Risk 2: Dataset Scale Issues (MEDIUM)
**Impact**: Memory errors or timeouts with large datasets
**Mitigation**:
- Profile only first 100 rows
- Stream-read large files
- Clear documentation of file size limits

### Risk 3: LLM Hallucination (MEDIUM)
**Impact**: Generated JSON blueprint contains invalid field names
**Mitigation**:
- Schema validation layer
- Field name fuzzy matching
- User confirmation for ambiguous requests

### Risk 4: Tableau Version Compatibility (LOW)
**Impact**: Generated files incompatible with older Tableau versions
**Mitigation**:
- Test across Tableau versions (2020.1+)
- Version declaration in workbook XML
- Compatibility documentation

---

## 8. SUCCESS METRICS

### Phase 1 (MVP)
- ✅ 100% valid .twb file generation rate
- ✅ Support datasets up to 1M rows
- ✅ <5 second workbook generation time
- ✅ Zero syntax errors in generated XML

### Phase 2-3
- Support 8+ chart types
- Dashboard layout generation
- <10 second generation for complex workbooks
- User satisfaction score >4/5

### Phase 4
- Enterprise adoption (10+ organizations)
- Tableau Server integration working
- 50+ template library

---

## 9. COMPETITIVE ANALYSIS

### Official Tableau MCP (Salesforce)
**Focus**: Data consumption (querying, exporting views)
**Gap**: No programmatic dashboard creation

### Our Advantage
**Focus**: Creator workflow acceleration
**Differentiator**: Automated scaffolding and rapid prototyping

---

## 10. GO-TO-MARKET STRATEGY

### Phase 1: Open Source Launch
- GitHub repository with MIT license
- Comprehensive documentation
- Sample datasets and examples
- Blog post: "Automating Tableau with MCP"

### Phase 2: Community Building
- Video tutorials
- Discord/Slack community
- Integration with popular MCP hosts (Claude Desktop, Kiro, Cursor)

### Phase 3: Enterprise Offering
- Premium features (Tableau Server integration)
- Custom template library
- Enterprise support
- SaaS offering consideration

---

## 11. TECHNICAL DEBT & FUTURE CONSIDERATIONS

### Known Limitations (MVP)
1. CSV only (no database connections)
2. Single datasource per workbook
3. Basic chart types only
4. No calculated fields
5. Limited dashboard layout control

### Future Enhancements
1. Support for Tableau Hyper extracts
2. Real-time data source connections
3. AI-powered chart type recommendations
4. Natural language calculated field generation
5. Template marketplace

---

## 12. APPENDICES

### Appendix A: Tableau XML Structure Reference
**Critical Tags**:
- `<datasource>`: Defines data connections and metadata
- `<worksheet>`: Contains visualization logic
- `<dashboard>`: Layout containers and zones
- `<windows>`: UI viewport declarations

### Appendix B: Field Naming Conventions
- **Raw Fields**: `[field_name]`
- **With Datasource**: `[datasource_id].[field_name]`
- **Aggregated** (auto-applied): Tableau adds wrappers internally

### Appendix C: UUID Format
- Tableau format: `{XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXX}`
- Must be uppercase
- Must be unique across all worksheets and windows

---

## DOCUMENT CONTROL

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2026-06-22 | PRD Team | Initial comprehensive requirements |

