import pytest
from sql_setup import get_connection, close_connection
from schema_manager import SchemaManager

@pytest.fixture
def setup():
    conn = get_connection(":memory:")
    manager = SchemaManager(conn)

    yield manager

    close_connection(conn)

"""
testing discover_existing_tables function
"""
def test_discover_existing_tables_empty(setup):
    manager = setup

    tables = manager.discover_existing_tables()

    assert tables == []

def test_discover_existing_tables(setup):
    manager = setup

    manager.execute_create("""
        CREATE TABLE test_table (
            id INTEGER PRIMARY KEY,
            name TEXT
        )
    """)

    tables = manager.discover_existing_tables()

    assert "test_table" in tables

"""
testing get_table_schema() function
"""
def test_get_table_schema(setup):
    manager = setup

    manager.execute_create("""
        CREATE TABLE people (
            id INTEGER PRIMARY KEY,
            name TEXT,
            age INTEGER
        )
    """)

    schema = manager.get_table_schema("people")

    assert schema["name"] == "TEXT"
    assert schema["age"] == "INTEGER"

"""
testing get_all_schemas() function
"""
def test_get_all_schemas(setup):
    manager = setup

    manager.execute_create("""
        CREATE TABLE table1 (
            id INTEGER PRIMARY KEY,
            col1 TEXT
        )
    """)

    manager.execute_create("""
        CREATE TABLE table2 (
            id INTEGER PRIMARY KEY,
            col2 INTEGER
        )
    """)

    schemas = manager.get_all_schemas()

    assert "table1" in schemas
    assert "table2" in schemas
    assert schemas["table1"]["col1"] == "TEXT"
    assert schemas["table2"]["col2"] == "INTEGER"

"""
testing table_already_exists function
"""
def test_table_exists_true(setup):
    manager = setup

    manager.execute_create("""
        CREATE TABLE test (
            id INTEGER PRIMARY KEY
        )
    """)

    assert manager.table_already_exists("test") is True

def test_table_exists_false(setup):
    manager = setup

    assert manager.table_already_exists("nonexistent") is False

"""
testing schemas_match() function
"""
def test_schemas_match_true(setup):
    manager = setup

    existing_schema = {
        "id": "INTEGER",
        "name": "TEXT",
        "age": "INTEGER"
    }

    new_schema = {
        "name": "TEXT",
        "age": "INTEGER"
    }

    assert manager.schemas_match(new_schema, existing_schema) is True

def test_schemas_mismatch_columns(setup):
    manager = setup

    existing_schema = {
        "id": "INTEGER",
        "name": "TEXT"
    }

    new_schema = {
        "name": "TEXT",
        "age": "INTEGER"
    }

    assert manager.schemas_match(new_schema, existing_schema) is False

def test_schemas_mismatch_types(setup):
    manager = setup

    existing_schema = {
        "id": "INTEGER",
        "name": "TEXT",
        "age": "INTEGER"
    }

    new_schema = {
        "name": "TEXT",
        "age": "REAL"
    }

    assert manager.schemas_match(new_schema, existing_schema) is False

"""
testing generate_create_statement() function
"""
def test_generate_create_statement(setup):
    manager = setup

    schema = {
        "name": "TEXT",
        "age": "INTEGER"
    }

    statement = manager.generate_create_statement("people", schema)

    assert "CREATE TABLE IF NOT EXISTS people" in statement
    assert '"name" TEXT' in statement
    assert '"age" INTEGER' in statement

"""
testing execute_create() function
"""
def test_execute_create(setup):
    manager = setup

    create_statement = """
        CREATE TABLE test_create (
            id INTEGER PRIMARY KEY,
            name TEXT
        )
    """

    manager.execute_create(create_statement)

    tables = manager.discover_existing_tables()

    assert "test_create" in tables

"""
testing drop_table() function
"""
def test_drop_table(setup):
    manager = setup

    manager.execute_create("""
        CREATE TABLE to_delete (
            id INTEGER PRIMARY KEY
        )
    """)

    assert manager.table_already_exists("to_delete")

    manager.drop_table("to_delete")

    assert not manager.table_already_exists("to_delete")