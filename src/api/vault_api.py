#!/usr/bin/env python3
"""
ELYX Vault API
Provides REST API for vault operations (tasks, approvals, completed)

Usage:
    python src/api/vault_api.py --port 8080
"""

import sys
import json
import os
from pathlib import Path
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import yaml

# Add project root
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))


class VaultAPI:
    """Vault data access layer"""
    
    def __init__(self, vault_path: str = "obsidian_vault"):
        self.vault_path = Path(vault_path)
    
    ALLOWED_FOLDERS = {"Needs_Action", "Plans", "Pending_Approval", "Approved", "Rejected", "Done", "Logs", "Inbox", "Briefings", "Responses"}

    def _validate_folder(self, folder: str) -> bool:
        """Validate that the folder name is allowed and doesn't contain path traversal"""
        # Block path separators and traversal patterns
        if '..' in folder or '/' in folder or '\\' in folder:
            return False
        # Must be in the allowed set
        return folder in self.ALLOWED_FOLDERS

    def get_tasks(self, folder: str = "Needs_Action") -> list:
        """Get all tasks from a folder"""
        if not self._validate_folder(folder):
            return []
        folder_path = self.vault_path / folder
        if not folder_path.exists():
            return []
        
        tasks = []
        for md_file in folder_path.glob("*.md"):
            try:
                content = md_file.read_text(encoding='utf-8')
                frontmatter = self._parse_frontmatter(content)
                tasks.append({
                    "id": md_file.stem,
                    "filename": md_file.name,
                    "filepath": str(md_file),
                    "frontmatter": frontmatter,
                    "content": content,
                    "created": frontmatter.get('created', frontmatter.get('detected_at', '')),
                    "type": frontmatter.get('type', 'unknown'),
                    "priority": frontmatter.get('priority', 'medium'),
                    "status": frontmatter.get('status', 'pending'),
                    "from": frontmatter.get('from', ''),
                    "subject": frontmatter.get('subject', '')
                })
            except Exception as e:
                print(f"Error reading {md_file}: {e}")
        
        # Sort by created date (newest first)
        tasks.sort(key=lambda x: x.get('created', ''), reverse=True)
        return tasks
    
    def get_approval_requests(self) -> list:
        """Get all approval requests, with action/reason from second YAML block if present"""
        tasks = self.get_tasks("Pending_Approval")
        for t in tasks:
            details = self._parse_approval_details(t.get("content", ""))
            t["frontmatter"] = {**(t.get("frontmatter") or {}), **details}
        return tasks
    
    def get_completed_tasks(self) -> list:
        """Get completed tasks from Done folder"""
        return self.get_tasks("Done")
    
    def approve_task(self, filename: str) -> dict:
        """Approve a task by moving it from Pending_Approval to Approved"""
        return self._move_task(filename, "Pending_Approval", "Approved")
    
    def reject_task(self, filename: str) -> dict:
        """Reject a task by moving it from Pending_Approval to Rejected"""
        return self._move_task(filename, "Pending_Approval", "Rejected")

    def complete_task(self, filename: str) -> dict:
        """Mark a task done by moving it from Needs_Action to Done"""
        return self._move_task(filename, "Needs_Action", "Done")
    
    def _move_task(self, filename: str, from_folder: str, to_folder: str) -> dict:
        """Move a task file between folders"""
        try:
            # Sanitize filename - block path traversal
            if '..' in filename or '/' in filename or '\\' in filename:
                return {"success": False, "error": "Invalid filename"}
            from_path = self.vault_path / from_folder / filename
            to_path = self.vault_path / to_folder / filename
            # Verify resolved paths are within the vault
            if not str(from_path.resolve()).startswith(str(self.vault_path.resolve())):
                return {"success": False, "error": "Invalid path"}
            if not str(to_path.resolve()).startswith(str(self.vault_path.resolve())):
                return {"success": False, "error": "Invalid path"}
            
            if not from_path.exists():
                return {"success": False, "error": f"File not found: {filename}"}
            
            # Read and update status
            content = from_path.read_text(encoding='utf-8')
            frontmatter = self._parse_frontmatter(content)
            if to_folder == "Approved":
                frontmatter['status'] = 'approved'
            elif to_folder == "Rejected":
                frontmatter['status'] = 'rejected'
            else:
                frontmatter['status'] = 'completed'
            frontmatter['processed_at'] = datetime.now().isoformat()
            
            # Rebuild content with updated frontmatter
            content_without_fm = self._remove_frontmatter(content)
            new_fm_yaml = yaml.dump(frontmatter, default_flow_style=False).strip()
            new_content = f"---\n{new_fm_yaml}\n---\n{content_without_fm}"
            
            # Write to new location (ensure target folder exists)
            to_path.parent.mkdir(parents=True, exist_ok=True)
            to_path.write_text(new_content, encoding='utf-8')
            
            # Delete old file
            from_path.unlink()
            
            return {
                "success": True,
                "message": f"Task {to_folder.lower()[:-1]}d",
                "filename": filename,
                "new_path": str(to_path)
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def get_dashboard_summary(self) -> dict:
        """Get dashboard summary statistics"""
        return {
            "pending_tasks": len(self.get_tasks("Needs_Action")),
            "pending_approvals": len(self.get_approval_requests()),
            "completed_tasks": len(self.get_completed_tasks()),
            "plans_created": len(list((self.vault_path / "Plans").glob("*.md"))) if (self.vault_path / "Plans").exists() else 0,
            "last_updated": datetime.now().isoformat()
        }
    
    def _parse_frontmatter(self, content: str) -> dict:
        """Parse YAML frontmatter from markdown"""
        lines = content.split('\n')
        if len(lines) > 2 and lines[0].strip() == '---':
            for i in range(1, len(lines)):
                if lines[i].strip() == '---':
                    try:
                        fm_str = '\n'.join(lines[1:i])
                        return yaml.safe_load(fm_str) or {}
                    except Exception:
                        return {}
        return {}
    
    def _remove_frontmatter(self, content: str) -> str:
        """Remove frontmatter from markdown content"""
        lines = content.split('\n')
        if len(lines) > 2 and lines[0].strip() == '---':
            for i in range(1, len(lines)):
                if lines[i].strip() == '---':
                    return '\n'.join(lines[i+1:])
        return content

    def _parse_approval_details(self, content: str) -> dict:
        """Parse second YAML block in approval files for action, reason, related_task"""
        lines = content.split('\n')
        count = 0
        start = -1
        for i, line in enumerate(lines):
            if line.strip() == '---':
                count += 1
                if count == 1:
                    start = -1
                elif count == 2 and start == -1:
                    start = i + 1
                elif count == 3 and start >= 0:
                    try:
                        fm_str = '\n'.join(lines[start:i])
                        return yaml.safe_load(fm_str) or {}
                    except Exception:
                        return {}
        return {}


_ALLOWED_ORIGINS = os.getenv(
    "ALLOWED_ORIGINS", "http://localhost:3000,http://localhost:8080,http://localhost:8081"
).split(",")


class VaultAPIHandler(BaseHTTPRequestHandler):
    """HTTP request handler for Vault API"""

    def __init__(self, *args, vault_api: VaultAPI = None, **kwargs):
        self.vault_api = vault_api or VaultAPI()
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
        query = parse_qs(parsed.query)
        
        try:
            if path == '/api/vault/summary':
                self._send_json(self.vault_api.get_dashboard_summary())
            
            elif path == '/api/vault/tasks':
                folder = query.get('folder', ['Needs_Action'])[0]
                tasks = self.vault_api.get_tasks(folder)
                self._send_json({"tasks": tasks, "count": len(tasks)})
            
            elif path == '/api/vault/approvals':
                approvals = self.vault_api.get_approval_requests()
                self._send_json({"approvals": approvals, "count": len(approvals)})
            
            elif path == '/api/vault/completed':
                completed = self.vault_api.get_completed_tasks()
                self._send_json({"completed": completed, "count": len(completed)})
            
            elif path.startswith('/api/vault/task/'):
                # Get specific task content
                filename = path.split('/')[-1] + '.md'
                folder = query.get('folder', ['Needs_Action'])[0]
                tasks = self.vault_api.get_tasks(folder)
                task = next((t for t in tasks if t['filename'] == filename), None)
                
                if task:
                    self._send_json({"task": task})
                else:
                    self._send_json({"error": "Task not found"}, 404)
            
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
            
            if path == '/api/vault/approve':
                filename = body.get('filename')
                if not filename:
                    self._send_json({"error": "filename required"}, 400)
                    return
                
                result = self.vault_api.approve_task(filename)
                status = 200 if result.get('success') else 400
                self._send_json(result, status)
            
            elif path == '/api/vault/reject':
                filename = body.get('filename')
                if not filename:
                    self._send_json({"error": "filename required"}, 400)
                    return
                
                result = self.vault_api.reject_task(filename)
                status = 200 if result.get('success') else 400
                self._send_json(result, status)

            elif path == '/api/vault/complete':
                filename = body.get('filename')
                if not filename:
                    self._send_json({"error": "filename required"}, 400)
                    return
                
                result = self.vault_api.complete_task(filename)
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


def run_server(port: int = 8080):
    """Run the Vault API server"""
    vault_api = VaultAPI()
    
    def handler(*args, **kwargs):
        VaultAPIHandler(*args, vault_api=vault_api, **kwargs)
    
    server = HTTPServer(('localhost', port), handler)
    print(f"🔓 ELYX Vault API running at http://localhost:{port}")
    print(f"   - GET  /api/vault/summary")
    print(f"   - GET  /api/vault/tasks?folder=Needs_Action")
    print(f"   - GET  /api/vault/approvals")
    print(f"   - GET  /api/vault/completed")
    print(f"   - POST /api/vault/approve")
    print(f"   - POST /api/vault/reject")
    print(f"   - POST /api/vault/complete")
    print(f"\nPress Ctrl+C to stop")
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down Vault API...")
        server.shutdown()


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="ELYX Vault API Server")
    parser.add_argument("--port", type=int, default=8080, help="Port to run server on")
    args = parser.parse_args()
    
    run_server(args.port)
