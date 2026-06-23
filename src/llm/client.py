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
        """Construct prompt for LLM."""
        
        dimensions_list = [d["name"] for d in schema["dimensions"]]
        measures_list = [m["name"] for m in schema["measures"]]
        
        prompt = f"""You are a Tableau dashboard generator. Given a dataset schema and user request, generate a JSON blueprint for creating Tableau worksheets.

Dataset Schema:
- Dimensions (categorical fields): {', '.join(dimensions_list)}
- Measures (numeric fields): {', '.join(measures_list)}

User Request: {user_request}

Generate a JSON blueprint following this EXACT format (no additional text):
{{
  "sheets": [
    {{
      "name": "Sheet 1",
      "column_field": "<choose dimension>",
      "row_field": "<choose measure>",
      "mark_type": "Bar"
    }}
  ]
}}

Rules:
1. Use ONLY field names from the schema above
2. column_field should be a dimension
3. row_field should be a measure
4. mark_type can be: Bar, Line, Area, or Automatic
5. Create 1-3 sheets based on the request
6. Return ONLY valid JSON, no explanations

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
