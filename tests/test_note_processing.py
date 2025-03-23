"""Test note processing functionality."""

import json
from pathlib import Path
import pytest
from pytest_bdd import scenarios, given, when, then, parsers

# Import test scenarios from the feature file
scenarios('./features/note_processing.feature')


@pytest.fixture
@given("a valid markdown note with content and frontmatter")
def valid_markdown_note(vault_path):
    """Create a valid markdown note with frontmatter and content."""
    note_path = vault_path / "test_note.md"
    with open(note_path, "w") as f:
        f.write("""---
tags: [test, example]
---

# Test Note

This is a test note with content.
""")
    return note_path


@pytest.fixture
@given("a note that already exists in the database")
def existing_note(vault_path, note_processor, note_operations):
    """Create and process a note so it exists in the database."""
    note_path = vault_path / "existing_note.md"
    with open(note_path, "w") as f:
        f.write("""---
tags: [existing]
---

# Existing Note

This is an existing note.
""")
    
    # Process the note to add it to the database
    note_data = note_processor.process_file(note_path)
    note_operations.insert_or_update_note(note_data)
    
    return note_path


@pytest.fixture
@given("an invalid markdown file")
def invalid_markdown_file(vault_path):
    """Create an 'invalid' markdown file (for test purposes, we'll create a file that causes an error)."""
    # Create a directory with same name as the test note to cause an error when trying to read it
    note_path = vault_path / "invalid_note.md"
    note_path.mkdir(exist_ok=True)
    
    return note_path


@pytest.fixture
@when("the note processor processes the file")
def process_note(note_processor, valid_markdown_note):
    """Process the valid markdown note."""
    note_data = note_processor.process_file(valid_markdown_note)
    return note_data


@pytest.fixture
@when("the note processor attempts to process the file")
def attempt_process_invalid_note(note_processor, invalid_markdown_file):
    """Attempt to process the invalid markdown file."""
    note_data = note_processor.process_file(invalid_markdown_file)
    return note_data


@pytest.fixture
@when("the note is modified and processed again")
def modify_and_reprocess_note(existing_note):
    """Modify the existing note and process it again."""
    with open(existing_note, "w") as f:
        f.write("""---
tags: [existing, updated]
---

# Updated Note

This note has been updated.
""")
    
    return existing_note


@then("the note data should be stored in the database")
def verify_note_stored(note_operations, process_note):
    """Verify the note data is stored in the database."""
    note_operations.insert_or_update_note(process_note)
    
    # Retrieve all notes and check if our note is there
    all_notes = note_operations.get_all_notes()
    assert len(all_notes) >= 1
    
    # Find our note
    processed_note = next((note for note in all_notes if note['path'] == process_note['path']), None)
    assert processed_note is not None


@then("the stored note should contain the correct content")
def verify_content_stored(note_operations, process_note):
    """Verify the note content is correctly stored."""
    note_operations.insert_or_update_note(process_note)
    
    # Retrieve all notes
    all_notes = note_operations.get_all_notes()
    processed_note = next((note for note in all_notes if note['path'] == process_note['path']), None)
    
    # Check content
    assert "This is a test note with content." in processed_note['content']
    
    # Check tags
    tags = json.loads(processed_note['tags'])
    assert "test" in tags
    assert "example" in tags


@then("the database should be updated with the new content")
def verify_note_updated(note_processor, note_operations, modify_and_reprocess_note):
    """Verify the note is updated in the database."""
    # Process the modified note
    updated_note_data = note_processor.process_file(modify_and_reprocess_note)
    note_operations.insert_or_update_note(updated_note_data)
    
    # Retrieve all notes
    all_notes = note_operations.get_all_notes()
    updated_note = next((note for note in all_notes if note['path'] == updated_note_data['path']), None)
    
    # Check updated content
    assert "This note has been updated." in updated_note['content']
    
    # Check updated tags
    tags = json.loads(updated_note['tags'])
    assert "updated" in tags


@then("an error should be recorded in the database")
def verify_error_recorded(note_operations, attempt_process_invalid_note):
    """Verify an error is recorded in the database."""
    note_operations.insert_or_update_note(attempt_process_invalid_note)
    
    # Retrieve all notes
    all_notes = note_operations.get_all_notes()
    error_note = next((note for note in all_notes if note['path'] == attempt_process_invalid_note['path']), None)
    
    # Check error status
    assert error_note['status'] == 'error'
    assert error_note['error_message'] != '' 