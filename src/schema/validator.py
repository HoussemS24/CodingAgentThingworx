"""
Schema Validator Module
Validates specifications against spec.schema.json
"""

import json
from pathlib import Path
from typing import Dict, Any
import jsonschema
from jsonschema import Draft7Validator


class ValidationError(Exception):
    """Raised when spec validation fails"""
    pass


class SpecValidator:
    """
    Validates specifications against the JSON schema
    Fail fast approach - validation happens before execution
    """
    
    def __init__(self, schema_path: Path = None):
        if schema_path is None:
            schema_path = Path(__file__).parent / "spec.schema.json"
        
        self.schema_path = schema_path
        self.schema = self._load_schema()
        self.validator = Draft7Validator(self.schema)
    
    def _load_schema(self) -> Dict[str, Any]:
        """Load the JSON schema"""
        if not self.schema_path.exists():
            raise ValidationError(f"Schema file not found: {self.schema_path}")
        
        with open(self.schema_path) as f:
            return json.load(f)
    
    def validate(self, spec: Dict[str, Any]) -> None:
        """
        Validate a specification against the schema
        
        Args:
            spec: The specification dictionary to validate
            
        Raises:
            ValidationError: If validation fails
        """
        try:
            self.validator.validate(spec)
        except jsonschema.ValidationError as e:
            # Format error message for better readability
            error_path = " -> ".join(str(p) for p in e.path) if e.path else "root"
            raise ValidationError(
                f"Validation error at '{error_path}': {e.message}"
            )
        except jsonschema.SchemaError as e:
            raise ValidationError(f"Schema error: {e.message}")
    
    def validate_file(self, spec_file: Path) -> None:
        """
        Validate a specification file
        
        Args:
            spec_file: Path to the specification JSON file
            
        Raises:
            ValidationError: If validation fails
        """
        if not spec_file.exists():
            raise ValidationError(f"Spec file not found: {spec_file}")
        
        with open(spec_file) as f:
            spec = json.load(f)
        
        self.validate(spec)
    
    def get_errors(self, spec: Dict[str, Any]) -> list:
        """
        Get all validation errors without raising exception
        
        Args:
            spec: The specification dictionary to validate
            
        Returns:
            List of error messages
        """
        errors = []
        for error in self.validator.iter_errors(spec):
            error_path = " -> ".join(str(p) for p in error.path) if error.path else "root"
            errors.append(f"At '{error_path}': {error.message}")
        return errors


# Singleton instance
_validator_instance = None


def get_validator() -> SpecValidator:
    """Get or create the singleton validator instance"""
    global _validator_instance
    if _validator_instance is None:
        _validator_instance = SpecValidator()
    return _validator_instance


def validate_spec(spec: Dict[str, Any]) -> None:
    """Convenience function to validate a spec"""
    get_validator().validate(spec)


def validate_spec_file(spec_file: Path) -> None:
    """Convenience function to validate a spec file"""
    get_validator().validate_file(spec_file)
