"""Utilities for handling files in the note processor."""

import logging
from pathlib import Path

from .logging_config import configure_logging

logger = logging.getLogger(__name__)

def is_markdown_file(file_path):
    """Check if a file is a markdown file.
    
    Args:
        file_path (str or Path): Path to the file
        
    Returns:
        bool: True if the file is a markdown file, False otherwise
    """
    return Path(file_path).suffix.lower() in ['.md', '.markdown']

def validate_vault_path(vault_path):
    """Validate that the vault path exists.
    
    Args:
        vault_path (str or Path): Path to validate
        
    Returns:
        Path: Validated Path object
        
    Raises:
        ValueError: If the path doesn't exist
    """
    path = Path(vault_path)
    if not path.exists():
        raise ValueError(f"Vault path does not exist: {vault_path}")
    return path 