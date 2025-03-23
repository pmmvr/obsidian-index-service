"""Logging configuration for file watcher."""

import logging

def configure_logging():
    """Configure logging for the file watcher module."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    return logging.getLogger(__name__) 