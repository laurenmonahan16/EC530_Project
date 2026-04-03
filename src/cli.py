from sql_setup import get_connection, close_connection
from csv_loader import csvLoader
from schema_manager import SchemaManager
from sql_validator import sqlValidator
from query_service import QueryService
from llm_adapter import llmAdapter

def main():
    conn = get_connection("database.db")
    manager = SchemaManager(conn)
    loader = csvLoader(conn)
    validator = sqlValidator(conn, manager)
    query_handler = QueryService(conn, manager, validator)
    adapter = llmAdapter(manager)

    print("Welcome!")

    while True:

        command = input("\n> ").strip()

        if command.startswith("ingest"):
            try:
                _, path, table = command.split()
                loader.ingest(path, table, manager)
            except ValueError:
                print("Usage: ingest <path> <table_name>")

        elif command.startswith("query"):
            query = command[len("query"):].strip()
            try:
                result = query_handler.execute_query(query)
                print(query_handler.format_respose(result))
            except ValueError as e:
                print(f"Error: {e}")

        elif command.startswith("ask"):
            user_request = command[len("ask"):].strip()
            
            sql = adapter.generate_sql(user_request)
            print(f"\nGenerated SQL:\n{sql}\n")

            try:
                result = query_handler.execute_query(sql)
                print(query_handler.format_respose(result))
            except ValueError as e:
                print(f"Error: {e}")

        elif command == "tables":
            tables = manager.discover_existing_tables()
            for t in tables:
                print(t)

        elif command.startswith("schema"):
            _, table = command.split()
            schema = manager.get_table_schema(table)
            for col, typ in schema.items():
                print(f"{col} ({typ})")

        elif command == "exit":
            break
        
        elif command == "help":
            print("Commands:")
            print("  ingest <path> <table>  - load a CSV file")
            print("  query <sql>            - run a SQL query")
            print("  ask <question>         - natural language query")
            print("  tables                 - list all tables")
            print("  schema <table>         - show table schema")
            print("  exit                   - quit")

        else:
            print("Unknown command")

    close_connection(conn)


if __name__ == "__main__":
    main()