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

**Automatic**: let Tableau decide (use only when intent is unclear).

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

## Output Format

Return ONLY valid JSON, no explanations:
{{
  "sheets": [
    {{
      "name": "Descriptive Sheet Name",
      "column_field": "<field from dimensions list>",
      "row_field": "<field from measures list>",
      "mark_type": "Bar | Line | Area | Automatic",
      "sort": {{
        "field": "<measure field to sort by>",
        "direction": "DESC | ASC",
        "type": "field | alphabetical"
      }}
    }}
  ]
}}

Note: Omit the "sort" key entirely when no sorting is requested.

Rules:
1. Use ONLY field names from the schema above — never invent fields.
2. column_field must come from the dimensions list.
3. row_field must come from the measures list.
4. sort.field must come from the measures list (for field sort) or dimensions list (for alphabetical).
5. Create 1-3 sheets based on what the request asks for.
6. When the request mentions a date/time dimension, prefer Line mark type.
7. Return ONLY the JSON object — no markdown, no commentary.

Generate the blueprint now:"""

        return prompt
    
    def _call_gemini(self, prompt: str) -> Dict:
        """Call Google Gemini API."""
        import google.generativeai as genai
        
        genai.configure(api_key=self.api_key)
        model = genai.GenerativeModel('gemini-2.5-flash')
        
        response = model.generate_content(prompt)
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
