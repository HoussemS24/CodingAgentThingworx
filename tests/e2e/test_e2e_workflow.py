"""
E2E Test - Complete workflow from spec generation to execution
NOTE: Requires .env file with valid ThingWorx credentials
Skips if .env is not configured
"""

import pytest
import sys
import json
import requests
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.generator import SpecGenerator
from src.executor import Executor
from src.schema import validate_spec
from src.guardrails import validate_spec as validate_guardrails
from src.config import get_config, ConfigError


# Check if .env is configured
def is_env_configured():
    """Check if .env file exists and is properly configured"""
    env_file = Path(__file__).parent.parent.parent / ".env"
    if not env_file.exists():
        return False
    
    try:
        config = get_config()
        # Check for placeholder values
        if "your-app-key-here" in config.app_key:
            return False
        if "your-server" in config.base_url:
            return False
        return True
    except ConfigError:
        return False


@pytest.mark.skipif(not is_env_configured(), reason="No .env file configured")
class TestE2EWorkflow:
    """
    End-to-end tests for complete workflow
    These tests require a running ThingWorx instance
    """
    
    def test_validate_example_spec(self):
        """Test that example spec is valid"""
        spec_file = Path(__file__).parent.parent / "fixtures" / "example_spec.json"
        
        with open(spec_file) as f:
            spec = json.load(f)
        
        # Validate schema
        validate_spec(spec)
        
        # Validate guardrails
        validate_guardrails(spec)
    
    def test_dry_run_execution(self):
        """Test dry run execution of example spec"""
        spec_file = Path(__file__).parent.parent / "fixtures" / "example_spec.json"
        
        with open(spec_file) as f:
            spec = json.load(f)
        
        # Execute in dry run mode
        executor = Executor()
        result = executor.execute_spec(spec, dry_run=True)
        
        assert result["status"] == "dry_run"
        assert result["actions_executed"] == 4
        assert len(result["results"]) == 4
    
    @pytest.mark.integration
    def test_full_execution_and_verification(self):
        """
        Full E2E test: Create Thing, add services, verify they work
        WARNING: This creates actual resources in ThingWorx
        """
        spec_file = Path(__file__).parent.parent / "fixtures" / "example_spec.json"
        
        with open(spec_file) as f:
            spec = json.load(f)
        
        config = get_config()
        
        # Execute spec
        executor = Executor()
        result = executor.execute_spec(spec, dry_run=False)
        
        assert result["status"] == "success", f"Execution failed: {result.get('error')}"
        assert result["actions_executed"] == 4
        
        # Verify Thing exists
        thing_name = "TestCalculator"
        thing_url = f"{config.base_url}/Things/{thing_name}"
        
        response = requests.get(
            thing_url,
            headers=config.get_headers(),
            timeout=config.timeout
        )
        
        assert response.status_code == 200, f"Thing not found: {response.text}"
        
        # Verify and test Add service
        add_url = f"{config.base_url}/Things/{thing_name}/Services/Add"
        
        response = requests.post(
            add_url,
            headers=config.get_headers(),
            json={"a": 5, "b": 3},
            timeout=config.timeout
        )
        
        assert response.status_code == 200, f"Add service failed: {response.text}"
        
        # Parse result
        try:
            add_result = response.json()
            # ThingWorx returns result in different formats, handle both
            if isinstance(add_result, dict):
                actual_result = add_result.get("result", add_result.get("rows", [{}])[0].get("result"))
            else:
                actual_result = add_result
            
            assert actual_result == 8, f"Add service returned wrong result: {actual_result}"
        except Exception as e:
            pytest.fail(f"Failed to parse Add service result: {e}, response: {response.text}")
        
        # Verify and test Multiply service
        multiply_url = f"{config.base_url}/Things/{thing_name}/Services/Multiply"
        
        response = requests.post(
            multiply_url,
            headers=config.get_headers(),
            json={"a": 5, "b": 3},
            timeout=config.timeout
        )
        
        assert response.status_code == 200, f"Multiply service failed: {response.text}"
        
        try:
            multiply_result = response.json()
            if isinstance(multiply_result, dict):
                actual_result = multiply_result.get("result", multiply_result.get("rows", [{}])[0].get("result"))
            else:
                actual_result = multiply_result
            
            assert actual_result == 15, f"Multiply service returned wrong result: {actual_result}"
        except Exception as e:
            pytest.fail(f"Failed to parse Multiply service result: {e}, response: {response.text}")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-m", "not integration"])
