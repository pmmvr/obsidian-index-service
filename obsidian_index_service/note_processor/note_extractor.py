"""Extracts metadata from Obsidian markdown files."""

import json
import logging
from pathlib import Path
from datetime import datetime
import frontmatter

from .logging_config import configure_logging

logger = logging.getLogger(__name__)


def extract_note_data(file_path, vault_path):
    """Extract metadata and content from a markdown file.

    Args:
        file_path (Path): Path to the markdown file
        vault_path (Path): Root path of the vault

    Returns:
        dict: Extracted note data

    Raises:
        Various exceptions that will be caught by the caller
    """
    # Get relative path from vault root
    rel_path = file_path.relative_to(vault_path)

    # Extract file stats
    stats = file_path.stat()
    created_date = datetime.fromtimestamp(stats.st_ctime).isoformat()
    modified_date = datetime.fromtimestamp(stats.st_mtime).isoformat()

    # Extract title from filename (without extension)
    title = file_path.stem

    # Extract parent folder path relative to vault
    parent_folder = str(rel_path.parent)
    if parent_folder == ".":
        parent_folder = ""

    # Parse frontmatter and content
    with open(file_path, "r", encoding="utf-8") as f:
        post = frontmatter.load(f)
        content = post.content

    # Extract tags from frontmatter
    tags = extract_tags_from_frontmatter(post.metadata)

    # Assemble note data
    note_data = {
        "path": str(rel_path),
        "title": title,
        "parent_folder": parent_folder,
        "tags": json.dumps(tags),
        "created_date": created_date,
        "modified_date": modified_date,
        "content": content,
        "status": "success",
        "error_message": "",
    }

    logger.info(f"Processed note: {rel_path}")
    return note_data


def extract_tags_from_frontmatter(metadata):
    """Extract tags from frontmatter with support for multiple formats.

    Args:
        metadata (dict): The frontmatter metadata

    Returns:
        list: Extracted tags
    """
    tags = []

    # Extract tags from 'tags' field
    if "tags" in metadata:
        raw_tags = metadata["tags"]
        if isinstance(raw_tags, list):
            # Handle YAML list format directly
            tags = raw_tags
        elif isinstance(raw_tags, str):
            # Handle comma or space-separated tags
            tags = [tag.strip() for tag in raw_tags.replace(",", " ").split()]

    # Look for alternative tag formats in the metadata
    for key, value in metadata.items():
        if key.lower() == "metadata-e.g.-tags" and isinstance(value, list):
            tags.extend(value)
        elif key.lower() == "metadata" and isinstance(value, list):
            # Add support for the 'metadata' field containing tags
            tags.extend(value)

    return tags


def create_error_metadata(file_path, vault_path, error):
    """Create metadata for a file that failed processing.

    Args:
        file_path (Path): Path to the file
        vault_path (Path): Root path of the vault
        error (Exception): The error that occurred

    Returns:
        dict: Error metadata
    """
    try:
        rel_path = Path(file_path).relative_to(vault_path)
    except ValueError:
        rel_path = file_path

    return {
        "path": str(rel_path),
        "title": Path(file_path).stem,
        "parent_folder": "",
        "tags": "[]",
        "created_date": "",
        "modified_date": "",
        "content": "",
        "status": "error",
        "error_message": str(error),
    }

