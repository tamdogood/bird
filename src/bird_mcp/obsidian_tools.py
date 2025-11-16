"""Obsidian vault management tools for the Bird MCP server."""

from pathlib import Path
from typing import Any, Optional
import re
from datetime import datetime
import yaml


class ObsidianTools:
    """Tools for interacting with Obsidian vault via filesystem."""

    def __init__(self, vault_path: str):
        """
        Initialize Obsidian tools with vault path.

        Args:
            vault_path: Absolute path to Obsidian vault directory
        """
        self.vault_path = Path(vault_path)
        if not self.vault_path.exists():
            raise ValueError(f"Vault path does not exist: {vault_path}")

    async def create_note(
        self,
        title: str,
        content: str,
        folder: str = "",
        tags: Optional[list[str]] = None,
        frontmatter: Optional[dict[str, Any]] = None,
    ) -> dict[str, Any]:
        """
        Create a new note in the Obsidian vault.

        Args:
            title: Note title (will be filename)
            content: Note content in markdown
            folder: Subfolder within vault (e.g., "6 - main notes")
            tags: List of tags to add
            frontmatter: Additional YAML frontmatter fields

        Returns:
            Success status and note path
        """
        try:
            # Sanitize filename
            filename = re.sub(r'[<>:"/\\|?*]', '', title)
            filename = f"{filename}.md"

            # Determine full path
            if folder:
                note_folder = self.vault_path / folder
                note_folder.mkdir(parents=True, exist_ok=True)
            else:
                note_folder = self.vault_path

            note_path = note_folder / filename

            # Check if note already exists
            if note_path.exists():
                return {
                    "success": False,
                    "error": f"Note already exists: {filename}",
                }

            # Build frontmatter
            fm = frontmatter or {}
            fm["created"] = datetime.now().isoformat()
            if tags:
                fm["tags"] = tags

            # Build full note content
            full_content = "---\n"
            full_content += yaml.dump(fm, default_flow_style=False, allow_unicode=True)
            full_content += "---\n\n"
            full_content += f"# {title}\n\n"
            full_content += content

            # Write note
            note_path.write_text(full_content, encoding="utf-8")

            return {
                "success": True,
                "path": str(note_path.relative_to(self.vault_path)),
                "absolute_path": str(note_path),
                "message": f"Note created: {filename}",
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def read_note(self, note_path: str) -> dict[str, Any]:
        """
        Read a note from the vault.

        Args:
            note_path: Relative path from vault root (e.g., "6 - main notes/My Note.md")

        Returns:
            Note content, frontmatter, and metadata
        """
        try:
            full_path = self.vault_path / note_path
            if not full_path.exists():
                return {"success": False, "error": f"Note not found: {note_path}"}

            content = full_path.read_text(encoding="utf-8")

            # Parse frontmatter if present
            frontmatter = {}
            body = content
            if content.startswith("---"):
                parts = content.split("---", 2)
                if len(parts) >= 3:
                    try:
                        frontmatter = yaml.safe_load(parts[1]) or {}
                        body = parts[2].strip()
                    except yaml.YAMLError:
                        pass

            return {
                "success": True,
                "content": body,
                "frontmatter": frontmatter,
                "path": note_path,
                "absolute_path": str(full_path),
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def update_note(
        self,
        note_path: str,
        content: Optional[str] = None,
        frontmatter: Optional[dict[str, Any]] = None,
        append: bool = False,
    ) -> dict[str, Any]:
        """
        Update an existing note.

        Args:
            note_path: Relative path to note
            content: New content (or content to append)
            frontmatter: New/updated frontmatter fields
            append: If True, append content instead of replacing

        Returns:
            Success status
        """
        try:
            # Read existing note
            existing = await self.read_note(note_path)
            if not existing["success"]:
                return existing

            full_path = self.vault_path / note_path

            # Update frontmatter
            new_fm = existing.get("frontmatter", {})
            if frontmatter:
                new_fm.update(frontmatter)
            new_fm["modified"] = datetime.now().isoformat()

            # Update content
            if content:
                if append:
                    new_content = existing["content"] + "\n\n" + content
                else:
                    new_content = content
            else:
                new_content = existing["content"]

            # Write updated note
            full_content = "---\n"
            full_content += yaml.dump(new_fm, default_flow_style=False, allow_unicode=True)
            full_content += "---\n\n"
            full_content += new_content

            full_path.write_text(full_content, encoding="utf-8")

            return {"success": True, "message": f"Note updated: {note_path}"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def delete_note(self, note_path: str) -> dict[str, Any]:
        """
        Delete a note from the vault.

        Args:
            note_path: Relative path to note

        Returns:
            Success status
        """
        try:
            full_path = self.vault_path / note_path
            if not full_path.exists():
                return {"success": False, "error": f"Note not found: {note_path}"}

            full_path.unlink()
            return {"success": True, "message": f"Note deleted: {note_path}"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def search_notes(
        self,
        query: str,
        folder: Optional[str] = None,
        tag: Optional[str] = None,
    ) -> dict[str, Any]:
        """
        Search notes in the vault.

        Args:
            query: Text to search for in note content
            folder: Limit search to specific folder
            tag: Filter by tag

        Returns:
            List of matching notes
        """
        try:
            search_path = self.vault_path / folder if folder else self.vault_path
            results = []

            for note_path in search_path.rglob("*.md"):
                content = note_path.read_text(encoding="utf-8")

                # Tag filter
                if tag:
                    if not re.search(rf"#\b{re.escape(tag)}\b", content) and \
                       not re.search(rf"tags:.*{re.escape(tag)}", content):
                        continue

                # Content search
                if query.lower() in content.lower():
                    results.append({
                        "path": str(note_path.relative_to(self.vault_path)),
                        "title": note_path.stem,
                        "folder": str(note_path.parent.relative_to(self.vault_path)),
                    })

            return {
                "success": True,
                "results": results,
                "count": len(results),
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def list_notes(
        self,
        folder: str = "",
        recursive: bool = True,
    ) -> dict[str, Any]:
        """
        List all notes in vault or specific folder.

        Args:
            folder: Folder to list (empty = root)
            recursive: Include subfolders

        Returns:
            List of notes with metadata
        """
        try:
            search_path = self.vault_path / folder if folder else self.vault_path
            pattern = "**/*.md" if recursive else "*.md"

            notes = []
            for note_path in search_path.glob(pattern):
                notes.append({
                    "path": str(note_path.relative_to(self.vault_path)),
                    "title": note_path.stem,
                    "folder": str(note_path.parent.relative_to(self.vault_path)),
                    "size": note_path.stat().st_size,
                    "modified": datetime.fromtimestamp(note_path.stat().st_mtime).isoformat(),
                })

            # Sort by modified time (newest first)
            notes.sort(key=lambda x: x["modified"], reverse=True)

            return {
                "success": True,
                "notes": notes,
                "count": len(notes),
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def get_daily_note(self, date: Optional[str] = None) -> dict[str, Any]:
        """
        Get or create daily note for a specific date.

        Args:
            date: Date in YYYY-MM-DD format (default: today)

        Returns:
            Note content and path
        """
        try:
            if date is None:
                date_obj = datetime.now()
            else:
                date_obj = datetime.fromisoformat(date)

            date_str = date_obj.strftime("%Y-%m-%d")
            folder = "7- daily"  # Based on your vault structure

            note_path = f"{folder}/{date_str}.md"
            full_path = self.vault_path / note_path

            # Create if doesn't exist
            if not full_path.exists():
                await self.create_note(
                    title=date_str,
                    content=f"## Daily Note - {date_str}\n\n",
                    folder=folder,
                    frontmatter={
                        "date": date_str,
                        "type": "daily-note",
                    }
                )

            return await self.read_note(note_path)
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def get_vault_stats(self) -> dict[str, Any]:
        """
        Get statistics about the vault.

        Returns:
            Vault statistics
        """
        try:
            all_notes = list(self.vault_path.rglob("*.md"))

            # Count notes by folder
            folder_counts = {}
            total_size = 0

            for note_path in all_notes:
                folder = str(note_path.parent.relative_to(self.vault_path))
                folder_counts[folder] = folder_counts.get(folder, 0) + 1
                total_size += note_path.stat().st_size

            return {
                "success": True,
                "stats": {
                    "total_notes": len(all_notes),
                    "total_size_bytes": total_size,
                    "total_size_mb": round(total_size / (1024 * 1024), 2),
                    "folders": folder_counts,
                    "vault_path": str(self.vault_path),
                }
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
