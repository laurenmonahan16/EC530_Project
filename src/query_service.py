
import sqlite3

class QueryService:

    def __init__(self, conn, schema_manager, validator):
        self.conn = conn
        self.cur = self.conn.cursor()
        self.schema_manager = schema_manager
        self.validator = validator


    def validate_prompt(self, query:str) -> tuple[bool, str]:
        """
        calls sql validator 
        """
        return self.validator.validate(query)


    def execute_query(self, query:str) -> dict:
        """
        execute a validated query, return results
        """
        
        is_valid, error_message = self.validate_prompt(query) 

        if is_valid:
            self.cur.execute(query)
            return {
                "columns": [desc[0] for desc in self.cur.description],
                "rows": self.cur.fetchall()
            }
        else:
            raise ValueError(error_message)
      
        
    def format_respose(self, results: dict) -> str:
        """
        format query results for display
        """ 
        columns = results["columns"]
        rows = results["rows"]

        # col names become the header
        header = " | ".join(columns)

        # loop over results and format each row        
        lines = []
        lines.append(header)

        for row in rows:
            row_str = " | ".join(str(value) for value in row)
            lines.append(row_str)
        return "\n".join(lines)