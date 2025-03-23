"""Watches Obsidian vault directory for file changes."""

import time
import logging
from watchdog.observers import Observer

from .handlers import VaultEventHandler
from .scanner import VaultScanner
from .logging_config import configure_logging

logger = logging.getLogger(__name__)


class FileWatcher:
    """Watches an Obsidian vault directory for file changes."""

    def __init__(self, note_processor, database):
        """Initialize the file watcher.

        Args:
            note_processor: The note processor to use for processing files
            database: The database to store note metadata
        """
        self.note_processor = note_processor
        self.database = database
        self.observer = None
        self.event_handler = None
        self.scanner = VaultScanner(note_processor, database)

    def scan_existing_files(self):
        """Scan existing files in the vault and add them to the database.

        Returns:
            tuple: (processed_files, total_files, error_files)
        """
        return self.scanner.scan_existing_files()

    def start_watching(self):
        """Start watching the vault directory for changes."""
        vault_path = self.note_processor.vault_path
        logger.info(f"Starting to watch vault directory: {vault_path}")

        self.event_handler = VaultEventHandler(self.note_processor, self.database)
        self.observer = Observer()
        self.observer.schedule(self.event_handler, str(vault_path), recursive=True)
        self.observer.start()

        logger.info("File watcher started successfully")

        try:
            # Keep the main thread running while the observer thread works
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            self.stop_watching()

    def stop_watching(self):
        """Stop watching the vault directory."""
        if self.observer:
            self.observer.stop()
            self.observer.join()
            logger.info("File watcher stopped")

    def __del__(self):
        """Ensure observer is stopped when object is destroyed."""
        self.stop_watching()

