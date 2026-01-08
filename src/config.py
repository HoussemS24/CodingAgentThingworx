"""
Configuration Module
Loads configuration from environment variables (.env file)
"""

import os
from pathlib import Path
from typing import Optional


class ConfigError(Exception):
    """Raised when configuration is invalid or missing"""
    pass


class Config:
    """
    Configuration manager for ThingWorx connection
    Loads from .env file (never committed to git)
    """
    
    def __init__(self):
        self._load_env()
        self._validate()
    
    def _load_env(self) -> None:
        """Load environment variables from .env file"""
        # Find .env file in project root
        project_root = Path(__file__).parent.parent
        env_file = project_root / ".env"
        
        if env_file.exists():
            with open(env_file) as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#"):
                        if "=" in line:
                            key, value = line.split("=", 1)
                            os.environ[key.strip()] = value.strip()
    
    def _validate(self) -> None:
        """Validate required configuration"""
        if not self.app_key:
            raise ConfigError(
                "THINGWORX_APP_KEY not set. "
                "Copy .env.example to .env and set your credentials."
            )
        
        if not self.base_url:
            raise ConfigError(
                "THINGWORX_BASE_URL not set. "
                "Copy .env.example to .env and set your server URL."
            )
        
        # Check for placeholder values
        if self.app_key == "your-app-key-here":
            raise ConfigError(
                "THINGWORX_APP_KEY contains placeholder value. "
                "Please set your actual AppKey in .env file."
            )
        
        if "your-server" in self.base_url:
            raise ConfigError(
                "THINGWORX_BASE_URL contains placeholder value. "
                "Please set your actual server URL in .env file."
            )
    
    @property
    def app_key(self) -> str:
        """Get ThingWorx AppKey"""
        return os.environ.get("THINGWORX_APP_KEY", "")
    
    @property
    def base_url(self) -> str:
        """Get ThingWorx base URL"""
        url = os.environ.get("THINGWORX_BASE_URL", "")
        # Ensure no trailing slash
        return url.rstrip("/")
    
    @property
    def timeout(self) -> int:
        """Get request timeout in seconds"""
        return int(os.environ.get("THINGWORX_TIMEOUT", "30"))
    
    def get_headers(self) -> dict:
        """Get standard HTTP headers for ThingWorx API"""
        return {
            "appKey": self.app_key,
            "Accept": "application/json",
            "Content-Type": "application/json"
        }


# Singleton instance
_config_instance: Optional[Config] = None


def get_config() -> Config:
    """Get or create the singleton config instance"""
    global _config_instance
    if _config_instance is None:
        _config_instance = Config()
    return _config_instance


def reload_config() -> Config:
    """Force reload configuration from environment"""
    global _config_instance
    _config_instance = Config()
    return _config_instance
