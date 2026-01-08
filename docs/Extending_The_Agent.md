# How to Add a New Action/Capability

This guide outlines the steps required to add a new action to the ThingWorx Coding Agent. Adding a new action involves updating the schema, guardrails, executor, and tests to ensure the new capability is integrated safely and reliably.

Let's use the example of adding a `RestartThing` action.

## 1. Update the JSON Schema

First, you need to allow the new action in the `spec.schema.json` file. This ensures that specifications containing the new action can be validated.

**File**: `src/schema/spec.schema.json`

1.  **Add to Enum**: Add the new action name (`RestartThing`) to the `enum` list under `actions.items.properties.type`.

    ```json
    "type": {
      "type": "string",
      "enum": [
        "CreateThing",
        "UpdateThing",
        "EnableThing",
        "AddServiceToThing",
        "AddPropertyDefinition",
        "SetProperty",
        "ExecuteService",
        "RestartThing" // Add new action here
      ],
      "description": "Action type - only safe operations allowed"
    },
    ```

2.  **Define Parameters**: Add a new conditional block under `allOf` to define the required parameters for your new action.

    ```json
    {
      "if": {
        "properties": {
          "type": {
            "const": "RestartThing"
          }
        }
      },
      "then": {
        "properties": {
          "params": {
            "required": ["thingName"],
            "properties": {
              "thingName": {
                "type": "string"
              }
            }
          }
        }
      }
    }
    ```

## 2. Update the Guardrails

Next, update the guardrails to explicitly allow the new action. This is a critical security step.

**File**: `src/guardrails/guardrails.py`

1.  **Add to Allowlist**: Add the action name to the `ALLOWED_ACTIONS` set.

    ```python
    class Guardrails:
        ALLOWED_ACTIONS: Set[str] = {
            "CreateThing",
            "UpdateThing",
            "EnableThing",
            "AddServiceToThing",
            "AddPropertyDefinition",
            "SetProperty",
            "ExecuteService",
            "RestartThing"  # Add new action here
        }
    ```

If the action corresponds to a new or sensitive endpoint, you might also need to review the `BLOCKED_ENDPOINT_PATTERNS` to ensure it doesn't get blocked by mistake.

## 3. Implement the Executor Logic

Now, implement the logic that performs the action by calling the ThingWorx REST API.

**File**: `src/executor/executor.py`

1.  **Create Handler Method**: Add a new private method to the `Executor` class to handle the action. This method should take the `params` dictionary as an argument.

    ```python
    def _restart_thing(self, params: Dict) -> Dict[str, Any]:
        """Restart a Thing"""
        thing_name = params["thingName"]
        endpoint = f"{self.config.base_url}/Things/{thing_name}/Services/RestartThing"
        
        # Validate the endpoint with guardrails
        validate_endpoint(endpoint)
        
        response = requests.post(
            endpoint,
            headers=self.config.get_headers(),
            timeout=self.config.timeout
        )
        
        if response.status_code not in [200, 201]:
            raise ExecutionError(
                f"RestartThing failed: {response.status_code} - {response.text}"
            )
        
        self._log_success(f"Restarted Thing: {thing_name}")
        return {"status": "success", "thing_name": thing_name}
    ```

2.  **Map Action to Handler**: Add the new action and its handler method to the `handlers` dictionary in the `_execute_action` method.

    ```python
    def _execute_action(self, action_type: str, params: Dict) -> Dict[str, Any]:
        # ...
        handlers = {
            "CreateThing": self._create_thing,
            "UpdateThing": self._update_thing,
            "EnableThing": self._enable_thing,
            "AddServiceToThing": self._add_service_to_thing,
            "AddPropertyDefinition": self._add_property_definition,
            "SetProperty": self._set_property,
            "ExecuteService": self._execute_service,
            "RestartThing": self._restart_thing  # Add new mapping here
        }
        # ...
    ```

## 4. Update the LLM System Prompt

To enable the LLM to generate the new action, you must update its system prompt with information about the new capability.

**File**: `src/generator.py`

1.  **Add to Action List**: Add the new action and its parameters to the `SYSTEM_PROMPT` string in the `SpecGenerator` class.

    ```python
    class SpecGenerator:
        SYSTEM_PROMPT = """You are a ThingWorx automation expert. ...

    Allowed action types:
    - CreateThing: {name, thingTemplateName, description?}
    - EnableThing: {thingName}
    - AddServiceToThing: {thingName, serviceName, serviceCode, parameters, resultType}
    - AddPropertyDefinition: {thingName, name, type, description?}
    - SetProperty: {thingName, propertyName, value}
    - ExecuteService: {thingName, serviceName, serviceParams?}
    - RestartThing: {thingName}  # Add new action here

    CRITICAL RULES:
    ..."""
    ```

## 5. Write Tests

Finally, add tests to ensure the new action works as expected and is handled correctly by the validation and guardrail systems.

### Unit Tests

-   **Guardrails Test**: Add a test to `tests/unit/test_guardrails.py` to confirm the action is in the `ALLOWED_ACTIONS` set.
-   **Schema Test**: Add a test to `tests/unit/test_schema.py` to validate a spec containing the new `RestartThing` action.

### E2E Test

-   **Workflow Test**: If possible, add or update a test in `tests/e2e/test_e2e_workflow.py` to include the new action in a full workflow and verify its effect on the ThingWorx instance.

    For example, you could add a step to restart the `TestCalculator` Thing and check that it remains available.

By following these steps, you can safely and effectively extend the capabilities of the ThingWorx Coding Agent.
