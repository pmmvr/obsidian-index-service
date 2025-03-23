"""Database interface for the Obsidian indexing service."""

import logging
from typing import Dict, List

from .connection import DatabaseConnection
from .operations import NoteOperations

logger = logging.getLogger(__name__)

class Database:
    """Main database interface that combines connection and operations."""
    
    def __init__(self, db_path: str):
        """
        Initialize database components.
        
        Args:
            db_path (str): Path to the SQLite database file
        """
        self.connection = DatabaseConnection(db_path)
        self.notes = NoteOperations(self.connection)
        
    def close(self) -> None:
        """Close database connection."""
        self.connection.close()
        
    def insert_or_update_note(self, note_data: Dict) -> bool:
        """
        Insert or update a note in the database.
        
        Args:
            note_data (dict): Note metadata with required 'path' key
            
        Returns:
            bool: Success status of the operation
        """
        return self.notes.insert_or_update_note(note_data)
        
    def delete_note(self, path: str) -> bool:
        """
        Delete a note from the database.
        
        Args:
            path (str): Path of the note to delete
            
        Returns:
            bool: Success status of the operation
        """
        return self.notes.delete_note(path)
        
    def get_all_notes(self) -> List[Dict]:
        """
        Retrieve all notes from the database.
        
        Returns:
            list: List of note dictionaries
        """
        return self.notes.get_all_notes()
        
    def __enter__(self):
        """Support for context manager protocol."""
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Ensure connection is closed when using context manager."""
        self.close()