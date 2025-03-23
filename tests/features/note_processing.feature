Feature: Note Processing
  Feature: Note Processing
 
  As a user of the index service
  I want the service to process markdown notes, extracting their metadata and content for storage in the database.
  So that I can search for notes by their content and metadata.

  Scenario: Process a valid markdown note
    Given a valid markdown note with content and frontmatter
    When the note processor processes the file
    Then the note data should be stored in the database
    And the stored note should contain the correct content

  Scenario: Update an existing note
    Given a note that already exists in the database
    When the note is modified and processed again
    Then the database should be updated with the new content

  Scenario: Handle invalid markdown files
    Given an invalid markdown file
    When the note processor attempts to process the file
    Then an error should be recorded in the database 