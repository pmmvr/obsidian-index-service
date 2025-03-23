#!/usr/bin/env python3
import os
import sys
import logging
import argparse
import signal
from pathlib import Path

from dotenv import load_dotenv

from obsidian_index_service.config import Config
from obsidian_index_service.db.database import Database
from obsidian_index_service.note_processor.processor import NoteProcessor
from obsidian_index_service.file_watcher.watcher import FileWatcher

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Obsidian Index Service")
    parser.add_argument("--vault-path", help="Path to the Obsidian vault directory")
    parser.add_argument("--db-path", help="Path to the SQLite database file")
    parser.add_argument(
        "--scan-only",
        action="store_true",
        help="Only scan existing files without watching for changes",
    )
    return parser.parse_args()


def setup_signal_handlers(file_watcher, db):
    """Set up signal handlers for graceful shutdown.

    Args:
        file_watcher: The file watcher to stop
        db: The database connection to close
    """

    def signal_handler(sig, frame):
        logger.info("Received shutdown signal, stopping services...")
        file_watcher.stop_watching()
        db.close()
        logger.info("Shutdown complete, exiting")
        sys.exit(0)

    # Register signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)


def main():
    """Main entry point for the application."""
    try:
        # Load environment variables from .env file
        load_dotenv()

        args = parse_args()

        # Create configuration
        config = Config(
            vault_path=args.vault_path or os.getenv("OBSIDIAN_VAULT_PATH"),
            db_path=args.db_path or os.getenv("DB_PATH"),
        )

        # Initialize database
        db = Database(config.db_path)
        logger.info(f"Database initialized at: {config.db_path}")

        # Initialize note processor
        note_processor = NoteProcessor(config.vault_path)
        logger.info(f"Note processor initialized for vault: {config.vault_path}")

        # Initialize file watcher
        file_watcher = FileWatcher(note_processor, db)

        # Set up signal handlers for graceful shutdown
        setup_signal_handlers(file_watcher, db)

        # Perform initial scan of existing files
        logger.info("Starting initial scan of existing files...")
        file_watcher.scan_existing_files()

        # If scan-only mode, exit after scanning
        if args.scan_only:
            logger.info("Scan-only mode enabled, exiting after initial scan")
            db.close()
            return

        # Start monitoring for changes
        logger.info("Starting file monitoring service...")
        file_watcher.start_watching()  # This will block until interrupted

    except KeyboardInterrupt:
        logger.info("Application interrupted by user")
        # Cleanup is handled by signal handlers
    except Exception as e:
        logger.error(f"Error in main: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
