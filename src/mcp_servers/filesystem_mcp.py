"""
ELYX Filesystem MCP Server
Safe file operations scoped to the Obsidian vault.
"""

import os
import json
import shutil
from pathlib import Path

from mcp.server.fastmcp import FastMCP

mcp = FastMCP("elyx-filesystem-mcp")

VAULT_PATH = Path(os.environ.get("VAULT_PATH", "obsidian_vault")).resolve()


def _safe_path(rel_path: str) -> Path:
    """Resolve path and ensure it stays within the vault."""
    resolved = (VAULT_PATH / rel_path).resolve()
    if not str(resolved).startswith(str(VAULT_PATH)):
        raise ValueError(f"Path escapes vault: {rel_path}")
    return resolved


# --- Tools ---


@mcp.tool()
def read_file(path: str) -> str:
    """Read a file from the Obsidian vault."""
    fp = _safe_path(path)
    if not fp.exists():
        return json.dumps({"error": f"File not found: {path}"})
    return json.dumps({"path": path, "content": fp.read_text(encoding="utf-8")})


@mcp.tool()
def write_file(path: str, content: str) -> str:
    """Write content to a file in the Obsidian vault."""
    fp = _safe_path(path)
    fp.parent.mkdir(parents=True, exist_ok=True)
    fp.write_text(content, encoding="utf-8")
    return json.dumps({"success": True, "path": path, "bytes": len(content.encode("utf-8"))})


@mcp.tool()
def list_directory(path: str = "") -> str:
    """List files and folders in a vault directory."""
    dp = _safe_path(path) if path else VAULT_PATH
    if not dp.is_dir():
        return json.dumps({"error": f"Not a directory: {path}"})

    items = []
    for entry in sorted(dp.iterdir()):
        items.append({
            "name": entry.name,
            "type": "directory" if entry.is_dir() else "file",
            "size": entry.stat().st_size if entry.is_file() else None,
        })
    return json.dumps({"path": path or "/", "count": len(items), "items": items})


@mcp.tool()
def move_file(source: str, destination: str) -> str:
    """Move a file within the Obsidian vault."""
    src = _safe_path(source)
    dst = _safe_path(destination)
    if not src.exists():
        return json.dumps({"error": f"Source not found: {source}"})
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.move(str(src), str(dst))
    return json.dumps({"success": True, "from": source, "to": destination})


if __name__ == "__main__":
    mcp.run(transport="stdio")
