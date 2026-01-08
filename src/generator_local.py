"""
Local Spec Generator - Uses Ollama LLM instead of OpenAI
Generates ThingWorx specifications from natural language prompts
"""

import json
import os
from datetime import datetime
from typing import Dict, Any, Optional, List
from pathlib import Path

from .llm import OllamaClient
from .rag import LocalRAGEngine


class GenerationError(Exception):
    """Raised when spec generation fails"""
    pass


class LocalSpecGenerator:
    """
    Generates ThingWorx specifications using local Ollama LLM
    Supports RAG for context injection
    """
    
    SYSTEM_PROMPT = """You are a ThingWorx automation expert. Generate JSON specifications for ThingWorx operations.

Output ONLY valid JSON in this exact format:
{
  "version": "1.0.0",
  "metadata": {
    "generated_at": "ISO8601 timestamp",
    "prompt": "original user prompt"
  },
  "actions": [
    {
      "type": "ActionType",
      "params": {...},
      "description": "what this action does"
    }
  ]
}

Allowed action types:
- CreateThing: {name, thingTemplateName, description?}
- EnableThing: {thingName}
- AddServiceToThing: {thingName, serviceName, serviceCode, parameters, resultType}
- AddPropertyDefinition: {thingName, name, type, description?}
- SetProperty: {thingName, propertyName, value}
- ExecuteService: {thingName, serviceName, serviceParams?}
- CreateMashup: {name, description, content}
- UpdateMashup: {name, content}

CRITICAL RULES:
1. Use ServiceHelper.AddServiceToThing for ALL service creation
2. Service code MUST include proper header with Service name, Created date, Description, Inputs, Output, Change Log
3. Service code MUST end with 'var result = ...' to return value
4. Parameters format: {"paramName": "TYPE"} where TYPE is NUMBER, STRING, BOOLEAN, JSON, etc.
5. Always EnableThing after CreateThing

Generate deterministic, well-structured specs."""
    
    def __init__(
        self,
        ollama_url: str = "http://localhost:11434",
        model: str = "llama3.1:8b",
        use_rag: bool = True
    ):
        """
        Initialize local generator
        
        Args:
            ollama_url: Ollama server URL
            model: Model name
            use_rag: Whether to use RAG for context retrieval
        """
        self.client = OllamaClient(base_url=ollama_url, model=model)
        self.use_rag = use_rag
        self.rag_engine = None
        
        # Initialize RAG engine if enabled
        if use_rag:
            kb_path = Path(".kb_local")
            if kb_path.exists():
                self.rag_engine = LocalRAGEngine(kb_dir=kb_path)
    
    def generate(self, prompt: str, rag_sources: Optional[List[Dict]] = None) -> Dict[str, Any]:
        """
        Generate a specification from a prompt
        
        Args:
            prompt: Natural language description of desired ThingWorx operations
            rag_sources: Optional list of RAG sources used
            
        Returns:
            Generated specification dictionary
        """
        # Retrieve RAG context if enabled
        rag_context = None
        if self.use_rag and self.rag_engine:
            rag_context, sources = self.rag_engine.get_context(prompt)
            if not rag_sources:
                rag_sources = sources
        
        # Build user message with optional RAG context
        user_message = self._build_user_message(prompt, rag_context)
        
        try:
            # Call LLM with deterministic settings
            messages = [
                {"role": "system", "content": self.SYSTEM_PROMPT},
                {"role": "user", "content": user_message}
            ]
            
            response_text = self.client.chat(
                messages=messages,
                temperature=0.0  # Deterministic
            )
            
            # Parse JSON response
            spec = self._parse_response(response_text)
            
            # Add RAG sources to metadata if available
            if rag_sources:
                spec["metadata"]["rag_sources"] = rag_sources
            
            return spec
            
        except Exception as e:
            raise GenerationError(f"Failed to generate spec: {e}")
    
    def _build_user_message(self, prompt: str, rag_context: Optional[str] = None) -> str:
        """Build user message with optional RAG context"""
        if rag_context:
            return f"""CONTEXT (from documentation):
{rag_context}

USER REQUEST:
{prompt}

Generate a JSON specification for this request using the context above."""
        else:
            return prompt
    
    def _parse_response(self, response_text: str) -> Dict[str, Any]:
        """
        Parse LLM response and extract JSON spec
        
        Args:
            response_text: Raw LLM response
            
        Returns:
            Parsed specification dictionary
        """
        # Try to find JSON in response
        # LLMs sometimes wrap JSON in markdown code blocks
        json_match = None
        
        # Try to extract from code block
        if "```json" in response_text:
            start = response_text.find("```json") + 7
            end = response_text.find("```", start)
            if end > start:
                json_match = response_text[start:end].strip()
        elif "```" in response_text:
            start = response_text.find("```") + 3
            end = response_text.find("```", start)
            if end > start:
                json_match = response_text[start:end].strip()
        else:
            # Try to find JSON directly
            json_match = response_text.strip()
        
        if not json_match:
            raise GenerationError("No JSON found in LLM response")
        
        try:
            spec = json.loads(json_match)
        except json.JSONDecodeError as e:
            raise GenerationError(f"Invalid JSON in response: {e}\n\nResponse:\n{json_match}")
        
        # Validate basic structure
        if "version" not in spec:
            spec["version"] = "1.0.0"
        
        if "metadata" not in spec:
            spec["metadata"] = {}
        
        if "generated_at" not in spec["metadata"]:
            spec["metadata"]["generated_at"] = datetime.utcnow().isoformat() + "Z"
        
        if "actions" not in spec:
            raise GenerationError("Spec missing 'actions' field")
        
        return spec
    
    def check_ollama_status(self) -> Dict[str, Any]:
        """
        Check Ollama server status
        
        Returns:
            Status dictionary with availability and models
        """
        available = self.client.is_available()
        models = self.client.list_models() if available else []
        
        return {
            "available": available,
            "url": self.client.base_url,
            "model": self.client.model,
            "models_available": models
        }
