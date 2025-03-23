"""Database connection management."""

import os
import sqlite3
import logging
from pathlib import Path
from typing import Optional

from .errors import DatabaseError

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class DatabaseConnection:
    """Manages SQLite database connection and setup."""

    def __init__(self, db_path: str):
        """
        Initialize database connection and setup tables.

        Args:
            db_path (str): Path to the SQLite database file

        Raises:
            DatabaseError: If database initialization fails
        """
        self.db_path = db_path
        self.conn = None
        self._setup_database()

    def _setup_database(self) -> None:
        """Setup database directory and initialize tables."""
        self._ensure_db_directory()
        self._initialize_connection()
        self._create_tables()

    def _ensure_db_directory(self) -> None:
        """Create database directory if it doesn't exist."""
        db_dir = os.path.dirname(self.db_path)
        if db_dir:
            os.makedirs(db_dir, exist_ok=True)
            logger.info(f"Database directory ensured: {db_dir}")

    def _initialize_connection(self) -> None:
        """Initialize SQLite connection with optimal settings."""
        try:
            self.conn = sqlite3.connect(
                self.db_path, timeout=30.0, isolation_level=None, check_same_thread=False
            )
            self.conn.execute("PRAGMA journal_mode=WAL")
            self.conn.row_factory = sqlite3.Row
            logger.info(f"Database connection established: {self.db_path}")
        except sqlite3.Error as e:
            logger.error(f"Failed to initialize database connection: {e}")
            raise DatabaseError(f"Connection failed: {e}")

    def _create_tables(self) -> None:
        """Create necessary database tables if they don't exist."""
        try:
            with self.conn:
                self.conn.execute(
                    """
                    CREATE TABLE IF NOT EXISTS notes (
                        path TEXT PRIMARY KEY,
                        title TEXT,
                        parent_folder TEXT,
                        tags TEXT,
                        created_date TEXT,
                        modified_date TEXT,
                        content TEXT,
                        status TEXT DEFAULT 'success',
                        error_message TEXT,
                        last_indexed TEXT
                    )
                """
                )
            logger.info("Database tables verified/created")
        except sqlite3.Error as e:
            logger.error(f"Table creation failed: {e}")
            raise DatabaseError(f"Table creation failed: {e}")

    def close(self) -> None:
        """Safely close the database connection."""
        if self.conn:
            self.conn.close()
            self.conn = None
            logger.info("Database connection closed")

    def __enter__(self):
        """Support for context manager protocol."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Ensure connection is closed when using context manager."""
        self.close()

