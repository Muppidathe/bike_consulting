#langgraph_agent.py
import json
from langchain_core.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq
import mysql.connector
from mysql.connector import Error
from langchain_core.output_parsers import JsonOutputParser
import re
####################### start of dependency ############
def connect():
    try:
        db= mysql.connector.connect(
            host="localhost",
            port=3306,
            user="root",
            password="",
            database="sasi_kannan"
        )
        return db
    except Error as e:
        print("Error while connecting to MySQL", e)
        return None
#node-1 dependency
def get_schema() -> str:
    try: 
        db=connect()
        if db.is_connected():
            cursor=db.cursor()        
            # Fetch list of tables
            cursor.execute("SHOW TABLES")
            tables = cursor.fetchall()
            
            schema_details = {}
            
            for (table_name,) in tables:
                # Get CREATE TABLE statement
                cursor.execute(f"SHOW CREATE TABLE `{table_name}`")
                create_stmt = cursor.fetchone()[1]
                
                # Get sample rows from table
                cursor.execute(f"SELECT * FROM `{table_name}` LIMIT 3")
                sample_rows = cursor.fetchall()
                
                # Get column names
                columns = [desc[0] for desc in cursor.description]
                schema_details[table_name] = {
                    "create_statement": create_stmt,
                    "columns": columns,
                    "sample_rows": sample_rows
                }
            
            cursor.close()
            return schema_details
    except mysql.connector.Error as e:
        raise Exception(f"Error executing query: {str(e)}")


#node-1
def parse_question(state: dict) -> dict:
    """Parse user question and identify relevant tables and columns."""
    question = state['question']
    schema = get_schema()

    prompt = ChatPromptTemplate.from_messages([
        ("system", '''You are a database analyst that analyzes SQL database schemas and user questions.
Your task is to identify which tables and columns in the database are needed to answer the user's question.

Review the database schema carefully and determine:
1. Is the question answerable using this database?
2. Which specific tables are needed?
3. Which specific columns from those tables are required?
4. Which columns contain meaningful text/names that match nouns in the question?

Respond with this exact JSON structure:
{{
    "is_relevant": boolean,  // true if the question can be answered with this database
    "relevant_tables": [
        {{
            "table_name": string,  // name of a relevant table
            "columns": [string],   // all columns needed from this table
            "noun_columns": [string]  // only columns containing text/names/nouns
        }}
    ]
}}

For "noun_columns", include only columns that contain actual text values like names, descriptions, or categories - not IDs or numeric values. For example, "product_name" would be a noun column, but "product_id" would not.
'''),
        ("human", "DATABASE SCHEMA:\n{schema}\n\nUSER QUESTION:\n{question}\n\nIdentify the relevant tables and columns:")
    ])

    output_parser = JsonOutputParser()
    
    response = llm.invoke(prompt.format_messages(schema=schema, question=question)).content
    parsed_response = output_parser.parse(re.sub(r'<think>.*?</think>', '',response,flags=re.DOTALL))
    return {"parsed_question": parsed_response}

llm=ChatGroq(model="qwen-qwq-32b")
print(parse_question({"question": 'how much rupees muppidathi needs to return back.'}))