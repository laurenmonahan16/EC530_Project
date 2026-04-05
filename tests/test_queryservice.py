import pytest
from sql_setup import get_connection, close_connection
from schema_manager import SchemaManager
from sql_validator import sqlValidator
from query_service import QueryService


@pytest.fixture
def setup():
    conn = get_connection(":memory:")
    manager = SchemaManager(conn)
    validator = sqlValidator(conn, manager)
    service = QueryService(conn, manager, validator)

    # create test table
    conn.execute("""
        CREATE TABLE siblings (
            id INTEGER PRIMARY KEY,
            name TEXT,
            age INTEGER
        )
    """)

    conn.execute("""
        INSERT INTO siblings (name, age)
        VALUES ('Mike', 27), ('Lauren', 21)
    """)

    conn.commit()

    yield service, conn

    close_connection(conn)


"""
testing validate_prompt() function
"""
def test_valid_prompt(setup):
    service, _ = setup

    valid, _ = service.validate_prompt("SELECT name FROM siblings")

    assert valid is True

def test_invalid_prompt(setup):
    service, _ = setup

    valid, error = service.validate_prompt("DROP TABLE siblings")

    assert valid is False
    assert "SELECT" in error


"""
testing execute_query() function
"""
def test_execute_query_valid(setup):
    service, _ = setup

    result = service.execute_query("SELECT name FROM siblings")

    assert "columns" in result
    assert "rows" in result
    assert result["columns"] == ["name"]
    assert len(result["rows"]) == 2

def test_execute_query_nonselect(setup):
    service, _ = setup

    with pytest.raises(ValueError):
        service.execute_query("DROP TABLE siblings")

def test_execute_query_unknown_table(setup):
    service, _ = setup

    with pytest.raises(ValueError):
        service.execute_query("SELECT * FROM fake_table")

def test_execute_query_unknown_column(setup):
    service, _ = setup

    with pytest.raises(ValueError):
        service.execute_query("SELECT fake_column FROM siblings")


"""
testing format_respose() function
"""
def test_format_response(setup):
    service, _ = setup

    result = {
        "columns": ["name", "age"],
        "rows": [("Mike", 27), ("Lauren", 21)]
    }

    formatted = service.format_respose(result)

    assert "name | age" in formatted
    assert "Mike | 27" in formatted
    assert "Lauren | 21" in formatted

def test_format_response_empty_rows(setup):
    service, _ = setup

    result = {
        "columns": ["name"],
        "rows": []
    }

    formatted = service.format_respose(result)

    # response should still show header
    assert formatted.strip() == "name"