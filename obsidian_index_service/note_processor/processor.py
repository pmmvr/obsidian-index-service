"""Main note processor implementation."""

import logging
from pathlib import Path

from .file_utils import is_markdown_file, validate_vault_path
from .note_extractor import extract_note_data, create_error_metadata
from .logging_config import configure_logging

logger = logging.getLogger(__name__)


class NoteProcessor:
    """Processes Obsidian markdown files and extracts metadata."""

    def __init__(self, vault_path):
        """Initialize the note processor.

        Args:
            vault_path (str): Path to the Obsidian vault directory

        Raises:
            ValueError: If the vault path doesn't exist
        """
        self.vault_path = validate_vault_path(vault_path)
        logger.info(f"Note processor initialized with vault path: {vault_path}")

    def process_file(self, file_path):
        """Process a markdown file and extract its metadata.

        Args:
            file_path (str or Path): Path to the markdown file

        Returns:
            dict: Extracted metadata or None if processing fails
        """
        try:
            file_path = Path(file_path)

            # Skip non-markdown files
            if not is_markdown_file(file_path):
                logger.debug(f"Skipping non-markdown file: {file_path}")
                return None

            # Extract note data
            return extract_note_data(file_path, self.vault_path)

        except Exception as e:
            logger.error(f"Error processing file {file_path}: {e}")
            # Return metadata with error status
            return create_error_metadata(file_path, self.vault_path, e)

    def is_markdown_file(self, file_path):
        """Check if a file is a markdown file.

        Args:
            file_path (str or Path): Path to the file

        Returns:
            bool: True if the file is a markdown file, False otherwise
        """
        return is_markdown_file(file_path)

