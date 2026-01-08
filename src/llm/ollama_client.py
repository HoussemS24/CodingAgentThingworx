"""
Ollama LLM Client
Local LLM integration using Ollama API
"""

import requests
import json
from typing import Dict, Any, List, Optional


class OllamaClient:
    """
    Client for Ollama local LLM
    Compatible with Ollama API (http://localhost:11434)
    """
    
    def __init__(self, base_url: str = "http://localhost:11434", model: str = "llama3.1:8b"):
        """
        Initialize Ollama client
        
        Args:
            base_url: Ollama server URL
            model: Model name (default: llama3.1:8b)
        """
        self.base_url = base_url.rstrip("/")
        self.model = model
        self.timeout = 300  # 5 minutes for generation
    
    def chat(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.0,
        max_tokens: Optional[int] = None
    ) -> str:
        """
        Chat completion using Ollama
        
        Args:
            messages: List of message dicts with 'role' and 'content'
            temperature: Sampling temperature (0.0 = deterministic)
            max_tokens: Maximum tokens to generate
            
        Returns:
            Generated text response
        """
        endpoint = f"{self.base_url}/api/chat"
        
        payload = {
            "model": self.model,
            "messages": messages,
            "stream": False,
            "options": {
                "temperature": temperature,
            }
        }
        
        if max_tokens:
            payload["options"]["num_predict"] = max_tokens
        
        try:
            response = requests.post(
                endpoint,
                json=payload,
                timeout=self.timeout
            )
            
            if response.status_code != 200:
                raise Exception(f"Ollama API error: {response.status_code} - {response.text}")
            
            result = response.json()
            return result["message"]["content"]
            
        except requests.exceptions.ConnectionError:
            raise Exception(
                f"Cannot connect to Ollama at {self.base_url}. "
                "Make sure Ollama is running: 'ollama serve'"
            )
        except requests.exceptions.Timeout:
            raise Exception(
                f"Ollama request timed out after {self.timeout}s. "
                "Try a smaller prompt or increase timeout."
            )
        except Exception as e:
            raise Exception(f"Ollama client error: {e}")
    
    def generate(
        self,
        prompt: str,
        temperature: float = 0.0,
        max_tokens: Optional[int] = None
    ) -> str:
        """
        Simple text generation
        
        Args:
            prompt: Text prompt
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            
        Returns:
            Generated text
        """
        endpoint = f"{self.base_url}/api/generate"
        
        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": temperature,
            }
        }
        
        if max_tokens:
            payload["options"]["num_predict"] = max_tokens
        
        try:
            response = requests.post(
                endpoint,
                json=payload,
                timeout=self.timeout
            )
            
            if response.status_code != 200:
                raise Exception(f"Ollama API error: {response.status_code} - {response.text}")
            
            result = response.json()
            return result["response"]
            
        except requests.exceptions.ConnectionError:
            raise Exception(
                f"Cannot connect to Ollama at {self.base_url}. "
                "Make sure Ollama is running: 'ollama serve'"
            )
        except Exception as e:
            raise Exception(f"Ollama client error: {e}")
    
    def list_models(self) -> List[str]:
        """
        List available models
        
        Returns:
            List of model names
        """
        endpoint = f"{self.base_url}/api/tags"
        
        try:
            response = requests.get(endpoint, timeout=10)
            
            if response.status_code != 200:
                return []
            
            result = response.json()
            return [model["name"] for model in result.get("models", [])]
            
        except Exception:
            return []
    
    def is_available(self) -> bool:
        """
        Check if Ollama server is available
        
        Returns:
            True if server is reachable
        """
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            return response.status_code == 200
        except Exception:
            return False
    
    def pull_model(self, model_name: str) -> bool:
        """
        Pull a model (download if not available)
        
        Args:
            model_name: Name of model to pull
            
        Returns:
            True if successful
        """
        endpoint = f"{self.base_url}/api/pull"
        
        payload = {
            "name": model_name,
            "stream": False
        }
        
        try:
            response = requests.post(
                endpoint,
                json=payload,
                timeout=600  # 10 minutes for download
            )
            
            return response.status_code == 200
            
        except Exception as e:
            print(f"Failed to pull model: {e}")
            return False
