"""
LLM integration for blueprint generation.
Supports OpenRouter and Google Gemini.
"""

import json
import os
from typing import Dict, Optional
from dotenv import load_dotenv

load_dotenv()


class LLMClient:
    """Client for interacting with LLM APIs."""
    
    def __init__(self, provider: str = None):
        """
        Initialize LLM client.
        
        Args:
            provider: "openrouter" or "gemini". Defaults to env variable.
        """
        self.provider = provider or os.getenv("DEFAULT_LLM_PROVIDER", "gemini")
        
        if self.provider == "openrouter":
            self.api_key = os.getenv("OPENROUTER_API_KEY")
            if not self.api_key:
                raise ValueError("OPENROUTER_API_KEY not set in environment")
        elif self.provider == "gemini":
            self.api_key = os.getenv("GEMINI_API_KEY")
            if not self.api_key:
                raise ValueError("GEMINI_API_KEY not set in environment")
        else:
            raise ValueError(f"Unsupported provider: {self.provider}")
    
    def generate_blueprint(self, schema: Dict, user_request: str) -> Dict:
        """
        Generate JSON blueprint from schema and user request.
        
        Args:
            schema: Dataset schema from SchemaProfiler
            user_request: Natural language request from user
            
        Returns:
            dict: JSON blueprint with sheets configuration
        """
        prompt = self._build_prompt(schema, user_request)
        
        if self.provider == "gemini":
            return self._call_gemini(prompt)
        elif self.provider == "openrouter":
            return self._call_openrouter(prompt)
    
    def _build_prompt(self, schema: Dict, user_request: str) -> str:
        """Construct prompt for LLM with chart type and sort intelligence."""

        dimensions_list = [d["name"] for d in schema["dimensions"]]
        measures_list = [m["name"] for m in schema["measures"]]

        prompt = f"""You are a Tableau dashboard generator. Given a dataset schema and user request, generate a JSON blueprint for creating Tableau worksheets.

Dataset Schema:
- Dimensions (categorical / date fields): {', '.join(dimensions_list)}
- Measures (numeric fields): {', '.join(measures_list)}

User Request: {user_request}

## Chart Type Selection Rules

Choose mark_type based on these signals in the user request:

**Bar** (default for categorical comparisons):
- "by category", "compare", "ranking", "top N", "bottom N", "breakdown"

**Line** (continuous data over time, direction, change):
- Keywords: trend, over time, timeline, trajectory, history, historical,
  chronological, fluctuation, spike, dip, seasonal, time-series,
  "by year", "monthly", "quarterly", "daily", "hourly",
  growth rate, momentum, pace, pattern over, evolution of.
- Default when column_field is a date/time dimension.

**Area** (volume, cumulative magnitude, stacked contributions over time):
- Keywords: area under curve, cumulative, volume over time, running total,
  stacked trend, share over time, proportion over time,
  filled, contribution over time.

**Text** (single summary KPI number, no axis):
- Keywords: "KPI", "total", "grand total", "show me the total", "what is the total",
  "display the sum", "summarize", "single number", "big number", "headline metric",
  "scorecard", "how much total", "overall", "all-time", "in total"
- Use when the user wants ONE prominent number, not a chart
- Set column_field to null — no dimension axis needed
- Always include aggregation (Sum, Avg, Count, etc.)
- Optionally include format with number_format for currency/percentage

**Scatter** (measure vs measure, correlation, relationship):
- Keywords: "vs", "versus", "correlation", "relationship between", "scatter",
  "compare X and Y", "price vs cost", "profit vs sales", "X against Y"
- Requires column_field = one measure, row_field = another measure
- Optionally include detail_field (a dimension) for per-row granularity
- Optionally add encodings.color and encodings.shape from a dimension

**Pie** (part-to-whole, share, composition):
- Keywords: "pie", "share", "proportion", "percentage of total", "composition",
  "breakdown of", "contribution", "slice", "how much each", "what percentage"
- Requires color_field = dimension, size_field = measure
- Optionally include label_fields to show values on slices

**BoxPlot** (distribution, spread, outliers, range):
- Keywords: "box plot", "box-whisker", "whisker", "distribution", "spread",
  "outliers", "quartile", "median range", "variability", "dispersion"
- Requires row_field = measure, detail_field = dimension (grouping)

**Histogram** (frequency distribution, bins, count):
- Keywords: "histogram", "frequency", "distribution of", "how many fall",
  "bins", "buckets", "count of values", "value distribution"
- Requires row_field = measure (COUNT will be applied automatically)
- Optionally include bin_size (numeric), color_field = dimension for split

**ComboChart** (bar + line dual measure over time):
- Keywords: "bar and line", "combo", "dual axis", "two measures over time",
  "compare two metrics over", "overlay", "combined chart"
- Requires column_field = date dimension, bar_field = measure, line_field = measure
- Optionally include date_trunc: "Quarter" (default), "Month", "Year"

**Bar** (default for categorical comparisons):
- "by category", "compare", "ranking", "top N", "bottom N", "breakdown"

**Line** (continuous data over time, direction, change):
- Keywords: trend, over time, timeline, trajectory, history, historical,
  chronological, fluctuation, spike, dip, seasonal, time-series,
  "by year", "monthly", "quarterly", "daily", "hourly",
  growth rate, momentum, pace, pattern over, evolution of.
- Default when column_field is a date/time dimension.

**Area** (volume, cumulative magnitude, stacked contributions over time):
- Keywords: area under curve, cumulative, volume over time, running total,
  stacked trend, share over time, proportion over time,
  filled, contribution over time.

**Text** (single summary KPI number, no axis):
- Keywords: "KPI", "total", "grand total", "show me the total", "what is the total",
  "display the sum", "summarize", "single number", "big number", "headline metric",
  "scorecard", "how much total", "overall", "all-time", "in total"
- Use when the user wants ONE prominent number, not a chart
- Set column_field to null — no dimension axis needed
- Always include aggregation (Sum, Avg, Count, etc.)
- Optionally include format with number_format for currency/percentage

**Automatic**: let Tableau decide (use only when intent is unclear).

## Zoom / Viewpoint Selection Rules

Include a "zoom" field on any sheet when the user wants a specific view fit:

- "fit entire view", "fit all", "fit view", "show everything", "entire view" → "entire-view"
- "fit width", "fit to width", "fill width", "wide view" → "fit-width"
- "fit height", "fit to height", "fill height", "tall view" → "fit-height"
- No zoom keyword → omit the "zoom" field entirely (Tableau default = standard 100%)

## Sort Selection Rules

Include a "sort" block when the user asks for ordering:

**Field sort (sort dimension by a measure value)**:
- Keywords: "top N", "bottom N", "highest", "lowest", "most", "least",
  "ranked by", "sorted by", "ordered by", "best", "worst"
- Use direction: "DESC" for top/highest/most/best, "ASC" for lowest/least/worst/bottom

**Alphabetical sort**:
- Keywords: "alphabetically", "A to Z", "Z to A", "alphabetical order"
- Use type: "alphabetical", direction "ASC" or "DESC"

**No sort** (omit the "sort" key entirely):
- When user does not indicate any ordering preference

## Filter Selection Rules

Include a "filters" array when the user wants to restrict data to specific values:

**Categorical filter (exact match)**:
- Keywords: "only", "just", "where", "for", "in", "from", "show only", "filter by",
  "limited to", "specifically", "within"
- Example: "show sales for USA only" → filter region = ["USA"]
- Example: "sales in Electronics and Furniture" → filter category = ["Electronics", "Furniture"]

**No filter** (omit "filters" entirely):
- When user does not mention specific values to include/exclude

## Multi-Dimension Breakdown Rules

When the user lists MORE THAN ONE dimension to break a measure down by, put ALL of those
dimensions in "column_field" as an ARRAY (a JSON list), in the order the user names them.
This creates a single nested/grouped axis — it is NOT the same as color or tooltip encoding.

Trigger signals:
- The user names two or more dimensions joined by "and", commas, "by ... and ...", "across",
  "broken down by", "grouped by", "segmented by".
- Example: "Sales by Region, Product Category and Payment Method"
    → "column_field": ["Region", "Product_Category", "Payment_Method"], "row_field": "Sales_Amount"
- Example: "Profit by Category and Region"
    → "column_field": ["Category", "Region"], "row_field": "Profit"

Important distinctions:
- Use a multi-dimension ARRAY only when the user is listing dimensions to break the measure down by.
- Do NOT silently convert extra dimensions into color/size/tooltip encodings. Only add encodings
  when the user EXPLICITLY uses encoding keywords ("color by", "size by", "show ... in tooltip").
- A single dimension stays a plain string: "column_field": "Region".

## Aggregation Function Selection Rules

Extract the aggregation function keyword from the user request and include "aggregation" in the blueprint:

Keyword Mapping:
- "average", "avg", "mean", "typical" → "Avg"
- "median", "mid", "midpoint", "middle value" → "Median"
- "minimum", "min", "lowest", "least" → "Min"
- "maximum", "max", "highest", "greatest", "most" → "Max"
- "total", "sum", "combined", "altogether" → "Sum" (default)
- "count", "number of", "how many" → "Count"
- "distinct count", "unique count", "unique values" → "CountD"
- "standard deviation", "std dev", "variation" → "StdDev"

Default to "Sum" if no aggregation keyword is detected. Omit the "aggregation" key entirely when defaulting to Sum.

Examples:
- "Average sales by region" → {{"aggregation": "Avg", ...}}
- "Minimum discount by category" → {{"aggregation": "Min", ...}}
- "Count of transactions by month" → {{"aggregation": "Count", ...}}

## Visual Encodings (Story 2.4)

Include an "encodings" object to add color, size, and tooltip visual properties:

**Color Encoding**:
- Keywords: "color by", "colored by", "color-code", "color-coded"
- Example: "sales by category, color by region" → encodings.color = {{"field": "region", "type": "dimension"}}
- Use "type": "dimension" for categorical colors, "type": "measure" for gradient colors
- Optional "palette": "tableau10" (default), "tableau20", or other Tableau palettes

**Size Encoding**:
- Keywords: "size by", "sized by", "bubble", "bubble chart", "size-encoded"
- Example: "bubble chart with size by quantity" → encodings.size = {{"field": "quantity"}}
- Typically used with Circle or Point mark types

**Tooltip Encoding**:
- Keywords: "show", "display", "tooltip", "hover", "on hover"
- Example: "show sales and quantity in tooltip" → encodings.tooltip = ["sales", "quantity"]
- Can be a single field or array of fields to include in hover display

**No encoding** (omit "encodings" entirely):
- When user does not request color, size, or tooltip modifications

## KPI Number Formatting Rules

When mark_type is "Text", include a "format" object with number_format:

Number Format Patterns:
- Currency (dollars): "$#,##0" → shows $1,234
- Currency with cents: "$#,##0.00" → shows $1,234.56
- Percentage: "0.00%" → shows 12.34%
- Plain integer: "#,##0" → shows 1,234
- Decimal: "#,##0.00" → shows 1,234.56

Font sizes for KPIs:
- "large", "big", "prominent", "headline" → font_size: 36
- Default KPI font size → font_size: 24

Keywords that trigger currency format: "revenue", "sales", "profit", "cost", "price", "$"
Keywords that trigger percentage format: "rate", "ratio", "percentage", "%", "share"
Omit "format" entirely when no special formatting is implied.

## Output Format

Return ONLY valid JSON, no explanations:

Regular chart sheet:
{{
  "sheets": [
    {{
      "name": "Descriptive Sheet Name",
      "column_field": "<single dimension field, OR an array of dimension fields for multi-dimension breakdown>",
      "row_field": "<field from measures list>",
      "mark_type": "Bar | Line | Area | Circle | Automatic",
      "aggregation": "Avg | Min | Max | Median | Count | CountD | StdDev",
      "zoom": "entire-view | fit-width | fit-height",
      "sort": {{
        "field": "<measure field to sort by>",
        "direction": "DESC | ASC",
        "type": "field | alphabetical"
      }},
      "filters": [
        {{
          "field": "<dimension field to filter>",
          "operator": "=",
          "values": ["<value1>", "<value2>"]
        }}
      ],
      "encodings": {{
        "color": {{
          "field": "<dimension or measure field>",
          "type": "dimension | measure",
          "palette": "tableau10 | tableau20"
        }},
        "size": {{
          "field": "<measure field>"
        }},
        "tooltip": ["<field1>", "<field2>"]
      }}
    }}
  ]
}}

Scatter plot sheet (measure vs measure):
{{
  "sheets": [
    {{
      "name": "Price vs Cost by Category",
      "mark_type": "Scatter",
      "column_field": "<measure for X axis>",
      "row_field": "<measure for Y axis>",
      "detail_field": "<dimension for per-point granularity>",
      "zoom": "entire-view | fit-width | fit-height",
      "encodings": {{
        "color": {{"field": "<dimension>"}},
        "shape": {{"field": "<dimension>"}}
      }}
    }}
  ]
}}

Pie chart sheet:
{{
  "sheets": [
    {{
      "name": "Sales Share by Region",
      "mark_type": "Pie",
      "color_field": "<dimension for slice identity>",
      "size_field": "<measure for slice size>",
      "label_fields": ["<measure>", "<dimension>"],
      "zoom": "entire-view | fit-width | fit-height"
    }}
  ]
}}

Box-whisker plot sheet:
{{
  "sheets": [
    {{
      "name": "Quantity Distribution by Sales Rep",
      "mark_type": "BoxPlot",
      "row_field": "<measure for distribution>",
      "detail_field": "<dimension for grouping>",
      "zoom": "entire-view | fit-width | fit-height"
    }}
  ]
}}

Histogram sheet:
{{
  "sheets": [
    {{
      "name": "Sales Amount Distribution",
      "mark_type": "Histogram",
      "row_field": "<measure to distribute>",
      "bin_size": 500,
      "color_field": "<dimension to split bars (optional)>",
      "zoom": "entire-view | fit-width | fit-height"
    }}
  ]
}}

Combo bar-line chart sheet:
{{
  "sheets": [
    {{
      "name": "Discount vs Sales by Quarter",
      "mark_type": "ComboChart",
      "column_field": "<date dimension>",
      "date_trunc": "Quarter | Month | Year",
      "bar_field": "<measure for bar>",
      "line_field": "<measure for line>",
      "aggregation": "Sum",
      "zoom": "entire-view | fit-width | fit-height"
    }}
  ]
}}

KPI / Text mark sheet (single summary number):
{{
  "sheets": [
    {{
      "name": "Total Sales KPI",
      "column_field": null,
      "row_field": "<field from measures list>",
      "mark_type": "Text",
      "aggregation": "Sum | Avg | Min | Max | Count",
      "format": {{
        "number_format": "$#,##0 | 0.00% | #,##0",
        "font_size": 24
      }}
    }}
  ]
}}

Note: Omit the "sort" key entirely when no sorting is requested.
Note: Omit the "filters" key entirely when no filtering is requested.
Note: Omit the "encodings" key entirely when no color/size/tooltip is requested.
Note: Omit the "aggregation" key entirely when the default Sum aggregation applies.
Note: For Text/KPI mark type, set column_field to null — the metric is a single number with no axis.
Note: Omit "format" entirely when no special number formatting or font size is implied.
Note: Omit "zoom" entirely when no zoom/fit keyword is used by the user.
Note: Scatter uses column_field and row_field as MEASURES (both from measures list).
Note: Pie uses color_field and size_field (not column_field/row_field).
Note: BoxPlot uses row_field (measure) and detail_field (dimension).
Note: Histogram uses row_field (measure) and optional bin_size and color_field.
Note: ComboChart uses column_field (date dimension), bar_field and line_field (both measures).

Rules:
1. Use ONLY field names from the schema above — never invent fields.
2. column_field comes from the dimensions list (or null for Text/KPI marks, or a MEASURE for Scatter). It may be a single field (string) or an array of dimension fields for a multi-dimension breakdown; every field in the array must come from the appropriate list.
3. row_field must come from the measures list (except Scatter where both axes are measures).
4. sort.field must come from the measures list (for field sort) or dimensions list (for alphabetical).
5. filters[].field must come from the dimensions list.
6. filters[].values must contain actual data values matching the field (use realistic values from sample_values if known).
7. encodings.color.field can be from dimensions (categorical) or measures (gradient).
8. encodings.size.field should be a measure (numeric field).
9. encodings.tooltip fields can be from either dimensions or measures list.
10. Create 1-3 sheets based on what the request asks for.
11. When the request mentions a date/time dimension, prefer Line mark type (or ComboChart if two measures are mentioned).
12. Circle/Point mark types work best with size encoding (bubble charts).
13. Return ONLY the JSON object — no markdown, no commentary.
14. For Text mark type (KPI): column_field must be null, aggregation is required, format is optional.
15. number_format: "$#,##0" for currency, "0.00%" for percentage, "#,##0" for plain integers.
16. For Scatter: both column_field and row_field come from the MEASURES list, not dimensions.
17. For Pie: color_field from dimensions, size_field from measures — do NOT use column_field/row_field.
18. For ComboChart: column_field is a DATE dimension; bar_field and line_field are two different measures.

Generate the blueprint now:"""

        return prompt
    
    def _call_gemini(self, prompt: str) -> Dict:
        """Call Google Gemini API."""
        from google import genai

        client = genai.Client(api_key=self.api_key)
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
        )
        response_text = response.text.strip()
        
        # Extract JSON from response
        try:
            # Try to find JSON in response
            if "```json" in response_text:
                json_start = response_text.find("```json") + 7
                json_end = response_text.find("```", json_start)
                response_text = response_text[json_start:json_end].strip()
            elif "```" in response_text:
                json_start = response_text.find("```") + 3
                json_end = response_text.find("```", json_start)
                response_text = response_text[json_start:json_end].strip()
            
            blueprint = json.loads(response_text)
            return blueprint
        except json.JSONDecodeError as e:
            raise ValueError(f"LLM returned invalid JSON: {response_text[:200]}...")
    
    def _call_openrouter(self, prompt: str) -> Dict:
        """Call OpenRouter API."""
        from openai import OpenAI
        
        client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=self.api_key
        )
        
        response = client.chat.completions.create(
            model="anthropic/claude-3-haiku",  # or other free models
            messages=[{"role": "user", "content": prompt}]
        )
        
        response_text = response.choices[0].message.content.strip()
        
        try:
            # Try to extract JSON from response
            if "```json" in response_text:
                json_start = response_text.find("```json") + 7
                json_end = response_text.find("```", json_start)
                response_text = response_text[json_start:json_end].strip()
            elif "```" in response_text:
                json_start = response_text.find("```") + 3
                json_end = response_text.find("```", json_start)
                response_text = response_text[json_start:json_end].strip()
            
            blueprint = json.loads(response_text)
            return blueprint
        except json.JSONDecodeError:
            raise ValueError(f"LLM returned invalid JSON: {response_text[:200]}...")
