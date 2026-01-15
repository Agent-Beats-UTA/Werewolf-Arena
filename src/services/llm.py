import os
from google import genai
from pydantic import BaseModel
from typing import Optional, Any

class LLM(BaseModel):
    model_config = {"arbitrary_types_allowed": True}

    model: str = "gemini-2.0-flash"
    _client: Optional[Any] = None

    @property
    def client(self) -> genai.Client:
        if self._client is None:
            api_key = os.getenv("GEMINI_API_KEY")
            if not api_key:
                raise ValueError("GEMINI_API_KEY environment variable not set")
            self._client = genai.Client(api_key=api_key)
        return self._client

    def execute_prompt(self, prompt: str) -> str:
        response = self.client.models.generate_content(
            model=self.model,
            contents=prompt
        )
        return response.text
        
        