# Obsidian Index Service

This service monitors an Obsidian vault directory and indexes Markdown files—metadata *and* full content—into an SQLite database. I built it to work with my `mcp-server` project, but switched to an implementation that uses the Obsidian plugin API instead. I still see use for this as an agnostic note indexer or sync tool (see note under "Future Steps"), so I'm putting it up here.

## Functionality

It tracks file changes (create, modify, delete) in an Obsidian vault and stores everything in SQLite, accessible via a Docker volume. It captures:
- **Path**: File path (unique identifier)
- **Title**: From filename
- **Parent Folders**: Relative to vault root
- **Tags**: From YAML frontmatter
- **Created Date**: Filesystem timestamp
- **Modified Date**: Filesystem timestamp
- **Content**: Full text of the note
- **Status**: Processing outcome (success/error)
- **Error Message**: Details if processing fails

## Setup and Usage

### Prerequisites
- Python 3.12 or later
- Docker and Docker Compose (for containerized use)
- `uv` (optional, but recommended)


### Installation
1. Clone the repo:
   ```bash
    git clone https://github.com/pmmvr/obsidian-index-service.git
    cd obsidian-index-service
   ```

2. Set up a virtual environment:
   - With `uv` (recommended):
     ```bash
     uv venv
     source .venv/bin/activate # Linux/macOS
     .venv\Scripts\activate # Windows
     ```

   - With `python` (standard):
     ```bash
     python -m venv .venv
     source .venv/bin/activate  # Linux/macOS
     .venv\Scripts\activate     # Windows
     ```

3. Install dependencies:
   - With `uv` (recommended):
     ```bash
     uv sync  # Installs from uv.lock
     uv pip install pytest pytest-bdd pytest-mock  # For tests
     ```
   - With `pip`:
     ```bash
     pip install -e .
     pip install pytest pytest-bdd pytest-mock  # For tests
     ```

### Running Locally
Set environment variables:
```bash
export OBSIDIAN_VAULT_PATH=/path/to/vault
export DB_PATH=/path/to/notes.sqlite
```

Run it:
```bash
python main.py
```

With `uv`:
```bash
uv run python main.py
```

For a one-time scan:
```bash
python main.py --scan-only
```

Or with `uv`:
```bash
uv run python main.py --scan-only
```

### Command-Line Options
- `--vault-path`: Path to vault directory
- `--db-path`: Path to SQLite database
- `--scan-only`: Scan without watching

### Using Docker
1. Build and run:
   ```bash
   docker-compose up -d
   ```
2. It mounts your vault and exposes the SQLite database.

### Read-Only Access for Other Services
To let another service read the database (e.g., for scanning changes):
1. Use the same volume as `obsidian-index-service` in your `docker-compose.yml`:
   ```yaml
   services:
     your-service:
       image: your-image
       volumes:
         - ${DB_VOLUME_PATH:-./data}:/data:ro  # Read-only mount
   ```
2. `Obsidian Index Service` writes to `/data/notes.sqlite` (mounted read-write), while other services (e.g. an mcp-server) read it. SQLite's WAL mode handles concurrent access.


## How It Works

The Obsidian Index Service operates through the following process:
1. **Startup** (`ObsidianIndexService.__init__`)
   - Loads configuration from environment variables or command-line arguments
   - Initializes the database connection (`DatabaseConnection`)
   - Sets up the note processor (`NoteProcessor`)
   - Establishes signal handlers for graceful shutdown

2. **Database Initialization** (`DatabaseConnection.__init__`)
   - Creates/connects to an SQLite database
   - Sets up the database in WAL (Write-Ahead Logging) mode for better concurrency
   - Creates a 'notes' table if it doesn't exist with columns for path, title, tags, etc.

3. **Initial Vault Scan** (`NoteProcessor.scan_vault`)
   - Finds all Markdown files (*.md, *.markdown) in the vault directory
   - For each file, extracts metadata
   - Adds all extracted metadata to the database (`NoteOperations.insert_note`)

4. **Continuous Monitoring** (`FileWatcher.watch`)
   - Watches the vault directory for file system events
   - Processes different types of events:
     - File creation: Indexes new files
     - File modification: Updates index for changed files
     - File deletion: Removes entries from the index
     - File movement/renaming: Updates path information

5. **File Processing** (`NoteProcessor.process_note`)
   - Extracts metadata from Markdown files
   - Includes path, title, parent folders, tags, created/modified dates
   - Updates the database with this information (`NoteOperations.upsert_note`)

6. **Graceful Shutdown** (`ObsidianIndexService.shutdown`)
   - Properly closes file watchers and database connections when receiving termination signals

The service operates in the background, continuously keeping the SQLite database in sync with the Obsidian vault. Other applications can then use this database to access note metadata without having to parse Markdown files directly.

## Development
Run tests:
```bash
pytest
```

## Project Status
- **Done**: Core indexing (metadata + content), Docker setup, file watching, database CRUD.
- **Next**: Planned an API, but went with the plugin approach instead.

## Future Steps (Sync Tool Potential)
With some rework I can see this as a sync tool:
- **Remote Backend**: Add support for cloud storage (e.g., Dropbox) or a server.
- **Sync Logic**: Push local changes (content + metadata) to remote, pull remote updates, handle conflicts (e.g., last-write-wins).
- **Database Tweaks**: Add `sync_status` and `remote_id` columns.
- **File Watcher Updates**: Queue changes for sync, not just indexing.
- **CLI Option**: Add `--sync` to trigger it manually or continuously.
- **Error Handling**: Retry on network fails, log issues.
