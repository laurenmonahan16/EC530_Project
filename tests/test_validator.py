import pytest
import os

from conftest import DATA_DIR
from sql_setup import get_connection, close_connection
from csv_loader import csvLoader
from schema_manager import SchemaManager
from sql_validator import sqlValidator
from query_service import QueryService

@pytest.fixture
def validator():
    conn = get_connection(":memory:")

    manager = SchemaManager(conn)
    loader = csvLoader(conn)
    loader.ingest(os.path.join(DATA_DIR, "sample.csv"), "Family", manager)
    validator = sqlValidator(conn, manager)
    return validator

"""
testing is_select_query
"""
def test_nonselect_query(validator):
    query = "DELETE * FROM Family" 
    assert validator.is_select_query(query) is False

def test_select_query(validator):
    query = "SELECT * FROM Family LIMIT 2"
    assert validator.is_select_query(query) is True
    query2 = "select * from Family"
    assert validator.is_select_query(query2) is True

def test_empty_query(validator):
    assert validator.is_select_query("") is False

"""
testing is_valid_table
"""
def test_invalid_table(validator):
    query = "SELECT * FROM Lauren"
    assert validator.is_valid_table(query) is False

def test_valid_table(validator):
    query = "select * from Family"
    assert validator.is_valid_table(query) is True

def test_no_from_clause(validator):
    query = "SELECT * WHERE age > 6"
    assert validator.is_valid_table(query) is False

"""
testing is_valid_column
"""
def test_invalid_column(validator):
    query = "SELECT * FROM Family where height > 6"
    assert validator.is_valid_column(query) is False

def test_valid_column(validator):
    query = "SELECT * FROM Family where age > 18"
    assert validator.is_valid_column(query) is True

"""
testing validate
"""
def test_validate_fail(validator):
    query = "DROP TABLE Family"
    result = validator.validate(query)
    assert result[0] is False

def test_validate_pass(validator):
    query = "SELECT * FROM Family where age > 6"
    result = validator.validate(query)
    assert result[0] is True 
    assert result[1] == ""