"""
App Executor - Handles ThingWorx Application creation and management
"""

import json
import requests
from typing import Dict, Any, List
from ..config import get_config


class AppExecutor:
    """
    Executes Application-related operations in ThingWorx
    """
    
    def __init__(self):
        """Initialize App executor"""
        self.config = get_config()
    
    def create_application(
        self,
        name: str,
        description: str = "",
        home_mashup: str = None,
        menu_items: List[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """
        Create a new Application in ThingWorx
        
        Args:
            name: Application name
            description: Application description
            home_mashup: Home mashup name (optional)
            menu_items: List of menu items with title and mashup
            
        Returns:
            Result dictionary
        """
        # Build application configuration
        app_config = {
            "name": name,
            "description": description,
            "homeMashup": home_mashup or "",
            "menuItems": menu_items or []
        }
        
        # Create Application via EntityServices
        url = f"{self.config.base_url}/Resources/EntityServices/Services/CreateApplication"
        
        payload = {
            "name": name,
            "description": description,
            "thingTemplateName": "Application"
        }
        
        response = requests.post(
            url,
            headers=self.config.get_headers(),
            json=payload,
            timeout=self.config.timeout
        )
        
        if response.status_code not in [200, 201]:
            raise Exception(f"Failed to create Application: {response.status_code} - {response.text}")
        
        # Set home mashup if provided
        if home_mashup:
            self._set_home_mashup(name, home_mashup)
        
        # Add menu items if provided
        if menu_items:
            for item in menu_items:
                self._add_menu_item(name, item)
        
        return {
            "status": "success",
            "app_name": name,
            "message": f"Application '{name}' created successfully"
        }
    
    def _set_home_mashup(self, app_name: str, mashup_name: str) -> None:
        """Set the home mashup for an application"""
        url = f"{self.config.base_url}/Things/{app_name}/Services/SetHomeMashup"
        
        payload = {
            "mashupName": mashup_name
        }
        
        response = requests.post(
            url,
            headers=self.config.get_headers(),
            json=payload,
            timeout=self.config.timeout
        )
        
        if response.status_code not in [200, 201]:
            raise Exception(f"Failed to set home mashup: {response.status_code} - {response.text}")
    
    def _add_menu_item(self, app_name: str, menu_item: Dict[str, str]) -> None:
        """Add a menu item to an application"""
        url = f"{self.config.base_url}/Things/{app_name}/Services/AddMenuItem"
        
        payload = {
            "title": menu_item.get("title", "Menu Item"),
            "mashupName": menu_item.get("mashup", ""),
            "description": menu_item.get("description", "")
        }
        
        response = requests.post(
            url,
            headers=self.config.get_headers(),
            json=payload,
            timeout=self.config.timeout
        )
        
        if response.status_code not in [200, 201]:
            # Not critical if menu item fails
            print(f"Warning: Failed to add menu item: {response.status_code}")
    
    def update_application(
        self,
        name: str,
        description: str = None,
        home_mashup: str = None
    ) -> Dict[str, Any]:
        """
        Update an existing Application
        
        Args:
            name: Application name
            description: New description (optional)
            home_mashup: New home mashup (optional)
            
        Returns:
            Result dictionary
        """
        # Update description if provided
        if description:
            url = f"{self.config.base_url}/Things/{name}/Services/SetDescription"
            
            payload = {
                "description": description
            }
            
            response = requests.post(
                url,
                headers=self.config.get_headers(),
                json=payload,
                timeout=self.config.timeout
            )
            
            if response.status_code not in [200, 201]:
                raise Exception(f"Failed to update description: {response.status_code}")
        
        # Update home mashup if provided
        if home_mashup:
            self._set_home_mashup(name, home_mashup)
        
        return {
            "status": "success",
            "app_name": name,
            "message": f"Application '{name}' updated successfully"
        }
    
    def enable_application(self, name: str) -> Dict[str, Any]:
        """
        Enable an Application
        
        Args:
            name: Application name
            
        Returns:
            Result dictionary
        """
        url = f"{self.config.base_url}/Things/{name}/Services/EnableThing"
        
        response = requests.post(
            url,
            headers=self.config.get_headers(),
            timeout=self.config.timeout
        )
        
        if response.status_code not in [200, 201]:
            raise Exception(f"Failed to enable Application: {response.status_code} - {response.text}")
        
        return {
            "status": "success",
            "app_name": name,
            "message": f"Application '{name}' enabled"
        }
    
    def delete_application(self, name: str) -> Dict[str, Any]:
        """
        Delete an Application (for idempotency)
        
        Args:
            name: Application name
            
        Returns:
            Result dictionary
        """
        url = f"{self.config.base_url}/Things/{name}"
        
        response = requests.delete(
            url,
            headers=self.config.get_headers(),
            timeout=self.config.timeout
        )
        
        # 404 is OK (already deleted)
        if response.status_code not in [200, 204, 404]:
            raise Exception(f"Failed to delete Application: {response.status_code} - {response.text}")
        
        return {
            "status": "success",
            "app_name": name,
            "message": f"Application '{name}' deleted"
        }
    
    def create_full_app(
        self,
        app_name: str,
        description: str,
        mashups: List[Dict[str, Any]],
        things: List[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Create a complete application with Things, Mashups, and App entity
        
        Args:
            app_name: Application name
            description: Application description
            mashups: List of mashup definitions
            things: List of thing definitions (optional)
            
        Returns:
            Result dictionary with all created entities
        """
        from .executor import Executor
        from .mashup_executor import MashupExecutor
        
        results = {
            "app_name": app_name,
            "things_created": [],
            "mashups_created": [],
            "app_created": False
        }
        
        # Create Things if provided
        if things:
            executor = Executor()
            for thing in things:
                try:
                    result = executor._create_thing(thing)
                    results["things_created"].append(thing["name"])
                    
                    # Enable thing
                    executor._enable_thing({"thingName": thing["name"]})
                except Exception as e:
                    print(f"Warning: Failed to create Thing {thing.get('name')}: {e}")
        
        # Create Mashups
        mashup_executor = MashupExecutor()
        home_mashup = None
        menu_items = []
        
        for idx, mashup in enumerate(mashups):
            try:
                mashup_name = mashup.get("name", f"{app_name}_Mashup{idx+1}")
                mashup_desc = mashup.get("description", "")
                mashup_content = mashup.get("content", {})
                
                mashup_executor.create_mashup(mashup_name, mashup_desc, mashup_content)
                results["mashups_created"].append(mashup_name)
                
                # First mashup is home mashup
                if idx == 0:
                    home_mashup = mashup_name
                
                # Add to menu
                menu_items.append({
                    "title": mashup.get("title", f"View {idx+1}"),
                    "mashup": mashup_name,
                    "description": mashup_desc
                })
                
            except Exception as e:
                print(f"Warning: Failed to create Mashup {mashup.get('name')}: {e}")
        
        # Create Application
        try:
            self.create_application(
                name=app_name,
                description=description,
                home_mashup=home_mashup,
                menu_items=menu_items
            )
            
            # Enable application
            self.enable_application(app_name)
            
            results["app_created"] = True
            
        except Exception as e:
            raise Exception(f"Failed to create Application: {e}")
        
        return results
