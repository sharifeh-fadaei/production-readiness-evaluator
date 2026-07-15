import os
import requests
from typing import Optional, Dict, Any
from dotenv import load_dotenv

load_dotenv()

class OpenRouterClient:
    """OpenRouter LLM client with flexible model selection"""
    
    def __init__(self, model: str = "openai/gpt-4-turbo", api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("OPENROUTER_API_KEY")
        self.model = model
        self.base_url = "https://openrouter.ai/api/v1"
        
        if not self.api_key:
            print("WARNING: OPENROUTER_API_KEY not set. Using mock mode for testing.")
            self.api_key = "mock-key-for-testing"
    
    def call(self, prompt: str, system_prompt: str = None, temperature: float = 0.7) -> str:
        """Call OpenRouter API"""
        
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "HTTP-Referer": "https://github.com/sharifeh-fadaei/production-readiness-evaluator",
            "X-Title": "Production Readiness Evaluator",
        }
        
        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": 1000,
        }
        
        response = requests.post(
            f"{self.base_url}/chat/completions",
            headers=headers,
            json=payload,
            timeout=30
        )
        
        if response.status_code != 200:
            raise Exception(f"OpenRouter API error: {response.status_code} - {response.text}")
        
        data = response.json()
        return data["choices"][0]["message"]["content"]
    
    def get_available_models(self) -> list:
        """List of common models available on OpenRouter"""
        return [
            "openai/gpt-4-turbo",
            "openai/gpt-4",
            "openai/gpt-3.5-turbo",
            "anthropic/claude-3-opus",
            "anthropic/claude-3-sonnet",
            "anthropic/claude-3-haiku",
            "google/palm-2",
            "mistralai/mistral-large",
        ]