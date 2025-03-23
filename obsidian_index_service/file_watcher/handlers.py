"""Event handlers for file system events in the Obsidian vault."""

import logging
from pathlib import Path
from watchdog.events import FileSystemEventHandler

from .logging_config import configure_logging

logger = logging.getLogger(__name__)

class VaultEventHandler(FileSystemEventHandler):
    """Event handler for Obsidian vault file system events."""
    
    def __init__(self, note_processor, database):
        """Initialize the vault event handler.
        
        Args:
            note_processor: The note processor to use for processing files
            database: The database to store note metadata
        """
        self.note_processor = note_processor
        self.database = database
        super().__init__()
        
    def on_created(self, event):
        """Handle file creation events.
        
        Args:
            event: The file system event
        """
        if event.is_directory:
            return
            
        file_path = Path(event.src_path)
        if self.note_processor.is_markdown_file(file_path):
            logger.info(f"New file created: {file_path}")
            metadata = self.note_processor.process_file(file_path)
            if metadata:
                success = self.database.insert_or_update_note(metadata)
                if not success:
                    logger.error(f"Failed to index new file: {file_path}")
    
    def on_modified(self, event):
        """Handle file modification events.
        
        Args:
            event: The file system event
        """
        if event.is_directory:
            return
            
        file_path = Path(event.src_path)
        if self.note_processor.is_markdown_file(file_path):
            logger.info(f"File modified: {file_path}")
            metadata = self.note_processor.process_file(file_path)
            if metadata:
                success = self.database.insert_or_update_note(metadata)
                if not success:
                    logger.error(f"Failed to update index for modified file: {file_path}")
    
    def on_deleted(self, event):
        """Handle file deletion events.
        
        Args:
            event: The file system event
        """
        if event.is_directory:
            return
            
        file_path = Path(event.src_path)
        if self.note_processor.is_markdown_file(file_path):
            try:
                # Get relative path to delete from database
                rel_path = file_path.relative_to(self.note_processor.vault_path)
                logger.info(f"File deleted: {rel_path}")
                success = self.database.delete_note(str(rel_path))
                if not success:
                    logger.error(f"Failed to remove deleted file from index: {rel_path}")
            except ValueError:
                logger.error(f"Error determining relative path for deleted file: {file_path}")
    
    def on_moved(self, event):
        """Handle file move/rename events.
        
        Args:
            event: The file system event
        """
        if event.is_directory:
            return
            
        src_path = Path(event.src_path)
        dest_path = Path(event.dest_path)
        
        # Only process markdown files
        if self.note_processor.is_markdown_file(src_path) or self.note_processor.is_markdown_file(dest_path):
            try:
                # Get relative path to delete old entry
                rel_src_path = src_path.relative_to(self.note_processor.vault_path)
                logger.info(f"File moved/renamed: {rel_src_path} -> {dest_path}")
                
                # Delete old entry
                delete_success = self.database.delete_note(str(rel_src_path))
                if not delete_success:
                    logger.error(f"Failed to delete old path during move: {rel_src_path}")
                
                # Process and add new entry if destination is still a markdown file
                if self.note_processor.is_markdown_file(dest_path):
                    metadata = self.note_processor.process_file(dest_path)
                    if metadata:
                        insert_success = self.database.insert_or_update_note(metadata)
                        if not insert_success:
                            logger.error(f"Failed to add new path during move: {dest_path}")
            except ValueError as e:
                logger.error(f"Error handling moved file: {e}") 