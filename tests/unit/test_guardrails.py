"""
Unit tests for guardrails module
Tests that blocked actions are properly rejected
"""

import pytest
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.guardrails import (
    Guardrails,
    GuardrailViolation,
    validate_action_type,
    validate_endpoint,
    validate_service_code,
    validate_spec
)


class TestGuardrails:
    """Test guardrails enforcement"""
    
    def test_allowed_actions(self):
        """Test that allowed actions pass validation"""
        guardrails = Guardrails()
        
        allowed = [
            "CreateThing",
            "UpdateThing",
            "EnableThing",
            "AddServiceToThing",
            "AddPropertyDefinition",
            "SetProperty",
            "ExecuteService"
        ]
        
        for action in allowed:
            # Should not raise exception
            guardrails.validate_action_type(action)
    
    def test_blocked_actions(self):
        """Test that blocked actions are rejected"""
        guardrails = Guardrails()
        
        blocked = [
            "DeleteThing",
            "DeleteEntity",
            "ResetThing",
            "PurgeThing",
            "SetPermissions",
            "GrantAccess",
            "RevokeAccess"
        ]
        
        for action in blocked:
            with pytest.raises(GuardrailViolation):
                guardrails.validate_action_type(action)
    
    def test_unknown_action(self):
        """Test that unknown actions are rejected"""
        guardrails = Guardrails()
        
        with pytest.raises(GuardrailViolation):
            guardrails.validate_action_type("UnknownAction")
    
    def test_blocked_endpoints(self):
        """Test that blocked endpoint patterns are rejected"""
        guardrails = Guardrails()
        
        blocked_endpoints = [
            "/Things/MyThing/Services/DeleteThing",
            "/Things/MyThing/Services/RemoveProperty",
            "/Things/MyThing/Services/PurgeThing",
            "/Things/MyThing/Services/ResetThing",
            "/Things/MyThing/Permissions/SetPermissions",
            "/Things/MyThing/Services/GrantAccess"
        ]
        
        for endpoint in blocked_endpoints:
            with pytest.raises(GuardrailViolation):
                guardrails.validate_endpoint(endpoint)
    
    def test_allowed_endpoints(self):
        """Test that allowed endpoints pass validation"""
        guardrails = Guardrails()
        
        allowed_endpoints = [
            "/Things/MyThing/Services/EnableThing",
            "/Things/ServiceHelper/Services/AddServiceToThing",
            "/Resources/EntityServices/Services/CreateThing",
            "/Things/MyThing/Properties/MyProperty"
        ]
        
        for endpoint in allowed_endpoints:
            # Should not raise exception
            guardrails.validate_endpoint(endpoint)
    
    def test_blocked_code_patterns(self):
        """Test that blocked code patterns are rejected"""
        guardrails = Guardrails()
        
        blocked_codes = [
            "me.DeleteThing();",
            "Resources['EntityServices'].DeleteEntity({name: 'MyThing'});",
            "Things['MyThing'].SetPermissions({permissions: {}});",
            "me.GrantAccess({user: 'test'});",
            "Resources['ContentLoaderFunctions'].DeleteJSON({url: 'test'});"
        ]
        
        for code in blocked_codes:
            with pytest.raises(GuardrailViolation):
                guardrails.validate_service_code(code)
    
    def test_allowed_code(self):
        """Test that allowed code passes validation"""
        guardrails = Guardrails()
        
        allowed_codes = [
            "var result = a + b;",
            "me.EnableThing();",
            "var value = me.MyProperty;",
            "logger.info('Processing...');",
            "var data = Things['OtherThing'].GetData();"
        ]
        
        for code in allowed_codes:
            # Should not raise exception
            guardrails.validate_service_code(code)
    
    def test_spec_validation_success(self):
        """Test that valid spec passes validation"""
        guardrails = Guardrails()
        
        spec = {
            "version": "1.0.0",
            "metadata": {
                "generated_at": "2025-01-08T10:00:00",
                "prompt": "Create a calculator"
            },
            "actions": [
                {
                    "type": "CreateThing",
                    "params": {
                        "name": "Calculator",
                        "thingTemplateName": "GenericThing"
                    }
                },
                {
                    "type": "EnableThing",
                    "params": {
                        "thingName": "Calculator"
                    }
                },
                {
                    "type": "AddServiceToThing",
                    "params": {
                        "thingName": "Calculator",
                        "serviceName": "Add",
                        "serviceCode": "var result = a + b;",
                        "parameters": {"a": "NUMBER", "b": "NUMBER"},
                        "resultType": "NUMBER"
                    }
                }
            ]
        }
        
        # Should not raise exception
        guardrails.validate_spec(spec)
    
    def test_spec_validation_blocked_action(self):
        """Test that spec with blocked action is rejected"""
        guardrails = Guardrails()
        
        spec = {
            "version": "1.0.0",
            "metadata": {
                "generated_at": "2025-01-08T10:00:00",
                "prompt": "Delete a thing"
            },
            "actions": [
                {
                    "type": "DeleteThing",
                    "params": {
                        "thingName": "Calculator"
                    }
                }
            ]
        }
        
        with pytest.raises(GuardrailViolation):
            guardrails.validate_spec(spec)
    
    def test_spec_validation_blocked_code(self):
        """Test that spec with blocked code is rejected"""
        guardrails = Guardrails()
        
        spec = {
            "version": "1.0.0",
            "metadata": {
                "generated_at": "2025-01-08T10:00:00",
                "prompt": "Create service"
            },
            "actions": [
                {
                    "type": "AddServiceToThing",
                    "params": {
                        "thingName": "Calculator",
                        "serviceName": "BadService",
                        "serviceCode": "me.DeleteThing();",
                        "parameters": {},
                        "resultType": "NOTHING"
                    }
                }
            ]
        }
        
        with pytest.raises(GuardrailViolation):
            guardrails.validate_spec(spec)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
