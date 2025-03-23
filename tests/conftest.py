"""Test fixtures for pytest."""

import os
import tempfile
import pytest
from pathlib import Path
from pytest_bdd import given, when, then, parsers

from obsidian_index_service.db.connection import DatabaseConnection
from obsidian_index_service.db.operations import NoteOperations
from obsidian_index_service.note_processor.processor import NoteProcessor


@pytest.fixture
def temp_dir():
    """Create a temporary directory for tests."""
    with tempfile.TemporaryDirectory() as temp_dir:
        yield Path(temp_dir)


@pytest.fixture
def vault_path(temp_dir):
    """Create a temporary Obsidian vault."""
    vault_dir = temp_dir / "test_vault"
    vault_dir.mkdir()
    return vault_dir


@pytest.fixture
def db_path(temp_dir):
    """Create a path for the test database."""
    return str(temp_dir / "test.db")


@pytest.fixture
def db_connection(db_path):
    """Create a test database connection."""
    conn = DatabaseConnection(db_path)
    yield conn
    conn.close()


@pytest.fixture
def note_operations(db_connection):
    """Create note operations for testing."""
    return NoteOperations(db_connection)


@pytest.fixture
def note_processor(vault_path):
    """Create a note processor for testing."""
    return NoteProcessor(str(vault_path)) 