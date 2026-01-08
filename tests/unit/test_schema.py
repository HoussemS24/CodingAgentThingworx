"""
Unit tests for schema validation
Tests that specs are properly validated against schema
"""

import pytest
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.schema import SpecValidator, ValidationError, validate_spec


class TestSchemaValidation:
    """Test schema validation"""
    
    def test_valid_spec(self):
        """Test that valid spec passes validation"""
        spec = {
            "version": "1.0.0",
            "metadata": {
                "generated_at": "2025-01-08T10:00:00Z",
                "prompt": "Create a calculator"
            },
            "actions": [
                {
                    "type": "CreateThing",
                    "params": {
                        "name": "Calculator",
                        "thingTemplateName": "GenericThing"
                    }
                }
            ]
        }
        
        validator = SpecValidator()
        # Should not raise exception
        validator.validate(spec)
    
    def test_missing_version(self):
        """Test that spec without version is rejected"""
        spec = {
            "metadata": {
                "generated_at": "2025-01-08T10:00:00Z",
                "prompt": "Test"
            },
            "actions": []
        }
        
        validator = SpecValidator()
        with pytest.raises(ValidationError):
            validator.validate(spec)
    
    def test_missing_metadata(self):
        """Test that spec without metadata is rejected"""
        spec = {
            "version": "1.0.0",
            "actions": []
        }
        
        validator = SpecValidator()
        with pytest.raises(ValidationError):
            validator.validate(spec)
    
    def test_missing_actions(self):
        """Test that spec without actions is rejected"""
        spec = {
            "version": "1.0.0",
            "metadata": {
                "generated_at": "2025-01-08T10:00:00Z",
                "prompt": "Test"
            }
        }
        
        validator = SpecValidator()
        with pytest.raises(ValidationError):
            validator.validate(spec)
    
    def test_empty_actions(self):
        """Test that spec with empty actions array is rejected"""
        spec = {
            "version": "1.0.0",
            "metadata": {
                "generated_at": "2025-01-08T10:00:00Z",
                "prompt": "Test"
            },
            "actions": []
        }
        
        validator = SpecValidator()
        with pytest.raises(ValidationError):
            validator.validate(spec)
    
    def test_invalid_action_type(self):
        """Test that invalid action type is rejected"""
        spec = {
            "version": "1.0.0",
            "metadata": {
                "generated_at": "2025-01-08T10:00:00Z",
                "prompt": "Test"
            },
            "actions": [
                {
                    "type": "InvalidAction",
                    "params": {}
                }
            ]
        }
        
        validator = SpecValidator()
        with pytest.raises(ValidationError):
            validator.validate(spec)
    
    def test_create_thing_valid(self):
        """Test valid CreateThing action"""
        spec = {
            "version": "1.0.0",
            "metadata": {
                "generated_at": "2025-01-08T10:00:00Z",
                "prompt": "Create thing"
            },
            "actions": [
                {
                    "type": "CreateThing",
                    "params": {
                        "name": "MyThing",
                        "thingTemplateName": "GenericThing",
                        "description": "Test thing"
                    }
                }
            ]
        }
        
        validator = SpecValidator()
        validator.validate(spec)
    
    def test_create_thing_missing_name(self):
        """Test that CreateThing without name is rejected"""
        spec = {
            "version": "1.0.0",
            "metadata": {
                "generated_at": "2025-01-08T10:00:00Z",
                "prompt": "Create thing"
            },
            "actions": [
                {
                    "type": "CreateThing",
                    "params": {
                        "thingTemplateName": "GenericThing"
                    }
                }
            ]
        }
        
        validator = SpecValidator()
        with pytest.raises(ValidationError):
            validator.validate(spec)
    
    def test_add_service_valid(self):
        """Test valid AddServiceToThing action"""
        spec = {
            "version": "1.0.0",
            "metadata": {
                "generated_at": "2025-01-08T10:00:00Z",
                "prompt": "Add service"
            },
            "actions": [
                {
                    "type": "AddServiceToThing",
                    "params": {
                        "thingName": "MyThing",
                        "serviceName": "MyService",
                        "serviceCode": "var result = a + b;",
                        "parameters": {
                            "a": "NUMBER",
                            "b": "NUMBER"
                        },
                        "resultType": "NUMBER"
                    }
                }
            ]
        }
        
        validator = SpecValidator()
        validator.validate(spec)
    
    def test_add_service_invalid_parameter_type(self):
        """Test that AddServiceToThing with invalid parameter type is rejected"""
        spec = {
            "version": "1.0.0",
            "metadata": {
                "generated_at": "2025-01-08T10:00:00Z",
                "prompt": "Add service"
            },
            "actions": [
                {
                    "type": "AddServiceToThing",
                    "params": {
                        "thingName": "MyThing",
                        "serviceName": "MyService",
                        "serviceCode": "var result = a;",
                        "parameters": {
                            "a": "INVALID_TYPE"
                        },
                        "resultType": "NUMBER"
                    }
                }
            ]
        }
        
        validator = SpecValidator()
        with pytest.raises(ValidationError):
            validator.validate(spec)
    
    def test_add_service_invalid_result_type(self):
        """Test that AddServiceToThing with invalid result type is rejected"""
        spec = {
            "version": "1.0.0",
            "metadata": {
                "generated_at": "2025-01-08T10:00:00Z",
                "prompt": "Add service"
            },
            "actions": [
                {
                    "type": "AddServiceToThing",
                    "params": {
                        "thingName": "MyThing",
                        "serviceName": "MyService",
                        "serviceCode": "var result = a;",
                        "parameters": {
                            "a": "NUMBER"
                        },
                        "resultType": "INVALID_TYPE"
                    }
                }
            ]
        }
        
        validator = SpecValidator()
        with pytest.raises(ValidationError):
            validator.validate(spec)
    
    def test_rag_sources_optional(self):
        """Test that rag_sources in metadata is optional"""
        spec = {
            "version": "1.0.0",
            "metadata": {
                "generated_at": "2025-01-08T10:00:00Z",
                "prompt": "Test",
                "rag_sources": [
                    {
                        "file": "docs/test.md",
                        "section": "Introduction",
                        "relevance": 0.95
                    }
                ]
            },
            "actions": [
                {
                    "type": "CreateThing",
                    "params": {
                        "name": "Test",
                        "thingTemplateName": "GenericThing"
                    }
                }
            ]
        }
        
        validator = SpecValidator()
        validator.validate(spec)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
