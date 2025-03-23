# Obsidian Index Service Tests

Some quick E2E tests to validate the service is working as expected.

Uses pytest-bdd, for now we only test:

- Processing valid markdown notes with content and metadata
- Updating existing notes in the database
- Error handling for invalid files

## Running the Tests

To run 
```bash
uv pip install -e .[dev]
```

Then run:

```bash
pytest tests/
```

Or for more detailed output:

```bash
pytest tests/ -v
```