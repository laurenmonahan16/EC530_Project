import pandas
import numpy as np
import sqlite3
import logging
from schema_manager import SchemaManager

logging.basicConfig(filename='error_log.txt', level=logging.WARNING)

class csvLoader: 

    def __init__(self, conn):
        self.conn = conn
        self.cur = conn.cursor()

    def load_csv(self, filepath: str): 
        """
        read the csv, return dataframe
        """
        return pandas.read_csv(filepath, sep=None, engine="python" )

    def validate_data(self, df: pandas.DataFrame):
        """
        validation of data before its ingested **raises errors/logs warnings, does not change data
        """
        # check for empty df
        if df.empty: 
            raise ValueError("CSV is empty")
    
        # check for empty entries
        null_entries = df.reset_index(drop=True).isnull()
        for col in null_entries.columns:
            for row, is_null in null_entries[col].items():
                if is_null:
                    #log empty entry to error.txt
                    logging.warning(f"Missing value at row {row}, column '{col}'")               

        # check for empty column names
        for i, col in enumerate(df.columns):
            if str(col).strip() == "":
                raise ValueError(f"Empty column name found at index {i}")
            elif str(col).startswith("Unnamed"):
                raise ValueError(f"Unnamed column found at index {i}")

        # check for duplicate column names
        if df.columns.duplicated().any(): 
            duplicates = df.columns[df.columns.duplicated()].tolist()
            raise ValueError(f"Duplicate column names: {duplicates}")

    def get_csv_schema(seld, df: pandas.DataFrame) -> dict[str, str]:
        """
        map csv column -> SQL type (TEXT, INTEGER, REAL)
        """
        type_map = {}

        for column, dtype in df.dtypes.items():
            if "int" in str(dtype):
                type_map[column] = "INTEGER"
            elif  "float" in str(dtype): 
                type_map[column] = "REAL"
            else:
                type_map[column] = "TEXT"

        return type_map

    def insert_rows(self, df: pandas.DataFrame, table_name: str) -> None:
        """
        insert DataFrame rows into an existing table
        """
        col_names = df.columns.tolist()
        col_names_as_string = ", ".join(f'"{col}"' for col in col_names)
        temp_values = ", ".join(["?"]*len(col_names))

        #build insert command
        sql_insert = f'INSERT INTO {table_name} ({col_names_as_string}) VALUES ({temp_values})'
        
        #cleanup rows for data insertion
        rows = []

        for row in df.itertuples(index=False, name=None):
            # if empty entry in csv, replace with "None" so sql can read it 
            clean_row = []
            for entry in row:
                if pandas.isna(entry):
                    clean_row.append(None)
                else:
                    clean_row.append(entry)
            clean_row = tuple(clean_row)
            rows.append(clean_row)
        
        # execute insertion
        self.conn.executemany(sql_insert, rows)
        self.conn.commit()

    def ingest(self, filepath: str, table_name: str, schema_manager: SchemaManager, on_conflict: str = "error") -> None:
        """
        executes: load -> validate -> check schema -> create or append -> insert
        """
        # load the csv 
        df = self.load_csv(filepath)

        # validate data
        try:
            self.validate_data(df)
        except ValueError as e:
            print(f"Validation error: {e}")

        # get schema of the csv
        csv_schema = self.get_csv_schema(df)

        # check if table already exists
        name_exists = schema_manager.table_already_exists(table_name)

        # if exists, check if schemas match
        if name_exists:
            existing_schema = schema_manager.get_table_schema(table_name)
 
            schema_matches = schema_manager.schemas_match(csv_schema, existing_schema)

            if schema_matches:
                # append data to existing table 
                self.insert_rows(df, table_name)
            else: 
                #cli will prompt user on what they want to do in event of schema mismatch
                    # 1) overwrite the one that exists by same name? 
                    # 2) rename the table being ingested? 
                    # 3) skip ingestion entirely?

                if on_conflict == "skip":
                    print(f"Skipping ingestion for '{table_name}' due to schema mismatch")
                    return
                elif on_conflict == "overwrite":
                    schema_manager.drop_table(table_name)
                    create_statement = schema_manager.generate_create_statement(table_name, csv_schema)
                    schema_manager.execute_create(create_statement)
                    self.insert_rows(df, table_name)
                elif on_conflict == "rename":
                    create_statement = schema_manager.generate_create_statement(table_name, csv_schema)
                    schema_manager.execute_create(create_statement)
                    self.insert_rows(df, table_name)
                else:
                    raise ValueError(f"Schema mismatch for table '{table_name}'")
        
        else:
            #no table by that name exists yet, create new table & insert data
            create_statement = schema_manager.generate_create_statement(table_name, csv_schema)
            schema_manager.execute_create(create_statement)

            self.insert_rows(df, table_name)