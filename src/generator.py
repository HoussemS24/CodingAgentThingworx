"""
Spec Generator Module
Generates ThingWorx specifications from natural language prompts
Uses OpenAI API with deterministic settings
"""

import json
import os
from datetime import datetime
from typing import Dict, Any, Optional, List
from pathlib import Path
from openai import OpenAI
from .rag import RAGEngine


class GenerationError(Exception):
    """Raised when spec generation fails"""
    pass


class SpecGenerator:
    """
    Generates specifications from natural language prompts
    Uses LLM with deterministic settings (temperature 0)
    """
    
    SYSTEM_PROMPT = """You are a ThingWorx automation expert. Generate JSON specifications for ThingWorx operations.

You MUST generate valid JSON that matches this schema:
- version: "1.0.0"
- metadata: {generated_at, prompt, rag_sources (optional)}
- actions: array of action objects

Allowed action types:
- CreateThing: {name, thingTemplateName, description?}
- EnableThing: {thingName}
- AddServiceToThing: {thingName, serviceName, serviceCode, parameters, resultType}
- AddPropertyDefinition: {thingName, name, type, description?}
- SetProperty: {thingName, propertyName, value}
- ExecuteService: {thingName, serviceName, serviceParams?}

CRITICAL RULES:
1. Service code MUST include a header comment with:
   - Service name, creation date, author
   - Description, inputs, outputs
   - Change log
2. Use ServiceHelper.AddServiceToThing for all service creation
3. NEVER use Delete, Reset, or Permission operations
4. Parameter types: STRING, NUMBER, INTEGER, LONG, BOOLEAN, DATETIME, LOCATION, JSON, INFOTABLE
5. Always EnableThing after CreateThing

Generate deterministic, well-structured specs."""
    
    def __init__(self, rag_context: Optional[str] = None, use_rag: bool = True):
        """
        Initialize generator
        
        Args:
            rag_context: Optional RAG-retrieved context to inject
            use_rag: Whether to use RAG for context retrieval
        """
        self.client = OpenAI()  # Uses OPENAI_API_KEY from environment
        self.rag_context = rag_context
        self.use_rag = use_rag
        self.rag_engine = None
        
        # Initialize RAG engine if enabled
        if use_rag:
            kb_path = Path(".kb")
            if kb_path.exists():
                self.rag_engine = RAGEngine(kb_dir=kb_path)
    
    def generate(self, prompt: str, rag_sources: Optional[List[Dict]] = None) -> Dict[str, Any]:
        """
        Generate a specification from a prompt
        
        Args:
            prompt: Natural language description of desired ThingWorx operations
            rag_sources: Optional list of RAG sources used
            
        Returns:
            Generated specification dictionary
        """
        # Retrieve RAG context if enabled and not provided
        if self.use_rag and self.rag_engine and not self.rag_context:
            context, sources = self.rag_engine.get_context(prompt)
            self.rag_context = context
            if not rag_sources:
                rag_sources = sources
        
        # Build user message with optional RAG context
        user_message = self._build_user_message(prompt)
        
        try:
            # Call LLM with deterministic settings
            response = self.client.chat.completions.create(
                model="gpt-4.1-mini",  # Using available model
                messages=[
                    {"role": "system", "content": self.SYSTEM_PROMPT},
                    {"role": "user", "content": user_message}
                ],
                temperature=0,  # Deterministic
                response_format={"type": "json_object"}
            )
            
            # Parse response
            spec_text = response.choices[0].message.content
            spec = json.loads(spec_text)
            
            # Ensure required fields
            if "version" not in spec:
                spec["version"] = "1.0.0"
            
            if "metadata" not in spec:
                spec["metadata"] = {}
            
            spec["metadata"]["generated_at"] = datetime.now().isoformat()
            spec["metadata"]["prompt"] = prompt
            
            if rag_sources:
                spec["metadata"]["rag_sources"] = rag_sources
            
            return spec
            
        except json.JSONDecodeError as e:
            raise GenerationError(f"Failed to parse LLM response as JSON: {e}")
        except Exception as e:
            raise GenerationError(f"Spec generation failed: {e}")
    
    def _build_user_message(self, prompt: str) -> str:
        """Build user message with optional RAG context"""
        if self.rag_context:
            return f"""Context from documentation:
{self.rag_context}

User request:
{prompt}

Generate a JSON specification for this request."""
        else:
            return f"""User request:
{prompt}

Generate a JSON specification for this request."""
    
    def generate_and_save(
        self,
        prompt: str,
        output_dir: Path,
        rag_sources: Optional[List[Dict]] = None
    ) -> Path:
        """
        Generate spec and save to file
        
        Args:
            prompt: Natural language prompt
            output_dir: Directory to save spec
            rag_sources: Optional RAG sources
            
        Returns:
            Path to saved spec file
        """
        spec = self.generate(prompt, rag_sources)
        
        # Create output directory
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Generate filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"spec_{timestamp}.json"
        output_file = output_dir / filename
        
        # Save spec
        with open(output_file, "w") as f:
            json.dump(spec, f, indent=2)
        
        return output_file


def generate_spec(prompt: str, rag_context: Optional[str] = None) -> Dict[str, Any]:
    """
    Convenience function to generate a spec
    
    Args:
        prompt: Natural language prompt
        rag_context: Optional RAG context
        
    Returns:
        Generated specification
    """
    generator = SpecGenerator(rag_context=rag_context)
    return generator.generate(prompt)
