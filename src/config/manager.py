import json
import yaml
from pathlib import Path
from typing import Dict, Any, Optional

class ConfigManager:
    """
    Centralized configuration manager for the AI Employee system
    """
    def __init__(self, config_path: str = "config.json"):
        self.config_path = Path(config_path)
        self.config = self.load_config()

    def load_config(self) -> Dict[str, Any]:
        """
        Load configuration from file, create default if it doesn't exist
        """
        if self.config_path.exists():
            with open(self.config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        else:
            # Create default configuration
            default_config = self.get_default_config()
            self.save_config(default_config)
            return default_config

    def get_default_config(self) -> Dict[str, Any]:
        """
        Get default configuration values
        """
        import os

        return {
            "vault_path": os.getenv("OBSIDIAN_VAULT_PATH", "obsidian_vault"),
            "check_interval": {
                "gmail": int(os.getenv("GMAIL_CHECK_INTERVAL", "120")),  # seconds
                "whatsapp": int(os.getenv("WHATSAPP_CHECK_INTERVAL", "30")),  # seconds
                "filesystem": int(os.getenv("FILESYSTEM_CHECK_INTERVAL", "10")),  # seconds
                "calendar": int(os.getenv("CALENDAR_CHECK_INTERVAL", "300")),  # seconds
                "orchestrator": int(os.getenv("ORCHESTRATOR_CHECK_INTERVAL", "60"))  # seconds
            },
            "watchdog": {
                "check_interval": int(os.getenv("WATCHDOG_CHECK_INTERVAL", "60")),
                "auto_restart": os.getenv("WATCHDOG_AUTO_RESTART", "true").lower() == "true"
            },
            "gmail": {
                "credentials_path": os.getenv("GMAIL_CREDENTIALS_PATH", "gmail_credentials.json"),
                "monitor_filters": ["is:unread is:important"]
            },
            "whatsapp": {
                "session_path": os.getenv("WHATSAPP_SESSION_PATH", "~/.whatsapp_session"),
                "keywords": ["urgent", "asap", "invoice", "payment", "help", "emergency", "critical", "important"]
            },
            "linkedin": {
                "session_path": os.getenv("LINKEDIN_SESSION_PATH", "~/.linkedin_session"),
                "keywords": ["urgent", "asap", "meeting", "proposal", "opportunity", "help", "important", "follow", "contact"],
                "check_interval": int(os.getenv("LINKEDIN_CHECK_INTERVAL", "300"))  # seconds
            },
            "calendar": {
                "sync_enabled": os.getenv("CALENDAR_SYNC_ENABLED", "false").lower() == "true",
                "providers": ["google", "outlook"],  # Supported providers
                "default_provider": os.getenv("CALENDAR_DEFAULT_PROVIDER", "google"),
                "sync_frequency_minutes": int(os.getenv("CALENDAR_SYNC_FREQUENCY", "15")),
                "create_tasks_for_events": os.getenv("CALENDAR_CREATE_TASKS_FOR_EVENTS", "true").lower() == "true"
            },
            "silver_tier_features": {
                "enable_analytics": os.getenv("ENABLE_ANALYTICS", "true").lower() == "true",
                "enable_learning": os.getenv("ENABLE_LEARNING", "true").lower() == "true",
                "enable_advanced_monitoring": os.getenv("ENABLE_ADVANCED_MONITORING", "true").lower() == "true",
                "enable_predictive_features": os.getenv("ENABLE_PREDICTIVE_FEATURES", "true").lower() == "true",
                "enable_calendar_integration": os.getenv("ENABLE_CALENDAR_INTEGRATION", "false").lower() == "true"
            },
            "gold_tier_features": {
                "enable_advanced_ai": os.getenv("ENABLE_ADVANCED_AI", "true").lower() == "true",
                "enable_strategic_insights": os.getenv("ENABLE_STRATEGIC_INSIGHTS", "true").lower() == "true",
                "enable_collaboration_engine": os.getenv("ENABLE_COLLABORATION_ENGINE", "true").lower() == "true",
                "enable_bi_reporting": os.getenv("ENABLE_BI_REPORTING", "true").lower() == "true"
            },
            "api": {
                "host": os.getenv("API_HOST", "localhost"),
                "port": int(os.getenv("API_PORT", "8000")),
                "workers": int(os.getenv("API_WORKERS", "4")),
                "cors_origins": os.getenv("CORS_ORIGINS", "*").split(",")
            },
            "database": {
                "url": os.getenv("DATABASE_URL", "sqlite:///silver_tier.db"),
                "pool_size": int(os.getenv("DB_POOL_SIZE", "20")),
                "pool_overflow": int(os.getenv("DB_POOL_OVERFLOW", "10")),
                "echo": os.getenv("DB_ECHO", "false").lower() == "true"
            },
            "security": {
                "require_approval_for": [
                    "payments",
                    "emails_to_new_contacts",
                    "file_sharing",
                    "access_changes",
                    "confidential_info"
                ],
                "approval_threshold": int(os.getenv("APPROVAL_THRESHOLD", "100"))
            },
            "logging": {
                "level": os.getenv("LOG_LEVEL", "INFO"),
                "file_logging": os.getenv("LOG_FILE_LOGGING", "true").lower() == "true",
                "log_retention_days": int(os.getenv("LOG_RETENTION_DAYS", "30")),
                "structured_logging": os.getenv("STRUCTURED_LOGGING", "true").lower() == "true"
            },
            "mcp_servers": {
                "email_mcp": {
                    "enabled": os.getenv("EMAIL_MCP_ENABLED", "true").lower() == "true",
                    "port": int(os.getenv("EMAIL_MCP_PORT", "8080")),
                    "host": os.getenv("EMAIL_MCP_HOST", "localhost")
                },
                "browser_mcp": {
                    "enabled": os.getenv("BROWSER_MCP_ENABLED", "true").lower() == "true",
                    "port": int(os.getenv("BROWSER_MCP_PORT", "8081")),
                    "host": os.getenv("BROWSER_MCP_HOST", "localhost")
                }
            },
            "integrations": {
                "calendar_enabled": os.getenv("CALENDAR_INTEGRATION_ENABLED", "false").lower() == "true",
                "crm_enabled": os.getenv("CRM_ENABLED", "false").lower() == "true",
                "project_management_enabled": os.getenv("PROJECT_MANAGEMENT_ENABLED", "false").lower() == "true",
                "gmail_enabled": os.getenv("GMAIL_ENABLED", "true").lower() == "true",
                "whatsapp_enabled": os.getenv("WHATSAPP_ENABLED", "true").lower() == "true",
                "linkedin_enabled": os.getenv("LINKEDIN_ENABLED", "true").lower() == "true"
            },
            # Global configuration for Platinum Tier
            "global": {
                "region": os.getenv("GLOBAL_REGION", "us-east-1"),
                "scale": {
                    "enabled": os.getenv("GLOBAL_SCALE_ENABLED", "true").lower() == "true",
                    "multi_region_support": os.getenv("MULTI_REGION_SUPPORT", "true").lower() == "true"
                }
            },

            # Quantum security configuration
            "quantum": {
                "encryption": {
                    "enabled": os.getenv("QUANTUM_ENCRYPTION_ENABLED", "true").lower() == "true"
                },
                "key_rotation_interval": int(os.getenv("QUANTUM_KEY_ROTATION_INTERVAL", "24")),  # hours
                "secure_communication": os.getenv("QUANTUM_SECURE_COMMUNICATION", "true").lower() == "true"
            },

            # Blockchain integration configuration
            "blockchain": {
                "network": os.getenv("BLOCKCHAIN_NETWORK", "ethereum"),
                "rpc_url": os.getenv("BLOCKCHAIN_RPC_URL", "https://mainnet.infura.io/v3/YOUR_PROJECT_ID"),
                "smart_contract_address": os.getenv("SMART_CONTRACT_ADDRESS", "0x...")
            },

            # IoT device management configuration
            "iot": {
                "device_manager": {
                    "enabled": os.getenv("IOT_DEVICE_MANAGER_ENABLED", "true").lower() == "true"
                },
                "device_api_key": os.getenv("IOT_DEVICE_API_KEY", ""),
                "connection_timeout": int(os.getenv("IOT_DEVICE_CONNECTION_TIMEOUT", "30"))
            },

            # AR/VR interface configuration
            "arvr": {
                "interface": {
                    "enabled": os.getenv("ARVR_INTERFACE_ENABLED", "true").lower() == "true"
                },
                "rendering_engine": os.getenv("ARVR_RENDERING_ENGINE", "unity"),
                "supported_platforms": os.getenv("ARVR_SUPPORTED_PLATFORMS", "windows,macos,android").split(",")
            },

            # Global scaling configuration
            "global_scaling": {
                "load_balancer": os.getenv("GLOBAL_LOAD_BALANCER", "http://global-lb.example.com"),
                "regional_endpoints": json.loads(os.getenv("REGIONAL_ENDPOINTS", '["http://us-east.example.com", "http://eu-west.example.com"]')),
                "auto_scaling_enabled": os.getenv("AUTO_SCALING_ENABLED", "true").lower() == "true"
            },

            # PostgreSQL for enterprise analytics
            "postgres": {
                "host": os.getenv("POSTGRES_HOST", "localhost"),
                "port": int(os.getenv("POSTGRES_PORT", "5432")),
                "db": os.getenv("POSTGRES_DB", "enterprise_analytics"),
                "user": os.getenv("POSTGRES_USER", "analytics_user"),
                "password": os.getenv("POSTGRES_PASSWORD", "secure_password")
            },

            # Advanced AI configuration
            "ai": {
                "use_quantum": os.getenv("USE_QUANTUM_AI", "true").lower() == "true",
                "quantum_processor_provider": os.getenv("QUANTUM_PROCESSOR_PROVIDER", "qiskit"),
                "federated_learning_enabled": os.getenv("FEDERATED_LEARNING_ENABLED", "true").lower() == "true"
            },

            # Platinum Tier specific features
            "platinum_tier_features": {
                "enable_global_operations": os.getenv("ENABLE_GLOBAL_OPERATIONS", "true").lower() == "true",
                "enable_quantum_security": os.getenv("ENABLE_QUANTUM_SECURITY", "true").lower() == "true",
                "enable_blockchain_integration": os.getenv("ENABLE_BLOCKCHAIN_INTEGRATION", "true").lower() == "true",
                "enable_iot_connectivity": os.getenv("ENABLE_IOT_CONNECTIVITY", "true").lower() == "true",
                "enable_arvr_interfaces": os.getenv("ENABLE_ARVR_INTERFACES", "true").lower() == "true",
                "enable_predictive_analytics": os.getenv("ENABLE_PREDICTIVE_ANALYTICS", "true").lower() == "true",
                "enable_autonomous_operations": os.getenv("ENABLE_AUTONOMOUS_OPERATIONS", "true").lower() == "true"
            }
        }

    def save_config(self, config: Dict[str, Any]):
        """
        Save configuration to file
        """
        with open(self.config_path, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)

    def get(self, key: str, default: Any = None) -> Any:
        """
        Get a configuration value using dot notation (e.g., 'gmail.credentials_path')
        """
        keys = key.split('.')
        value = self.config

        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default

        return value

    def set(self, key: str, value: Any):
        """
        Set a configuration value using dot notation
        """
        keys = key.split('.')
        config_ref = self.config

        for k in keys[:-1]:
            if k not in config_ref or not isinstance(config_ref[k], dict):
                config_ref[k] = {}
            config_ref = config_ref[k]

        config_ref[keys[-1]] = value
        self.save_config(self.config)

    def reload(self):
        """
        Reload configuration from file
        """
        self.config = self.load_config()

    def update_from_dict(self, updates: Dict[str, Any]):
        """
        Update configuration with values from a dictionary
        """
        def deep_update(target: Dict, updates: Dict):
            for key, value in updates.items():
                if key in target and isinstance(target[key], dict) and isinstance(value, dict):
                    deep_update(target[key], value)
                else:
                    target[key] = value

        deep_update(self.config, updates)
        self.save_config(self.config)


# Global configuration instance
config_manager = ConfigManager()


def get_config(key: str, default: Any = None) -> Any:
    """
    Convenience function to get configuration values
    """
    return config_manager.get(key, default)


def set_config(key: str, value: Any):
    """
    Convenience function to set configuration values
    """
    config_manager.set(key, value)


def reload_config():
    """
    Convenience function to reload configuration
    """
    config_manager.reload()