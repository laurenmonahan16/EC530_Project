import pandas
import sqlite3

class csvLoader: 

    def load_csv(filepath: str): 
        """
        read the csv, return dataframe
        """
        return pandas.read_csv(filepath)

    def validate_data(df: pandas.DataFrame) -> bool:
        """
        validation of data before its ingested 
        """
        pass

    def get_csv_schema(df: pandas.DataFrame) -> dict[str, str]:
        """
        map csv column -> SQL type (TEXT, INTEGER, REAL)
        """
        pass

    def insert_rows(conn, df: pandas.DataFrame, table_name: str) -> None:
        """
        insert DataFrame rows into an existing table
        """
        pass

    def ingest(conn, filepath: str, table_name: str, schema_manager) -> None:
        """
        executes: load -> validate -> check schema -> create or append -> insert
        """
        pass