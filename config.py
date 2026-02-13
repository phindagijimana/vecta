"""
Med42 Service Configuration Management
Centralized configuration using Pydantic for type safety and validation
"""

import os
from typing import Optional
from pydantic_settings import BaseSettings


class Med42Config(BaseSettings):
    """Configuration settings for Med42 service"""

    # Application settings
    app_home: str = os.environ.get("APP_HOME", os.getcwd())
    service_port: int = int(os.environ.get("SERVICE_PORT", "8080"))
    service_host: str = os.environ.get("SERVICE_HOST", "0.0.0.0")
    max_concurrent_users: int = int(os.environ.get("MAX_CONCURRENT_USERS", "10"))

    # Model settings
    model_name: str = os.environ.get("MODEL_NAME", "m42-health/Llama3-Med42-8B")
    device: Optional[str] = None

    # File upload settings
    upload_folder: str = ""
    max_content_length: int = 50 * 1024 * 1024  # 50MB
    allowed_extensions: set = {"txt", "pdf", "docx", "xlsx", "xls", "csv", "json"}

    # Logging settings
    log_level: str = os.environ.get("LOG_LEVEL", "INFO")
    log_dir: str = ""

    # Security settings
    secret_key: str = os.urandom(24).hex()
    enable_phi_filtering: bool = True
    audit_log_enabled: bool = True

    # Performance settings
    model_cache_dir: Optional[str] = None
    enable_model_pooling: bool = False

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # Derive computed paths
        self.upload_folder = os.path.join(self.app_home, "uploads")
        self.log_dir = os.path.join(self.app_home, "logs")
        self.model_cache_dir = os.path.join(self.app_home, "model_cache")

        # Determine device
        if self.device is None:
            try:
                import torch
                self.device = "cuda" if torch.cuda.is_available() else "cpu"
            except ImportError:
                self.device = "cpu"

    class Config:
        env_prefix = "MED42_"
        case_sensitive = False


# Global configuration instance
config = Med42Config()
