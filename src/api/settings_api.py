#!/usr/bin/env python3
"""
ELYX Settings API
Provides REST API for managing feature flags and settings

Usage:
    python src/api/settings_api.py --port 8081
"""

import sys
import json
import os
from pathlib import Path
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
from datetime import datetime

# Add project root
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# Feature flags configuration
FEATURE_FLAGS = {
    "ENABLE_ANALYTICS": {
        "default": True,
        "type": "boolean",
        "description": "Enable analytics and reporting features",
        "category": "features"
    },
    "ENABLE_LEARNING": {
        "default": True,
        "type": "boolean",
        "description": "Enable adaptive learning and AI improvement",
        "category": "features"
    },
    "ENABLE_CALENDAR_INTEGRATION": {
        "default": False,
        "type": "boolean",
        "description": "Enable calendar synchronization",
        "category": "integrations"
    },
    "ENABLE_AUDIT_LOGGING": {
        "default": True,
        "type": "boolean",
        "description": "Enable cryptographic audit logging",
        "category": "security"
    },
    "ENABLE_ACTION_SIGNING": {
        "default": True,
        "type": "boolean",
        "description": "Enable cryptographic action signing",
        "category": "security"
    },
    "ENABLE_SOCIAL_POSTING": {
        "default": True,
        "type": "boolean",
        "description": "Enable social media auto-posting",
        "category": "features"
    },
    "ENABLE_CEO_BRIEFINGS": {
        "default": True,
        "type": "boolean",
        "description": "Enable weekly CEO briefing generation",
        "category": "features"
    },
    "ENABLE_WINDOWS_SCHEDULER": {
        "default": True,
        "type": "boolean",
        "description": "Enable Windows Task Scheduler integration",
        "category": "integrations"
    }
}


class SettingsAPI:
    """Settings management layer"""
    
    def __init__(self, env_path: str = ".env", config_path: str = "config.json"):
        self.env_path = Path(env_path)
        self.config_path = Path(config_path)
        self.load_settings()
    
    def load_settings(self):
        """Load current settings from .env and config.json"""
        self.env_vars = {}
        self.config = {}
        
        # Load .env
        if self.env_path.exists():
            content = self.env_path.read_text(encoding='utf-8')
            for line in content.split('\n'):
                if '=' in line and not line.strip().startswith('#'):
                    key, value = line.split('=', 1)
                    self.env_vars[key.strip()] = value.strip().strip('"\'')
        
        # Load config.json
        if self.config_path.exists():
            with open(self.config_path, 'r', encoding='utf-8') as f:
                self.config = json.load(f)
    
    def save_env(self):
        """Save .env file"""
        lines = []
        for key, value in self.env_vars.items():
            lines.append(f"{key}={value}")
        
        self.env_path.write_text('\n'.join(lines), encoding='utf-8')
    
    def save_config(self):
        """Save config.json"""
        with open(self.config_path, 'w', encoding='utf-8') as f:
            json.dump(self.config, f, indent=2)
    
    def get_feature_flag(self, flag_name: str) -> bool:
        """Get feature flag value"""
        # Check .env first
        if flag_name in self.env_vars:
            value = self.env_vars[flag_name].lower()
            return value in ('true', '1', 'yes')
        
        # Check config.json
        if flag_name in self.config:
            value = str(self.config[flag_name]).lower()
            return value in ('true', '1', 'yes')
        
        # Return default
        return FEATURE_FLAGS.get(flag_name, {}).get('default', False)
    
    def set_feature_flag(self, flag_name: str, value: bool) -> dict:
        """Set feature flag value"""
        if flag_name not in FEATURE_FLAGS:
            return {
                "success": False,
                "error": f"Unknown feature flag: {flag_name}"
            }
        
        # Save to .env
        self.env_vars[flag_name] = str(value).upper()
        self.save_env()
        
        return {
            "success": True,
            "flag": flag_name,
            "value": value,
            "message": f"Feature {flag_name} {'enabled' if value else 'disabled'}"
        }
    
    def get_all_flags(self) -> list:
        """Get all feature flags with their current values"""
        flags = []
        for flag_name, config in FEATURE_FLAGS.items():
            current_value = self.get_feature_flag(flag_name)
            flags.append({
                "name": flag_name,
                "value": current_value,
                "default": config['default'],
                "type": config['type'],
                "description": config['description'],
                "category": config['category']
            })
        
        return flags
    
    def get_settings(self) -> dict:
        """Get all settings (filtered to exclude sensitive data)"""
        return {
            "feature_flags": self.get_all_flags(),
        }
    
    def update_setting(self, key: str, value: any) -> dict:
        """Update a setting"""
        if key.startswith('ENABLE_'):
            return self.set_feature_flag(key, value)
        else:
            # Update config.json
            self.config[key] = value
            self.save_config()
            return {
                "success": True,
                "key": key,
                "value": value
            }


_ALLOWED_ORIGINS = os.getenv(
    "ALLOWED_ORIGINS", "http://localhost:3000,http://localhost:8080,http://localhost:8081"
).split(",")


class SettingsAPIHandler(BaseHTTPRequestHandler):
    """HTTP request handler for Settings API"""

    def __init__(self, *args, settings_api: SettingsAPI = None, **kwargs):
        self.settings_api = settings_api or SettingsAPI()
        super().__init__(*args, **kwargs)

    def _get_cors_origin(self):
        """Return the request Origin if it is in the allowed list, else empty."""
        origin = self.headers.get('Origin', '')
        if origin in _ALLOWED_ORIGINS:
            return origin
        return ''

    def _set_headers(self, status=200, content_type="application/json"):
        self.send_response(status)
        self.send_header('Content-Type', content_type)
        cors_origin = self._get_cors_origin()
        if cors_origin:
            self.send_header('Access-Control-Allow-Origin', cors_origin)
            self.send_header('Vary', 'Origin')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
    
    def _send_json(self, data, status=200):
        self._set_headers(status)
        self.wfile.write(json.dumps(data).encode())
    
    def do_OPTIONS(self):
        self._set_headers(200)
    
    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path
        
        try:
            if path == '/api/settings/flags':
                # Get all feature flags
                flags = self.settings_api.get_all_flags()
                self._send_json({"flags": flags, "count": len(flags)})
            
            elif path == '/api/settings/flags/' + parsed.path.split('/')[-1]:
                # Get specific flag
                flag_name = parsed.path.split('/')[-1]
                value = self.settings_api.get_feature_flag(flag_name)
                self._send_json({"flag": flag_name, "value": value})
            
            elif path == '/api/settings/all':
                # Get all settings
                settings = self.settings_api.get_settings()
                self._send_json(settings)
            
            else:
                self._send_json({"error": "Not found"}, 404)
                
        except Exception as e:
            self._send_json({"error": str(e)}, 500)
    
    def do_POST(self):
        parsed = urlparse(self.path)
        path = parsed.path
        
        try:
            content_length = int(self.headers.get('Content-Length', 0))
            body = json.loads(self.rfile.read(content_length).decode())
            
            if path == '/api/settings/flags':
                # Update feature flag
                flag_name = body.get('flag')
                value = body.get('value')
                
                if not flag_name:
                    self._send_json({"error": "flag name required"}, 400)
                    return
                
                result = self.settings_api.set_feature_flag(flag_name, value)
                status = 200 if result.get('success') else 400
                self._send_json(result, status)
            
            elif path == '/api/settings/update':
                # Update any setting
                key = body.get('key')
                value = body.get('value')
                
                if not key:
                    self._send_json({"error": "key required"}, 400)
                    return
                
                result = self.settings_api.update_setting(key, value)
                status = 200 if result.get('success') else 400
                self._send_json(result, status)
            
            else:
                self._send_json({"error": "Not found"}, 404)
                
        except json.JSONDecodeError:
            self._send_json({"error": "Invalid JSON"}, 400)
        except Exception as e:
            self._send_json({"error": str(e)}, 500)
    
    def log_message(self, format, *args):
        # Suppress default logging
        pass


def run_server(port: int = 8081):
    """Run the Settings API server"""
    settings_api = SettingsAPI()
    
    def handler(*args, **kwargs):
        SettingsAPIHandler(*args, settings_api=settings_api, **kwargs)
    
    server = HTTPServer(('localhost', port), handler)
    print(f"🔧 ELYX Settings API running at http://localhost:{port}")
    print(f"   - GET  /api/settings/flags - Get all feature flags")
    print(f"   - GET  /api/settings/flags/FLAG_NAME - Get specific flag")
    print(f"   - POST /api/settings/flags - Update feature flag")
    print(f"   - GET  /api/settings/all - Get all settings")
    print(f"\nPress Ctrl+C to stop")
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down Settings API...")
        server.shutdown()


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="ELYX Settings API Server")
    parser.add_argument("--port", type=int, default=8081, help="Port to run server on")
    args = parser.parse_args()
    
    run_server(args.port)
