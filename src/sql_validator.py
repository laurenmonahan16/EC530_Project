
def is_select_query(query: str) -> bool:
    """
    reject anything that is not a SELECT query
    """
    pass

def is_valid_table(query: str, known_tables: list[str]) -> bool:
    """ 
    reject queries referencing unknown tables
    """
    pass

def is_valid_column(query: str, schema: dict[str, dict[str, str]]) -> bool:
    """
    reject queries referencing unknown columns
    """
    pass

def validate(query: str, schema: dict[str, dict[str, str]]) -> tuple[bool, str]:
    """
    runs all validation checks above

    returns (is_valid, error_message) for each check in tuple
    """
    pass