"""
Guardrails Module - Security and Safety Controls
Enforces constraints: no destructive actions, no permission escalation
"""

from typing import Dict, List, Set
import re


class GuardrailViolation(Exception):
    """Raised when a guardrail constraint is violated"""
    pass


class Guardrails:
    """
    Enforces security and safety constraints on ThingWorx operations
    """
    
    # Allowed action types (whitelist)
    ALLOWED_ACTIONS: Set[str] = {
        "CreateThing",
        "UpdateThing",
        "EnableThing",
        "AddServiceToThing",
        "AddPropertyDefinition",
        "SetProperty",
        "ExecuteService"
    }
    
    # Explicitly blocked actions (blacklist)
    BLOCKED_ACTIONS: Set[str] = {
        "DeleteThing",
        "DeleteEntity",
        "DeletePropertyDefinition",
        "DeleteServiceDefinition",
        "ResetThing",
        "PurgeThing",
        "SetPermissions",
        "AddPermission",
        "RemovePermission",
        "GrantAccess",
        "RevokeAccess",
        "SetVisibility",
        "DeleteProject",
        "DeleteMashup",
        "DeleteDataShape",
        "DeleteThingTemplate",
        "DeleteThingShape"
    }
    
    # Blocked endpoint patterns (regex)
    BLOCKED_ENDPOINT_PATTERNS: List[str] = [
        r".*/Delete.*",
        r".*/Remove.*",
        r".*/Purge.*",
        r".*/Reset.*",
        r".*/Permissions/.*",
        r".*/SetPermissions.*",
        r".*/GrantAccess.*",
        r".*/RevokeAccess.*"
    ]
    
    # Blocked code patterns in service code
    BLOCKED_CODE_PATTERNS: List[str] = [
        r"DeleteThing",
        r"DeleteEntity",
        r"SetPermissions",
        r"GrantAccess",
        r"RevokeAccess",
        r"Resources\[.*\]\.Delete",
        r"Resources\[.*\]\.Purge",
        r"Resources\[.*\]\.Reset"
    ]
    
    def __init__(self):
        self.compiled_endpoint_patterns = [
            re.compile(pattern, re.IGNORECASE) 
            for pattern in self.BLOCKED_ENDPOINT_PATTERNS
        ]
        self.compiled_code_patterns = [
            re.compile(pattern, re.IGNORECASE) 
            for pattern in self.BLOCKED_CODE_PATTERNS
        ]
    
    def validate_action_type(self, action_type: str) -> None:
        """
        Validate that action type is allowed
        
        Args:
            action_type: The action type to validate
            
        Raises:
            GuardrailViolation: If action is not allowed
        """
        if action_type in self.BLOCKED_ACTIONS:
            raise GuardrailViolation(
                f"Action '{action_type}' is explicitly blocked (destructive/permission operation)"
            )
        
        if action_type not in self.ALLOWED_ACTIONS:
            raise GuardrailViolation(
                f"Action '{action_type}' is not in the allowlist. "
                f"Allowed actions: {', '.join(sorted(self.ALLOWED_ACTIONS))}"
            )
    
    def validate_endpoint(self, endpoint: str) -> None:
        """
        Validate that endpoint does not match blocked patterns
        
        Args:
            endpoint: The REST endpoint to validate
            
        Raises:
            GuardrailViolation: If endpoint matches a blocked pattern
        """
        for pattern in self.compiled_endpoint_patterns:
            if pattern.search(endpoint):
                raise GuardrailViolation(
                    f"Endpoint '{endpoint}' matches blocked pattern '{pattern.pattern}'"
                )
    
    def validate_service_code(self, code: str) -> None:
        """
        Validate that service code does not contain blocked patterns
        
        Args:
            code: The service code to validate
            
        Raises:
            GuardrailViolation: If code contains blocked patterns
        """
        for pattern in self.compiled_code_patterns:
            match = pattern.search(code)
            if match:
                raise GuardrailViolation(
                    f"Service code contains blocked pattern '{pattern.pattern}': '{match.group()}'"
                )
    
    def validate_spec(self, spec: Dict) -> None:
        """
        Validate entire specification against all guardrails
        
        Args:
            spec: The specification dictionary to validate
            
        Raises:
            GuardrailViolation: If any guardrail is violated
        """
        if "actions" not in spec:
            raise GuardrailViolation("Spec must contain 'actions' field")
        
        for idx, action in enumerate(spec["actions"]):
            action_type = action.get("type")
            if not action_type:
                raise GuardrailViolation(f"Action {idx} missing 'type' field")
            
            # Validate action type
            self.validate_action_type(action_type)
            
            # Validate service code if present
            if action_type == "AddServiceToThing":
                params = action.get("params", {})
                service_code = params.get("serviceCode", "")
                if service_code:
                    self.validate_service_code(service_code)
    
    def get_allowed_actions(self) -> List[str]:
        """Return list of allowed action types"""
        return sorted(self.ALLOWED_ACTIONS)
    
    def get_blocked_actions(self) -> List[str]:
        """Return list of blocked action types"""
        return sorted(self.BLOCKED_ACTIONS)


# Singleton instance
_guardrails_instance = Guardrails()


def validate_action_type(action_type: str) -> None:
    """Convenience function to validate action type"""
    _guardrails_instance.validate_action_type(action_type)


def validate_endpoint(endpoint: str) -> None:
    """Convenience function to validate endpoint"""
    _guardrails_instance.validate_endpoint(endpoint)


def validate_service_code(code: str) -> None:
    """Convenience function to validate service code"""
    _guardrails_instance.validate_service_code(code)


def validate_spec(spec: Dict) -> None:
    """Convenience function to validate entire spec"""
    _guardrails_instance.validate_spec(spec)


def get_guardrails() -> Guardrails:
    """Get the singleton guardrails instance"""
    return _guardrails_instance
