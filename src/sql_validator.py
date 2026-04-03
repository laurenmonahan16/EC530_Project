import sqlite3

class sqlValidator:

    def __init__(self, conn, schema_manager):
        self.conn = conn
        self.cur = self.conn.cursor()
        self.schema_manager = schema_manager

    def is_select_query(self, query: str) -> bool:
        """
        reject anything that is not a SELECT query
        """
        return query.strip().lower().startswith("select")


    def is_valid_table(self, query: str) -> bool:
        """ 
        reject queries referencing unknown tables
        """
        known_tables = self.schema_manager.discover_existing_tables()

        tokens = query.strip().split()
        upper_tokens = [t.upper() for t in tokens]
        
        if "FROM" not in upper_tokens:
            return False
        
        from_index = upper_tokens.index("FROM")
        
        if from_index + 1 >= len(tokens):
            return False
        
        table_name = tokens[from_index + 1].strip(";,")
        
        return table_name in known_tables


    def is_valid_column(self, query: str) -> bool:
        """
        reject queries referencing unknown columns
        """

        tokens = query.strip().split()
        upper_tokens = [t.upper() for t in tokens]

        if "FROM" not in upper_tokens:
            return False

        from_index = upper_tokens.index("FROM")
        table_name = tokens[from_index + 1].strip(";,")
        
        schema = self.schema_manager.get_table_schema(table_name)

        # extract everything between SELECT and FROM
        select_clause = " ".join(tokens[1:from_index])

        # wildcard is always valid
        if select_clause.strip() == "*":
            return True
        
        if '"' in select_clause:
            return True

        # split columns by comma and check each
        columns = [c.strip() for c in select_clause.split(",")]
        known_columns = schema.keys()

        for col in columns:
            col_clean = col.strip().strip('"')
            if col_clean not in known_columns:
                return False

        return True

    def validate(self, query: str) -> tuple[bool, str]:
        """
        runs all validation checks above
        returns (is_valid, error_message)
        """
        
        if not self.is_select_query(query):
            return (False, "Only SELECT queries are allowed") # stops here if fails

        if not self.is_valid_table(query):
            return (False, "Query references an unknown table") # stops here if fails

        if not self.is_valid_column(query):
            return (False, "Query references an unknown column") # stops here if fails

        return (True, "") # only valid if all three checks pass