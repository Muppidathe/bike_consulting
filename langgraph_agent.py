#langgraph_agent.py
from typing import List, Any, Annotated, Dict
from typing_extensions import TypedDict
import operator
import json
from langchain_core.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq
from langgraph.graph import StateGraph, END,START
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

#node-2 dependency
def execute_query( query: str) -> List[Any]:
    """Execute SQL query on the MySQL database and return results."""
    try:
        # Connect to MySQL
        db=connect()
        cursor = db.cursor()

        # Execute query
        cursor.execute(query)
        results = cursor.fetchall()

        cursor.close()
        db.close()

        return results
    except mysql.connector.Error as e:
        raise Exception(f"Error executing query: {str(e)}")
#node-8 dependency
barGraphIntstruction = '''
Where data is: {
  labels: string[]
  values: {data: number[], label: string}[]
}

DETAILED INSTRUCTIONS FOR YOUR DATABASE:
- For vehicle sales data: Use labels for different model names and values for cost or sales prices
- For bills data: Use labels for person names and values for transaction amounts
- For expenses data: Use labels for different expense descriptions and values for amounts spent

EXAMPLES SPECIFIC TO YOUR DATABASE:

Example 1 - Vehicle Sales by Model:
data = {
  labels: ['R15', 'TVS', 'Pulsar', 'Activa', 'FZ'],
  values: [{data:[146000, 40000, 120000, 85000, 110000], label: 'Cost Price'}],
}

Example 2 - Money Given vs Received by Person:
data = {
  labels: ['MUPPIDATHI', 'BALA', 'KANNAN'],
  values: [
    {data:[15000, 12000, 8000], label: 'Money Given'}, 
    {data:[5000, 3000, 2000], label: 'Money Received'}
  ],
}

Example 3 - Office Expenses by Category:
data = {
  labels: ['PATHI', 'PEN', 'STATIONARY', 'CLEANING'],
  values: [{data:[56, 30, 120, 45], label: 'Amount'}],
}

Ensure the number of elements in 'labels' matches the number of elements in each 'data' array.
'''

horizontalBarGraphIntstruction = '''
Where data is: {
  labels: string[]
  values: {data: number[], label: string}[]
}

DETAILED INSTRUCTIONS FOR YOUR DATABASE:
- Best for comparing a small number of categories (like comparing just 2-3 people's transactions)
- Use when you have long category names like expense descriptions
- Perfect for vehicle comparison where only a few vehicles are being analyzed

EXAMPLES SPECIFIC TO YOUR DATABASE:

Example 1 - Money Given vs Received for a Single Person:
data = {
  labels: ['Money Given', 'Money Received'],
  values: [{data:[15000, 5000], label: 'MUPPIDATHI'}],
}

Example 2 - Profit Comparison Between Vehicles:
data = {
  labels: ['KL31N7871', 'TN31N7871'],
  values: [{data:[4000, 2000], label: 'Profit Margin'}],
}

Example 3 - Transaction Amounts by Person:
data = {
  labels: ['MUPPIDATHI', 'BALA'],
  values: [{data:[10000, 12000], label: 'Outstanding Amount'}],
}

Make sure labels are clear and descriptive, especially for vehicle numbers or expense categories.
'''

lineGraphIntstruction = '''
Where data is: {
  xValues: number[] | string[]
  yValues: {data: number[], label: string}[]
}

DETAILED INSTRUCTIONS FOR YOUR DATABASE:
- Perfect for showing trends over dates in your tables
- Use for tracking expenses, bills, or vehicle sales over time
- Can show multiple trends simultaneously (e.g., money given vs received over time)

EXAMPLES SPECIFIC TO YOUR DATABASE:

Example 1 - Expenses Over Time:
data = {
  xValues: ['2025-03-01', '2025-03-02', '2025-03-03', '2025-03-04'],
  yValues: [
    {data: [25, 40, 15, 86], label: 'Office Expenses'},
    {data: [100, 250, 300, 500], label: 'Vehicle Expenses'}
  ],
}

Example 2 - Transaction History for a Person:
data = {
  xValues: ['Jan', 'Feb', 'Mar', 'Apr'],
  yValues: [
    {data: [5000, 7000, 15000, 8000], label: 'Money Given to MUPPIDATHI'},
    {data: [1000, 2000, 5000, 3000], label: 'Money Received from MUPPIDATHI'}
  ],
}

Example 3 - Vehicle Value Trends:
data = {
  xValues: ['Purchase', 'After Repair', 'At Sale'],
  yValues: [
    {data: [146000, 147500, 150000], label: 'R15 Value'}
  ],
}

Ensure xValues represent time periods or sequential stages, and the data points in yValues correspond exactly to these x-axis points.
'''

pieChartIntstruction = '''
Where data is: [
  {id: number, value: number, label: string}
]

DETAILED INSTRUCTIONS FOR YOUR DATABASE:
- Ideal for showing proportions within your data
- Use for expense breakdowns, money distribution among people, or vehicle cost distributions
- Best when you have 2-7 categories to compare

EXAMPLES SPECIFIC TO YOUR DATABASE:

Example 1 - Distribution of Outstanding Money:
data = [
  {id: 0, value: 10000, label: 'MUPPIDATHI'},
  {id: 1, value: 12000, label: 'BALA'},
  {id: 2, value: 5000, label: 'KANNAN'}
]

Example 2 - Office Expense Breakdown:
data = [
  {id: 0, value: 56, label: 'PATHI'},
  {id: 1, value: 30, label: 'PEN'},
  {id: 2, value: 150, label: 'FURNITURE'}
]

Example 3 - Vehicle Cost Distribution:
data = [
  {id: 0, value: 146000, label: 'Base Cost'},
  {id: 1, value: 1000, label: 'Fine'},
  {id: 2, value: 500, label: 'Repairs'}
]

Always assign unique ID values, make sure values are numbers, and ensure labels are descriptive.
'''

scatterPlotIntstruction = '''
Where data is: {
  series: [{
    data: [{x: number, y: number, id: number}],
    label: string
  }]
}

DETAILED INSTRUCTIONS FOR YOUR DATABASE:
- Use for showing relationships between two numeric variables
- Good for analyzing vehicle value vs age, cost price vs sales price, or transaction amounts vs dates
- Can show multiple data series to compare different categories

EXAMPLES SPECIFIC TO YOUR DATABASE:

Example 1 - Vehicle Cost vs Year:
data = {
  series: [{
    data: [
      {x: 2016, y: 40000, id: 1},
      {x: 2018, y: 75000, id: 2},
      {x: 2020, y: 100000, id: 3},
      {x: 2022, y: 146000, id: 4}
    ],
    label: 'Vehicles'
  }]
}

Example 2 - Transaction Amount vs Date:
data = {
  series: [{
    data: [
      {x: 1, y: 15000, id: 1},  // March 1, 2025
      {x: 2, y: 8000, id: 2},   // March 2, 2025
      {x: 3, y: 12000, id: 3},  // March 3, 2025
      {x: 4, y: 5000, id: 4}    // March 4, 2025
    ],
    label: 'Money Given'
  }, {
    data: [
      {x: 1, y: 2000, id: 5},   // March 1, 2025
      {x: 2, y: 3000, id: 6},   // March 2, 2025
      {x: 3, y: 1000, id: 7},   // March 3, 2025
      {x: 4, y: 5000, id: 8}    // March 4, 2025
    ],
    label: 'Money Received'
  }]
}

Example 3 - Cost Price vs Sales Price:
data = {
  series: [{
    data: [
      {x: 40000, y: 45000, id: 1},  // TVS
      {x: 146000, y: 150000, id: 2} // R15
    ],
    label: 'Vehicles'
  }]
}

Make sure each data point has a unique ID, and x and y values represent numeric measurements that could have a meaningful relationship.
'''
graph_instructions = {
    "bar": barGraphIntstruction,
    "horizontal_bar": horizontalBarGraphIntstruction,
    "line": lineGraphIntstruction,
    "pie": pieChartIntstruction,
    "scatter": scatterPlotIntstruction
}
def _format_other_visualizations(visualization, question, sql_query, results):
    instructions = graph_instructions[visualization]
    prompt = ChatPromptTemplate.from_messages([
        ("system", '''You are a financial data visualization expert specialized in vehicle sales and bill tracking systems.

Your job is to convert SQL query results into precisely formatted JSON for creating charts. You must follow the exact structure provided in the template.

SPECIFIC GUIDELINES FOR THIS DATABASE:
1. For bills/transactions data:
   - Consider whether to group by person name or date
   - Distinguish between money given (positive) and received (negative)
   - Calculate net balances when appropriate

2. For vehicle data:
   - Compare cost price vs. sales price for profitability analysis
   - Highlight vehicles with pending payments (received_amount < sales_price)
   - Group by model_name when comparing vehicle types

3. For expense data:
   - Categories expenses logically by description
   - Group small amounts into "Other" if there are many small categories
   - Sort expense categories by amount for better visualization

Use the exact field names and data structures shown in the template. Triple-check that your JSON is valid and matches the expected format. Your response should be ONLY the correctly formatted JSON with no additional text.
'''),
        ("human", '''USER QUESTION: 
{question}

SQL QUERY:
{sql_query}

QUERY RESULTS (tuples):
{results}

FORMAT TEMPLATE:
{instructions}

Convert the results to the exact format shown in the template:'''),
    ])
    response = llm.invoke(prompt.format_messages(question=question, sql_query=sql_query, results=results, instructions=instructions)).content
    
    try:
        # Try to extract just the JSON part if there's any explanation text
        json_str= re.sub(r'<think>.*?</think>','', response)
        formatted_data_for_visualization = json.loads(json_str)
        return {"formatted_data_for_visualization": formatted_data_for_visualization}
    except json.JSONDecodeError:
        # Second attempt - try to find anything that looks like JSON
        try:
            json_pattern = r'({[\s\S]*}|\[[\s\S]*\])'
            match = re.search(json_pattern, response)
            if match:
                json_str = match.group(0)
                formatted_data_for_visualization = json.loads(json_str)
                return {"formatted_data_for_visualization": formatted_data_for_visualization}
        except:
            pass
            
        return {"error": "Failed to format data for visualization", "raw_response": response}###############end of dependecy###############################################
# Define TypedDicts
class State(TypedDict):
    question: str
    parsed_question: Dict[str, Any]
    unique_nouns: List[str]
    sql_query: str
    results: List[Any]
    visualization: str
    sql_valid: bool
    sql_issues: str
    answer: Annotated[str, operator.add]
    error: str
    visualization_reason: str
    formatted_data_for_visualization: Dict[str, Any]
    is_relevant:bool
# class parse_question_stuct_inner(BaseModel):
#     table_name: str=Field(description="name of the table")
#     columns: list[str]=Field(description="list of all columns which is important respective to the question")
#     noun_columns: list[str]=Field(description="it contain only the columns that are relevant to the question and contain nouns or names")
# class parse_question_stuct(BaseModel):
#     is_relevant:bool=Field(description="it is set to False if question is not related to the database or if the question has no enough information")
#     relevant_tables:list[parse_question_stuct_inner]=Field(description="if is_relevant is set to be true then fill this with table information relavant to the question")
# class validate_sql_struct(BaseModel):
#     valid: bool=Field(description="set it to be True if generted sql query is valid otherwise set it to be False")
#     issues:Optional[str]=Field(description="if there is error/issues in generated sql query then highlight the issues and error")
#     corrected_query: str=Field(description="it there is issues in the generated sql query then provide the correct sql query")
############

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


#node-2
def get_unique_nouns(state: dict) -> dict:
    """Find unique nouns in relevant tables and columns."""
    parsed_question = state['parsed_question']
    
    if not parsed_question['is_relevant']:
        return {"unique_nouns": []}

    unique_nouns = set()
    for table_info in parsed_question['relevant_tables']:
        table_name = table_info['table_name']
        noun_columns = table_info['noun_columns']
        
        if noun_columns:
            column_names = ', '.join(f"{col}" for col in noun_columns)
            query = f"SELECT DISTINCT {column_names} FROM {table_name}"
            results = execute_query(query)
            for row in results:
                unique_nouns.update(str(value) for value in row if value)

    return {"unique_nouns": list(unique_nouns)}
#node-3
def generate_sql(state: dict) -> dict:
    """Generate SQL query based on parsed question and unique nouns."""
    question = state['question']
    parsed_question = state['parsed_question']
    unique_nouns = state['unique_nouns']

    if not parsed_question['is_relevant']:
        return {"sql_query": "NOT_RELEVANT", "is_relevant": False}
    
    schema = get_schema()

    prompt = ChatPromptTemplate.from_messages([
        ("system", '''You are an expert MySQL developer who writes precise SQL queries to answer user questions.

Given a database schema, a question, and unique text values from the database, write a SQL query that will correctly answer the user's question.

IMPORTANT GUIDELINES:
1. Always use backticks (`) around table and column names
2. Filter out NULL values, empty strings, and "N/A" values
3. Ensure your query is properly formatted and includes appropriate joins
4. For visualization purposes, keep your result set simple - 2-3 columns max
5. For aggregation queries, use GROUP BY and appropriate aggregation functions
6. For questions about distribution or trends, ensure your query provides data suitable for visualization
7.never use \\n(new line caracter) between the query

If you cannot write a query with the available information, respond with "NOT_ENOUGH_INFO".

COMMON QUERY PATTERNS:
- For "top/best/highest" questions: 
  SELECT `column_name`, COUNT(*) FROM `table` WHERE `column_name` IS NOT NULL GROUP BY `column_name` ORDER BY COUNT(*) DESC LIMIT 1

- For comparing categories: 
  SELECT `category_column`, SUM(`value_column`) FROM `table` WHERE `category_column` IS NOT NULL GROUP BY `category_column` ORDER BY SUM(`value_column`) DESC

- For time-based trends: 
  SELECT `date_column`, SUM(`value_column`) FROM `table` WHERE `date_column` IS NOT NULL GROUP BY `date_column` ORDER BY `date_column`

- For relationship analysis: 
  SELECT `column1`, `column2`, COUNT(*) FROM `table` WHERE `column1` IS NOT NULL AND `column2` IS NOT NULL GROUP BY `column1`, `column2`

Consider the unique nouns provided, and make sure your query uses correct spellings and names exactly as they appear in the database.
'''),
        ("human", '''DATABASE SCHEMA:
{schema}

USER QUESTION:
{question}

RELEVANT TABLES AND COLUMNS:
{parsed_question}

UNIQUE NOUNS IN DATABASE:
{unique_nouns}

Write Only a SQL_query that answers this question.Don't output any explanation or thought's:'''),
    ])

    response = llm.invoke(prompt.format_messages(schema=schema, question=question, parsed_question=parsed_question, unique_nouns=unique_nouns)).content
    
    if response.strip() == "NOT_ENOUGH_INFO":
        return {"sql_query": "NOT_RELEVANT"}
    else:
        return {"sql_query": re.sub(r'\n','',re.sub(r'<think>.*?</think>', '',response,flags=re.DOTALL))}

#node-4
def validate_and_fix_sql(state: dict) -> dict:
    """Validate and fix the generated SQL query."""
    sql_query = state['sql_query']

    if sql_query == "NOT_RELEVANT":
        return {"sql_query": "NOT_RELEVANT", "sql_valid": False}
    
    schema = get_schema()

    prompt = ChatPromptTemplate.from_messages([
        ("system", '''You are a SQL expert who validates and fixes SQL queries.

Examine the provided SQL query and database schema to:
1. Verify that all table and column names exist in the schema
2. Check that table and column names are properly enclosed in backticks (`)
3. Ensure proper join conditions if multiple tables are used
4. Verify that all SQL syntax is correct
5. Check that aggregation functions are used correctly with GROUP BY clauses
6.check for unwanted text in the query such as newline charcter,sql,etc...
7.check whether the paranthesis() are correctly opened and closed
If you find any issues, fix them and provide the corrected query.

Respond with ONLY this JSON format no other explanation:
{{
    "valid": boolean,  // true if query is valid, false if issues found
    "issues": string or null,  // description of issues found, or null if none
    "corrected_query": string  // fixed query or "None" if no fixes needed
}}
'''),
        ("human", '''DATABASE SCHEMA:
{schema}

SQL QUERY TO VALIDATE:
{sql_query}

Validate this query and provide fixes if needed:''')
    ])

    output_parser = JsonOutputParser()
    response = llm.invoke(prompt.format_messages(schema=schema, sql_query=sql_query)).content
    response=re.sub(r'<think>.*?</think>', '',response,flags=re.DOTALL)
    result = output_parser.parse(response)

    if result["valid"] and result["issues"] is None:
        return {"sql_query": sql_query, "sql_valid": True}
    else:
        return {
            "sql_query": result["corrected_query"],
            "sql_valid": result["valid"],
            "sql_issues": result["issues"]
        }

# node-5
def execute_sql(state: dict) -> dict:
    """Execute SQL query and return results."""
    query = state['sql_query']
    
    if query == "NOT_RELEVANT":
        return {"results": "NOT_RELEVANT"}

    try:
        results = execute_query(query)
        return {"results": results}
    except Exception as e:
        return {"results": "NOT_RELEVANT","error": str(e)}
#node-6
def format_results(state: dict) -> dict:
    """Format query results into a human-readable response."""
    question = state['question']
    results = state['results']

    if results == "NOT_RELEVANT":
        return {"answer": "I can only answer questions related to the database. Your question doesn't seem to be about the data I have access to."}

    prompt = ChatPromptTemplate.from_messages([
        ("system", '''You are a data analyst who explains SQL query results clearly and concisely.

Given a user's question and the query results, create a brief, informative response that:
1. Directly answers the user's question
2. Provides key insights from the data
3. Mentions specific numbers or trends if relevant
4. Presents the information in a natural, conversational way

Keep your response concise - ideally one or two sentences. Don't use formatting like bullet points or markdown.
'''),
        ("human", '''USER QUESTION: 
{question}

QUERY RESULTS:
{results}

Create a clear, concise answer based on these results:'''),
    ])

    response = llm.invoke(prompt.format_messages(question=question, results=results)).content
    return {"answer": re.sub(r'<think>.*?</think>', '',response,flags=re.DOTALL)}

# node-7
def choose_visualization(state: dict) -> dict:
    """Choose an appropriate visualization for the data."""
    question = state['question']
    results = state['results']
    sql_query = state['sql_query']

    if results == "NOT_RELEVANT":
        return {"visualization": "none", "visualization_reasoning": "No visualization needed for irrelevant questions."}

    prompt = ChatPromptTemplate.from_messages([
        ("system", '''You are a data visualization expert who recommends the best chart type for presenting data.

Based on the user's question, SQL query, and results, determine the most appropriate visualization type.

AVAILABLE VISUALIZATION TYPES:
- bar: For comparing categories (vertical bars)
- horizontal_bar: For comparing categories with fewer items or large value differences
- line: For showing trends over time or continuous data
- pie: For showing proportions of a whole (limited to 2-7 categories)
- scatter: For showing relationships between two variables
- none: When no visualization is appropriate

SELECTION GUIDELINES:
- Bar charts: Best for comparing discrete categories
- Line charts: Best for time series or continuous data
- Pie charts: Best for showing percentage breakdowns (use sparingly)
- Scatter plots: Best for showing correlation between two variables
- Horizontal bars: Best for comparing categories with long names or few items

Select exactly ONE visualization type from the list above.
'''),
        ("human", '''USER QUESTION: 
{question}

SQL QUERY:
{sql_query}

QUERY RESULTS:
         
{results}

What visualization would best represent this data? Answer in this format:
Recommended Visualization: [type]
Reason: [brief explanation]'''),
    ])

    response = llm.invoke(prompt.format_messages(question=question, sql_query=sql_query, results=results)).content
    response=re.sub(r'<think>.*?</think>','',response,flags=re.DOTALL)
    match = re.search(r"Recommended Visualization:\s*(\w+)\nReason:\s*(.*)", response, flags=re.DOTALL)
    visualization='none'
    reason=' '
    if match:
        visualization = match.group(1)  # Extracts "none"
        reason = match.group(2)  # Extracts the full Reason text

    return {"visualization": visualization, "visualization_reason": [reason]}

#node-8
def format_data_for_visualization(state: dict) -> dict:
    """Format the data for the chosen visualization type."""
    visualization = state['visualization']
    results = state['results']
    question = state['question']
    sql_query = state['sql_query']

    if visualization == "none":
        return {"formatted_data_for_visualization": None}
    return _format_other_visualizations(visualization, question, sql_query, results)
def create_workflow():
    """Create and configure the workflow graph."""
    global llm
    llm=ChatGroq(model="qwen-qwq-32b")
    workflow = StateGraph(State)
    # Add nodes to the graph
    workflow.add_node("parse_question", parse_question)
    workflow.add_node("get_unique_nouns", get_unique_nouns)
    workflow.add_node("generate_sql", generate_sql)
    workflow.add_node("validate_and_fix_sql", validate_and_fix_sql)
    workflow.add_node("execute_sql", execute_sql)
    workflow.add_node("format_results", format_results)
    workflow.add_node("choose_visualization", choose_visualization)
    workflow.add_node("format_data_for_visualization", format_data_for_visualization)

    # Define edges
    workflow.add_edge(START,"parse_question")
    workflow.add_edge("parse_question", "get_unique_nouns")
    workflow.add_edge("get_unique_nouns", "generate_sql")
    workflow.add_edge("generate_sql", "validate_and_fix_sql")
    workflow.add_edge("validate_and_fix_sql", "execute_sql")
    workflow.add_edge("execute_sql", "format_results")
    workflow.add_edge("execute_sql", "choose_visualization")
    workflow.add_edge("choose_visualization", "format_data_for_visualization")
    workflow.add_edge("format_data_for_visualization", END)
    workflow.add_edge("format_results", END)
    return workflow.compile()

# w = create_workflow()
# result = w.invoke({"question": 'how much rupees muppidathi needs to return back.'})
# print(result)