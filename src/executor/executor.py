"""
Executor Module - Executes ThingWorx REST API calls
Implements all allowed actions with proper error handling and logging
"""

import json
import requests
from datetime import datetime
from typing import Dict, Any, List, Optional
from pathlib import Path

from ..config import get_config
from ..guardrails import validate_action_type, validate_endpoint, validate_service_code


class ExecutionError(Exception):
    """Raised when execution of an action fails"""
    pass


class Executor:
    """
    Executes ThingWorx operations via REST API
    All operations are logged for audit trail
    """
    
    def __init__(self, log_dir: Optional[Path] = None):
        self.config = get_config()
        self.log_dir = log_dir or Path("artifacts/logs")
        self.log_dir.mkdir(parents=True, exist_ok=True)
        self.current_log: List[Dict[str, Any]] = []
    
    def execute_spec(self, spec: Dict, dry_run: bool = False) -> Dict[str, Any]:
        """
        Execute a complete specification
        
        Args:
            spec: The specification dictionary
            dry_run: If True, only validate and log planned actions without execution
            
        Returns:
            Execution result with status and logs
        """
        timestamp = datetime.now().isoformat()
        log_file = self.log_dir / f"{timestamp.replace(':', '-')}.log"
        
        self.current_log = []
        results = []
        
        try:
            actions = spec.get("actions", [])
            
            for idx, action in enumerate(actions):
                action_type = action["type"]
                params = action["params"]
                description = action.get("description", "")
                
                self._log_action(
                    f"Action {idx + 1}/{len(actions)}: {action_type}",
                    params,
                    dry_run=dry_run
                )
                
                if dry_run:
                    result = {"status": "dry_run", "action": action_type, "params": params}
                else:
                    result = self._execute_action(action_type, params)
                
                results.append(result)
            
            execution_result = {
                "status": "success" if not dry_run else "dry_run",
                "timestamp": timestamp,
                "spec_metadata": spec.get("metadata", {}),
                "actions_executed": len(results),
                "results": results,
                "log_file": str(log_file)
            }
            
        except Exception as e:
            execution_result = {
                "status": "error",
                "timestamp": timestamp,
                "error": str(e),
                "results": results,
                "log_file": str(log_file)
            }
            self._log_error(str(e))
        
        # Write log file
        self._write_log(log_file, execution_result)
        
        return execution_result
    
    def _execute_action(self, action_type: str, params: Dict) -> Dict[str, Any]:
        """
        Execute a single action
        
        Args:
            action_type: Type of action to execute
            params: Action parameters
            
        Returns:
            Action result
        """
        # Validate action type with guardrails
        validate_action_type(action_type)
        
        # Route to appropriate handler
        handlers = {
            "CreateThing": self._create_thing,
            "UpdateThing": self._update_thing,
            "EnableThing": self._enable_thing,
            "AddServiceToThing": self._add_service_to_thing,
            "AddPropertyDefinition": self._add_property_definition,
            "SetProperty": self._set_property,
            "ExecuteService": self._execute_service
        }
        
        handler = handlers.get(action_type)
        if not handler:
            raise ExecutionError(f"No handler for action type: {action_type}")
        
        return handler(params)
    
    def _create_thing(self, params: Dict) -> Dict[str, Any]:
        """Create a new Thing"""
        endpoint = f"{self.config.base_url}/Resources/EntityServices/Services/CreateThing"
        validate_endpoint(endpoint)
        
        payload = {
            "name": params["name"],
            "thingTemplateName": params.get("thingTemplateName", "GenericThing")
        }
        
        if "description" in params:
            payload["description"] = params["description"]
        
        response = requests.post(
            endpoint,
            headers=self.config.get_headers(),
            json=payload,
            timeout=self.config.timeout
        )
        
        if response.status_code not in [200, 201]:
            raise ExecutionError(
                f"CreateThing failed: {response.status_code} - {response.text}"
            )
        
        self._log_success(f"Created Thing: {params['name']}")
        return {"status": "success", "thing_name": params["name"]}
    
    def _update_thing(self, params: Dict) -> Dict[str, Any]:
        """Update Thing configuration"""
        thing_name = params["thingName"]
        endpoint = f"{self.config.base_url}/Things/{thing_name}"
        validate_endpoint(endpoint)
        
        # Get current config
        response = requests.get(
            endpoint,
            headers=self.config.get_headers(),
            timeout=self.config.timeout
        )
        
        if response.status_code != 200:
            raise ExecutionError(
                f"Failed to get Thing config: {response.status_code} - {response.text}"
            )
        
        config = response.json()
        
        # Update fields
        if "description" in params:
            config["description"] = params["description"]
        
        # Put updated config
        response = requests.put(
            endpoint,
            headers=self.config.get_headers(),
            json=config,
            timeout=self.config.timeout
        )
        
        if response.status_code not in [200, 201]:
            raise ExecutionError(
                f"UpdateThing failed: {response.status_code} - {response.text}"
            )
        
        self._log_success(f"Updated Thing: {thing_name}")
        return {"status": "success", "thing_name": thing_name}
    
    def _enable_thing(self, params: Dict) -> Dict[str, Any]:
        """Enable a Thing"""
        thing_name = params["thingName"]
        endpoint = f"{self.config.base_url}/Things/{thing_name}/Services/EnableThing"
        validate_endpoint(endpoint)
        
        response = requests.post(
            endpoint,
            headers=self.config.get_headers(),
            timeout=self.config.timeout
        )
        
        if response.status_code not in [200, 201]:
            raise ExecutionError(
                f"EnableThing failed: {response.status_code} - {response.text}"
            )
        
        self._log_success(f"Enabled Thing: {thing_name}")
        return {"status": "success", "thing_name": thing_name}
    
    def _add_service_to_thing(self, params: Dict) -> Dict[str, Any]:
        """Add a service to a Thing using ServiceHelper"""
        thing_name = params["thingName"]
        service_name = params["serviceName"]
        service_code = params["serviceCode"]
        
        # Validate service code with guardrails
        validate_service_code(service_code)
        
        endpoint = f"{self.config.base_url}/Things/ServiceHelper/Services/AddServiceToThing"
        validate_endpoint(endpoint)
        
        payload = {
            "thingName": thing_name,
            "serviceName": service_name,
            "serviceCode": service_code,
            "parameters": params.get("parameters", {}),
            "resultType": params.get("resultType", "STRING")
        }
        
        response = requests.post(
            endpoint,
            headers=self.config.get_headers(),
            json=payload,
            timeout=self.config.timeout
        )
        
        if response.status_code not in [200, 201]:
            raise ExecutionError(
                f"AddServiceToThing failed: {response.status_code} - {response.text}"
            )
        
        self._log_success(f"Added service '{service_name}' to Thing '{thing_name}'")
        return {
            "status": "success",
            "thing_name": thing_name,
            "service_name": service_name
        }
    
    def _add_property_definition(self, params: Dict) -> Dict[str, Any]:
        """Add a property definition to a Thing"""
        thing_name = params["thingName"]
        endpoint = f"{self.config.base_url}/Things/{thing_name}/Services/AddPropertyDefinition"
        validate_endpoint(endpoint)
        
        payload = {
            "name": params["name"],
            "type": params["type"]
        }
        
        if "description" in params:
            payload["description"] = params["description"]
        
        response = requests.post(
            endpoint,
            headers=self.config.get_headers(),
            json=payload,
            timeout=self.config.timeout
        )
        
        if response.status_code not in [200, 201]:
            raise ExecutionError(
                f"AddPropertyDefinition failed: {response.status_code} - {response.text}"
            )
        
        self._log_success(f"Added property '{params['name']}' to Thing '{thing_name}'")
        return {
            "status": "success",
            "thing_name": thing_name,
            "property_name": params["name"]
        }
    
    def _set_property(self, params: Dict) -> Dict[str, Any]:
        """Set a property value"""
        thing_name = params["thingName"]
        property_name = params["propertyName"]
        value = params["value"]
        
        endpoint = f"{self.config.base_url}/Things/{thing_name}/Properties/*"
        validate_endpoint(endpoint)
        
        payload = {property_name: value}
        
        response = requests.put(
            endpoint,
            headers=self.config.get_headers(),
            json=payload,
            timeout=self.config.timeout
        )
        
        if response.status_code not in [200, 201]:
            raise ExecutionError(
                f"SetProperty failed: {response.status_code} - {response.text}"
            )
        
        self._log_success(f"Set property '{property_name}' on Thing '{thing_name}'")
        return {
            "status": "success",
            "thing_name": thing_name,
            "property_name": property_name
        }
    
    def _execute_service(self, params: Dict) -> Dict[str, Any]:
        """Execute a service on a Thing"""
        thing_name = params["thingName"]
        service_name = params["serviceName"]
        service_params = params.get("serviceParams", {})
        
        endpoint = f"{self.config.base_url}/Things/{thing_name}/Services/{service_name}"
        validate_endpoint(endpoint)
        
        response = requests.post(
            endpoint,
            headers=self.config.get_headers(),
            json=service_params,
            timeout=self.config.timeout
        )
        
        if response.status_code not in [200, 201]:
            raise ExecutionError(
                f"ExecuteService failed: {response.status_code} - {response.text}"
            )
        
        result = response.json() if response.text else {}
        
        self._log_success(f"Executed service '{service_name}' on Thing '{thing_name}'")
        return {
            "status": "success",
            "thing_name": thing_name,
            "service_name": service_name,
            "result": result
        }
    
    def _log_action(self, message: str, params: Dict, dry_run: bool = False) -> None:
        """Log an action"""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "level": "INFO",
            "message": message,
            "params": params,
            "dry_run": dry_run
        }
        self.current_log.append(log_entry)
    
    def _log_success(self, message: str) -> None:
        """Log a success message"""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "level": "SUCCESS",
            "message": message
        }
        self.current_log.append(log_entry)
    
    def _log_error(self, message: str) -> None:
        """Log an error message"""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "level": "ERROR",
            "message": message
        }
        self.current_log.append(log_entry)
    
    def _write_log(self, log_file: Path, execution_result: Dict) -> None:
        """Write execution log to file"""
        log_data = {
            "execution_result": execution_result,
            "detailed_log": self.current_log
        }
        
        with open(log_file, "w") as f:
            json.dump(log_data, f, indent=2)
