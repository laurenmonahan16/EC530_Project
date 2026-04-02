import os
import anthropic

api_key = os.environ.get("ANTHROPIC_API_KEY")

class llmAdapter:

    def __init__(self, schema_manager):
        self.schema_manager = schema_manager


    def build_prompt(self, user_request:str) ->str:
        """
        Pass table schema and user request to an LLM
        """

        # get all table schemas and format as a string
        all_schemas = self.schema_manager.get_all_schemas()

        descriptions =[]

        for table_name, columns in all_schemas.items():
            column_descriptions = ", ".join(f"{col} ({type})" for col, type in columns.items())
            description = f"Table: {table_name}\n  Columns: {column_descriptions}"
            descriptions.append(description)

        all_descriptions = "\n".join(descriptions)
        
        # build the prompt
        prompt = f"""You are an AI assistant that converts natural language to SQLite SQL queries.
        
            The database has the following tables:
            {all_descriptions}.
            
            The user asked: {user_request}
            
            Return ONLY a valid SQLite SELECT query with no explanation, no markdown, no backticks.
            """

        return prompt


    def generate_sql(self, user_request:str) ->str:
        """
        AI generates sql that is passed to query service, display results
        """
        client = anthropic.Anthropic(api_key=api_key)
    
        prompt = self.build_prompt(user_request)
        
        # send request
        message = client.messages.create(
            model="claude-opus-4-6",
            max_tokens=1024,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        
        return message.content[0].text.strip()


