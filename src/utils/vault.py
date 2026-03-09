import json
from pathlib import Path
from datetime import datetime
import yaml
import re

class VaultEntry:
    """
    Represents an entry in the Obsidian vault
    """
    def __init__(self, filepath, content=None):
        self.filepath = Path(filepath)
        self.filename = self.filepath.name
        self.content = content or self.filepath.read_text(encoding='utf-8')
        self.frontmatter = self._extract_frontmatter()
        self.status = self.frontmatter.get('status', 'pending')
        self.type = self.frontmatter.get('type', 'task')

    def _extract_frontmatter(self):
        """
        Extract YAML frontmatter from markdown file
        """
        content_lines = self.content.split('\n')
        if len(content_lines) > 2 and content_lines[0].strip() == '---':
            # Find closing ---
            for i in range(1, len(content_lines)):
                if content_lines[i].strip() == '---':
                    frontmatter_str = '\n'.join(content_lines[1:i])
                    try:
                        return yaml.safe_load(frontmatter_str) or {}
                    except yaml.YAMLError:
                        return {}
        return {}

    def update_status(self, new_status):
        """
        Update the status in the frontmatter and save the file
        """
        self.frontmatter['status'] = new_status
        self.status = new_status

        # Update the content with new frontmatter
        content_without_frontmatter = self._remove_frontmatter()
        new_content = self._add_frontmatter(content_without_frontmatter)

        self.filepath.write_text(new_content, encoding='utf-8')
        self.content = new_content

    def _remove_frontmatter(self):
        """
        Remove frontmatter from content
        """
        content_lines = self.content.split('\n')
        if len(content_lines) > 2 and content_lines[0].strip() == '---':
            for i in range(1, len(content_lines)):
                if content_lines[i].strip() == '---':
                    return '\n'.join(content_lines[i+1:])
        return self.content

    def _add_frontmatter(self, content_without_frontmatter):
        """
        Add frontmatter to content
        """
        frontmatter_yaml = yaml.dump(self.frontmatter, default_flow_style=False).strip()
        return f"---\n{frontmatter_yaml}\n---\n{content_without_frontmatter}"

def create_vault_entry(vault_path, folder, filename, content, entry_type=None, priority='medium'):
    """
    Create a new vault entry in the specified folder
    """
    vault_path = Path(vault_path)
    folder_path = vault_path / folder
    folder_path.mkdir(exist_ok=True)

    filepath = folder_path / filename

    # Create frontmatter
    frontmatter = {
        'type': entry_type or 'task',
        'priority': priority,
        'status': 'pending',
        'created': datetime.now().isoformat(),
        'source': 'system'
    }

    frontmatter_yaml = yaml.dump(frontmatter, default_flow_style=False).strip()
    full_content = f"---\n{frontmatter_yaml}\n---\n\n{content}"

    filepath.write_text(full_content, encoding='utf-8')
    return filepath

def get_pending_tasks(vault_path):
    """
    Get all pending tasks from the Needs_Action folder
    """
    vault_path = Path(vault_path)
    needs_action_path = vault_path / 'Needs_Action'

    if not needs_action_path.exists():
        return []

    pending_tasks = []
    for file_path in needs_action_path.glob('*.md'):
        try:
            entry = VaultEntry(file_path)
            if entry.status in ['pending', 'processing']:
                pending_tasks.append(entry)
        except Exception:
            continue  # Skip files that can't be parsed

    return pending_tasks

def move_file_to_folder(file_path, target_folder, vault_path):
    """
    Move a file from one vault folder to another.
    Handles WinError 183 (file already exists) by appending a timestamp suffix.
    """
    import time

    vault_path = Path(vault_path)
    file_path = Path(file_path)
    target_path = vault_path / target_folder
    target_path.mkdir(exist_ok=True)

    target_file = target_path / file_path.name

    # If target already exists, add a timestamp suffix to avoid collision
    if target_file.exists():
        stem = file_path.stem
        suffix = file_path.suffix
        target_file = target_path / f"{stem}_{int(time.time())}{suffix}"

    try:
        file_path.rename(target_file)
    except OSError:
        # Fallback: copy + delete (handles cross-drive moves on Windows)
        import shutil
        shutil.copy2(str(file_path), str(target_file))
        file_path.unlink()

    return target_file

def get_files_by_status(vault_path, folder, status):
    """
    Get all files in a folder with a specific status
    """
    vault_path = Path(vault_path)
    folder_path = vault_path / folder

    if not folder_path.exists():
        return []

    matching_files = []
    for file_path in folder_path.glob('*.md'):
        try:
            entry = VaultEntry(file_path)
            if entry.status == status:
                matching_files.append(entry)
        except Exception:
            continue  # Skip files that can't be parsed

    return matching_files