"""
Mashup Executor - Handles Mashup creation and updates in ThingWorx
"""

import json
import requests
from typing import Dict, Any
from ..config import get_config


class MashupExecutor:
    """
    Executes Mashup-related operations in ThingWorx
    """
    
    def __init__(self):
        """Initialize Mashup executor"""
        self.config = get_config()
    
    def create_mashup(self, name: str, description: str, content: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a new Mashup in ThingWorx
        
        Args:
            name: Mashup name
            description: Mashup description
            content: Mashup content (UI structure)
            
        Returns:
            Result dictionary
        """
        # Build mashup content structure
        mashup_content = {
            "UI": content.get("UI", self._get_default_ui()),
            "Events": content.get("Events", []),
            "mashupType": "mashup"
        }
        
        # Build payload
        payload = {
            "entityType": "Mashups",
            "name": name,
            "description": description,
            "mashupContent": json.dumps(mashup_content),
            "projectName": content.get("projectName", "PTCDefaultProject")
        }
        
        # Create Mashup via REST API
        url = f"{self.config.base_url}/Mashups?Content-Type=application%2Fjson"
        
        response = requests.put(
            url,
            headers=self.config.get_headers(),
            json=payload,
            timeout=self.config.timeout
        )
        
        if response.status_code not in [200, 201]:
            raise Exception(f"Failed to create Mashup: {response.status_code} - {response.text}")
        
        return {
            "status": "success",
            "mashup_name": name,
            "message": f"Mashup '{name}' created successfully"
        }
    
    def update_mashup(self, name: str, content: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update an existing Mashup
        
        Args:
            name: Mashup name
            content: New mashup content
            
        Returns:
            Result dictionary
        """
        # Get existing mashup
        get_url = f"{self.config.base_url}/Mashups/{name}"
        
        response = requests.get(
            get_url,
            headers=self.config.get_headers(),
            timeout=self.config.timeout
        )
        
        if response.status_code != 200:
            raise Exception(f"Mashup '{name}' not found: {response.status_code}")
        
        # Update content
        mashup_content = {
            "UI": content.get("UI", self._get_default_ui()),
            "Events": content.get("Events", []),
            "mashupType": "mashup"
        }
        
        # Use UpdateMashupContent service
        update_url = f"{self.config.base_url}/Mashups/{name}/Services/UpdateMashupContent"
        
        update_payload = {
            "mashupContent": json.dumps(mashup_content)
        }
        
        response = requests.post(
            update_url,
            headers=self.config.get_headers(),
            json=update_payload,
            timeout=self.config.timeout
        )
        
        if response.status_code not in [200, 201]:
            raise Exception(f"Failed to update Mashup: {response.status_code} - {response.text}")
        
        return {
            "status": "success",
            "mashup_name": name,
            "message": f"Mashup '{name}' updated successfully"
        }
    
    def delete_mashup(self, name: str) -> Dict[str, Any]:
        """
        Delete a Mashup (for idempotency)
        
        Args:
            name: Mashup name
            
        Returns:
            Result dictionary
        """
        url = f"{self.config.base_url}/Mashups/{name}"
        
        response = requests.delete(
            url,
            headers=self.config.get_headers(),
            timeout=self.config.timeout
        )
        
        # 404 is OK (already deleted)
        if response.status_code not in [200, 204, 404]:
            raise Exception(f"Failed to delete Mashup: {response.status_code} - {response.text}")
        
        return {
            "status": "success",
            "mashup_name": name,
            "message": f"Mashup '{name}' deleted"
        }
    
    def _get_default_ui(self) -> Dict[str, Any]:
        """
        Get default UI structure for a Mashup
        
        Returns:
            Default UI structure
        """
        return {
            "Properties": {
                "Id": "mashup-root",
                "Type": "mashup",
                "ResponsiveLayout": True,
                "Width": 1024,
                "Height": 618,
                "Style": "DefaultMashupStyle",
                "StyleTheme": "PTC Convergence Theme",
                "Title": "Default Mashup",
                "Area": "Mashup",
                "__TypeDisplayName": "Mashup",
                "Visible": True,
                "Z-index": 10,
                "Top": 0,
                "Left": 0
            },
            "Widgets": [
                {
                    "Properties": {
                        "Id": "root-container",
                        "Type": "flexcontainer",
                        "flex-direction": "column",
                        "align-items": "center",
                        "justify-content": "center",
                        "flex-grow": 1,
                        "ResponsiveLayout": True
                    },
                    "Widgets": [
                        {
                            "Properties": {
                                "Id": "label-1",
                                "Type": "ptcslabel",
                                "Text": "Welcome to ThingWorx",
                                "font-size": "24px",
                                "font-weight": "bold"
                            }
                        }
                    ]
                }
            ]
        }
    
    def generate_simple_mashup_content(
        self,
        title: str,
        widgets: list = None
    ) -> Dict[str, Any]:
        """
        Generate a simple Mashup content structure
        
        Args:
            title: Mashup title
            widgets: List of widget definitions
            
        Returns:
            Mashup content dictionary
        """
        if widgets is None:
            widgets = []
        
        return {
            "UI": {
                "Properties": {
                    "Id": "mashup-root",
                    "Type": "mashup",
                    "ResponsiveLayout": True,
                    "Width": 1024,
                    "Height": 618,
                    "Style": "DefaultMashupStyle",
                    "StyleTheme": "PTC Convergence Theme",
                    "Title": title,
                    "Area": "Mashup",
                    "__TypeDisplayName": "Mashup",
                    "Visible": True,
                    "Z-index": 10,
                    "Top": 0,
                    "Left": 0
                },
                "Widgets": [
                    {
                        "Properties": {
                            "Id": "root-container",
                            "Type": "flexcontainer",
                            "flex-direction": "column",
                            "align-items": "center",
                            "justify-content": "flex-start",
                            "flex-grow": 1,
                            "ResponsiveLayout": True,
                            "padding": "20px"
                        },
                        "Widgets": widgets
                    }
                ]
            },
            "Events": []
        }
