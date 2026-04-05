import pytest
import pandas as pd
from sql_setup import get_connection, close_connection
from csv_loader import csvLoader
from schema_manager import SchemaManager


@pytest.fixture
def setup():
    conn = get_connection(":memory:")
    loader = csvLoader(conn)
    manager = SchemaManager(conn) 

    yield loader, manager

    close_connection(conn)

"""
testing load_csv() function
"""
def test_load_csv(setup):
    loader, _ = setup
    df = loader.load_csv("../data/sample.csv")
    
    assert len(df) == 3
    assert list(df.columns) == ["name", "age", "gender"]


"""
testing validate_data() function
"""
def test_empty_data(setup):
    loader, _ = setup
    df = loader.load_csv("../data/empty.csv")

    with pytest.raises(ValueError):
        loader.validate_data(df)

def test_duplicate_columns(setup):
    loader, _ = setup
    df = pd.DataFrame([[1, 2]], columns=["a", "a"])

    with pytest.raises(ValueError):
        loader.validate_data(df)

def test_unnamed_column(setup):
    loader, _ = setup
    df = pd.DataFrame([[1, 2]], columns=["a", "Unnamed : 1"])
    with pytest.raises(ValueError):
        loader.validate_data(df)

"""
testing get_csv_schema() function
"""
def test_get_schema(setup):
    loader, _ = setup
    
    df = pd.DataFrame({
        "int_col": [1, 2],
        "float_col": [1.5, 2.5],
        "text_col": ["a", "b"]
    })

    schema = loader.get_csv_schema(df)

    assert schema["int_col"] == "INTEGER"
    assert schema["float_col"] == "REAL"
    assert schema["text_col"] == "TEXT"


"""
testing insert_rows() function
"""
def test_insert_rows(setup):
    loader, manager = setup

    df = pd.DataFrame({
        "name": ["Lauren", "Mike"],
        "age": [21, 27]
    })

    # create table 
    create_statement = manager.generate_create_statement(
        "people",
        loader.get_csv_schema(df)
    )
    manager.execute_create(create_statement)

    # insert df into table
    loader.insert_rows(df, "people")

    # check results
    result = loader.conn.execute("SELECT name, age FROM people").fetchall()
    assert len(result) == 2
    assert result[0] == ("Lauren", 21)

"""
testing ingest() function
"""
def test_ingest_appends(setup):
    loader, manager = setup

    loader.ingest("../data/sample.csv", "Family", manager)
    loader.ingest("../data/sample.csv", "Family", manager) 

    result = loader.conn.execute("SELECT * FROM Family").fetchall()

    assert len(result) == 6  # 3 rows inserted twice

def test_ingest_mismatch_schema(setup):
    loader, manager = setup

    loader.ingest("../data/sample.csv", "Family", manager)
    with pytest.raises(ValueError):
        loader.ingest("../data/sample_modified.csv", "Family", manager) 

def test_ingest_overwrite_on_mismatch(setup):
    loader, manager = setup
    loader.ingest("../data/sample.csv", "Family", manager)
    loader.ingest("../data/sample_modified.csv", "Family", manager, on_conflict="overwrite")
    # verify new schema is in place
    schema = manager.get_table_schema("Family")
    assert "height" in schema