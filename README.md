# EC530 Project: Data Systems with LLM Interfaces

## System Overview

This system allows users to load structured CSV data into a SQLite database 
and query it using either raw SQL or natural language. Natural language queries 
are translated to SQL using the Anthropic Claude API.

### Modules

- **db_connection** — manages SQLite connections
- **csv_loader** — loads, validates, and ingests CSV files into the database
- **schema_manager** — understands and manages the structure of the database
- **sql_validator** — validates SQL queries before execution (only supports SELECT queries that reference tables/columns known in the system)
- **query_service** — orchestrates query validation, execution, and response formatting
- **llm_adapter** — translates natural language to SQL using Claude API
- **cli** — command line interface for interacting with the system

### Architecture

**Ingestion:** CLI → CSV Loader → Schema Manager → SQLite

**SQL Query:** CLI → Query Service → SQL Validator → SQLite

**Natural Language Query:** CLI → Query Service → LLM Adapter → SQL Validator → SQLite

## How to run project

### Install dependencies
```bash
pip install -r requirements.txt
```

### Set your API key
```bash
export ANTHROPIC_API_KEY="your-key"
```

### Run the CLI
```bash
cd src
python cli.py
```

### Available commands

ingest <path> <tablename>  - load a CSV file into the database
query <sql>                - run a SQL query
ask <question>             - natural language query
tables                     - retrieve a list of all tables stored in databae
schema <table>             - show table schema
exit                       - quit

## How to run tests
```bash
pip install pytest
pytest
```

## Design Decisions
- **Each module is a class that takes `conn` in `__init__`** 
    — Rather than passing the connection to every method call, each class owns its connection. All modules share the same connection object so they operate on the same database state without reconnecting.

- **CLI never touches the database directly**
    — All queries go through QueryService, which enforces validation before execution. This means no SQL can reach the database without being checked, regardless of where it came from.

- **Validation errors raise exceptions, missing values log warnings** 
    — Structural problems like duplicate columns stop ingestion entirely. Missing cell values are logged to error_log.txt and inserted as NULL, since a partial row is still useful data.

- **Table schema conflicts are handled by on_conflict parameter in ingest()** 
    — User prompting lives in the CLI, not inside ingestion logic to maintain separation between the interface and the data layer. CLI prompts user to overwrite, rename table, or skip ingestion when conflict occurs. 

- **In-memory SQLite is used for tests** 
    — Using `:memory:` gives each test a clean database with no setup or cleanup needed, making tests fast and isolated