import os
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class Config:
    def __init__(self, vault_path=None, db_path=None):
        """Initialize configuration with paths.
        
        Args:
            vault_path (str, optional): Path to the Obsidian vault. Defaults to environment variable.
            db_path (str, optional): Path to the SQLite database. Defaults to environment variable.
        """
        # Set default vault path from environment variable or use provided one
        self.vault_path = vault_path or os.environ.get("OBSIDIAN_VAULT_PATH")
        if not self.vault_path:
            error_msg = "Vault path not specified in environment variable OBSIDIAN_VAULT_PATH or constructor"
            logger.error(error_msg)
            raise ValueError(error_msg)
        
        # Ensure vault path is absolute
        self.vault_path = os.path.abspath(self.vault_path)
        if not os.path.isdir(self.vault_path):
            error_msg = f"Vault path does not exist or is not a directory: {self.vault_path}"
            logger.error(error_msg)
            raise ValueError(error_msg)
        
        logger.info(f"Vault path set to: {self.vault_path}")
        
        # Set default database path from environment variable or use provided one
        db_default = os.path.join(os.getcwd(), "data", "notes.sqlite")
        self.db_path = db_path or os.environ.get("DB_PATH", db_default)
        
        # Ensure db_path is absolute
        self.db_path = os.path.abspath(self.db_path)
        logger.info(f"Database path set to: {self.db_path}")
        
    @property
    def file_extensions(self):
        """List of file extensions to monitor and index.
        
        Returns:
            list: List of file extensions (e.g., ['.md'])
        """
        return ['.md'] 