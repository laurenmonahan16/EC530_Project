import sqlite3

class SchemaManager: 
    """
    SchemaManager is responsible for understanding the structure of the database
    """
    def __init__(self, conn):
        self.conn = conn
        self.cur = self.conn.cursor()

    def discover_existing_tables(self) -> list[str]:
        """
        returns a list of all table names in the database
        """
    
        self.cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables_tuple=(self.cur.fetchall())

        tables_list = []
        # extract only table name from each tuple
        for item in tables_tuple:
            tables_list.append(item[0])
        
        return tables_list

    def get_table_schema(self, table_name: str) -> dict[str, str]:
        """
        returns column name -> type mapping for the given table
        """      

        self.cur.execute(f"PRAGMA table_info('{table_name}')")
        info=self.cur.fetchall() #each row in info is a tuple- index 1 is col name and index 2 is type

        type_map={}
        for item in info:
            type_map[item[1]]= item[2]

        return type_map

    def get_all_schemas(self) -> dict[str, dict[str, str]]:
        """
        returns schemas for all tables in the database
        """      
        name_to_schema_map={}

        for item in self.discover_existing_tables():
            name_to_schema_map[item] = self.get_table_schema(item)

        return name_to_schema_map

    def table_already_exists(self, table_name: str) -> bool:
        """
        is there a table by this name that already exists in the database?
        """
        result = False

        existing_tables = self.discover_existing_tables()

        for item in existing_tables:
            if table_name == item:
                result=True 
        
        return result

    def schemas_match(self, new_schema:dict, existing_schema:dict) -> bool:
        """ 
        do column names match existing table? do data types match exactly?

        if true, append data
        if false, create new table

        - Prompt user on schema conflict: overwrite, rename, or skip
        - Log to error.txt

        """
        
        # remove id column from existing schema
        existing_schema_filtered = {}

        for column_name, type in existing_schema.items():
            if column_name != "id":
                existing_schema_filtered[column_name] = type

        # check if column names in new table match column names of existing table 
        if set(new_schema.keys()) != set(existing_schema_filtered.keys()):
            return False
        
        # check if data type in new_schema matches type in existing_schema
        for col in new_schema:
            if new_schema[col] != existing_schema_filtered[col]:
                return False

        return True

    def generate_create_statement(self, table_name: str, schema: dict[str, str]) -> str:
        """
        Returns the CREATE TABLE SQL string
        """
        name_and_type=[]
        for name, type in schema.items():
            name_and_type.append(f'"{name}" {type}')


        combined_string = ", ".join(name_and_type)
        statement= f'CREATE TABLE IF NOT EXISTS {table_name} (id INTEGER PRIMARY KEY AUTOINCREMENT, {combined_string})'

        return statement
    
    def execute_create(self, create_command:str):

       self.cur.execute(f'{create_command}')
       self.conn.commit()

    def drop_table(self, table_name: str) -> None:
        self.conn.execute(f"DROP TABLE IF EXISTS {table_name}")
        self.conn.commit()