"""Scans Obsidian vault for existing files and indexes them."""

import logging
from pathlib import Path
from obsidian_index_service.note_processor.processor import NoteProcessor
from obsidian_index_service.db.database import Database
from .logging_config import configure_logging

logger = logging.getLogger(__name__)


class VaultScanner:
    """Scans an Obsidian vault for markdown files to index."""

    def __init__(self, note_processor: NoteProcessor, database: Database):
        """Initialize the vault scanner.

        Args:
            note_processor: The note processor to use for processing files
            database: The database to store note metadata
        """
        self.note_processor = note_processor
        self.database = database

    def scan_existing_files(self):
        """Scan existing files in the vault and add them to the database.

        Returns:
            tuple: (processed_files, total_files, error_files)
        """
        vault_path = self.note_processor.vault_path
        logger.info(f"Scanning existing files in {vault_path}")

        # Get all markdown files
        markdown_files = list(vault_path.glob("**/*.md")) + list(vault_path.glob("**/*.markdown"))
        total_files = len(markdown_files)
        processed_files = 0
        error_files = 0

        logger.info(f"Found {total_files} markdown files to index")

        for file_path in markdown_files:
            try:
                metadata = self.note_processor.process_file(file_path)
                if metadata:
                    success = self.database.insert_or_update_note(metadata)
                    if success:
                        processed_files += 1
                    else:
                        error_files += 1
                        logger.error(f"Failed to index file during initial scan: {file_path}")

                    # Log progress periodically
                    if processed_files % 100 == 0 or processed_files == total_files:
                        logger.info(f"Indexed {processed_files}/{total_files} files")
            except Exception as e:
                logger.error(f"Error processing file during initial scan: {file_path}, Error: {e}")
                error_files += 1

        logger.info(
            f"Initial scan complete. Successfully indexed {processed_files} files. Errors: {error_files}"
        )
        return processed_files, total_files, error_files
