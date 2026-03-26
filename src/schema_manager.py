
class SchemaManager: 
    """
    SchemaManager is responsible for understanding the structure of the database
    """
    def __init__(self, conn):
        self.conn = conn

    def discover_existing_tables(self) -> list[str]:
        """
        returns a list of all table names in the database
        """
        pass

    def get_table_schema(self, table_name: str) -> dict[str, str]:
        """
        - inspect column names and data types

        returns column name -> type mapping for the given table
        """      
        pass
    
    def get_all_schema(self) -> dict[str, dict[str, str]]:
        """
        inspect column names and data types

        returns schemas for all tables in the database
        """      
        pass

    def table_already_exists(self, table_name: str) -> bool:
        """
        is there a table by this name that already exists in the database?
        """
        pass

    def schemas_match(self, new_schema:dict, existing_schema:dict) -> bool:
        """ 
        do column names match existing table? do data types match exactly?

        if true, append data
        if false, create new table
        """
        pass

    def generate_create_statement(self, table_name: str, schema: dict[str, str]) -> str:
        """
        Returns the CREATE TABLE SQL string
        """
        pass