"""Database operations for note management."""

import sqlite3
import logging
from typing import Dict, List, Optional

from .connection import DatabaseConnection
from .errors import DatabaseError

logger = logging.getLogger(__name__)

class NoteOperations:
    """Manages note-related database operations."""
    
    def __init__(self, db_connection: DatabaseConnection):
        """
        Initialize with a database connection.
        
        Args:
            db_connection: An initialized DatabaseConnection instance
        """
        self.conn = db_connection.conn

    def insert_or_update_note(self, note_data: Dict) -> bool:
        """
        Insert or update a note in the database.
        
        Args:
            note_data (dict): Note metadata with required 'path' key
            
        Returns:
            bool: Success status of the operation
        """
        path = note_data.get('path', '')
        if not path:
            logger.error("Cannot process note with empty path")
            return False

        query = '''
            INSERT OR REPLACE INTO notes 
            (path, title, parent_folder, tags, created_date, modified_date, 
             content, status, error_message, last_indexed)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, datetime('now'))
        '''
        params = (
            path,
            note_data.get('title', ''),
            note_data.get('parent_folder', ''),
            note_data.get('tags', ''),
            note_data.get('created_date', ''),
            note_data.get('modified_date', ''),
            note_data.get('content', ''),
            note_data.get('status', 'success'),
            note_data.get('error_message', '')
        )

        return self._execute_transaction(query, params, f"insert/update note {path}")

    def delete_note(self, path: str) -> bool:
        """
        Delete a note from the database.
        
        Args:
            path (str): Path of the note to delete
            
        Returns:
            bool: Success status of the operation
        """
        if not path:
            logger.error("Cannot delete note with empty path")
            return False

        # Check if note exists before deletion
        exists_query = 'SELECT path FROM notes WHERE path = ?'
        if not self._execute_query(exists_query, (path,)).fetchone():
            logger.warning(f"Note not found for deletion: {path}")
            return False

        delete_query = 'DELETE FROM notes WHERE path = ?'
        return self._execute_transaction(delete_query, (path,), f"delete note {path}")

    def get_all_notes(self) -> List[Dict]:
        """
        Retrieve all notes from the database.
        
        Returns:
            list: List of note dictionaries
        """
        query = 'SELECT * FROM notes'
        try:
            with self.conn:
                cursor = self.conn.execute(query)
                return [dict(row) for row in cursor.fetchall()]
        except sqlite3.Error as e:
            logger.error(f"Failed to retrieve notes: {e}")
            return []

    def _execute_transaction(self, query: str, params: tuple, operation: str) -> bool:
        """Execute a database transaction with verification."""
        try:
            with self.conn:
                self.conn.execute('BEGIN IMMEDIATE')
                self.conn.execute(query, params)
                return True
        except sqlite3.Error as e:
            logger.error(f"Error during {operation}: {e}")
            return False

    def _execute_query(self, query: str, params: tuple) -> sqlite3.Cursor:
        """Execute a simple query and return cursor."""
        try:
            return self.conn.execute(query, params)
        except sqlite3.Error as e:
            logger.error(f"Query execution failed: {e}")
            raise DatabaseError(f"Query failed: {e}") 