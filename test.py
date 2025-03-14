from typing import List, Any, Annotated, Dict, Optional
from typing_extensions import TypedDict
import operator
import mysql.connector
import os
import json
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from langchain_groq import ChatGroq
from langgraph.graph import StateGraph, END

# Define TypedDicts
class InputState(TypedDict):
    question: str
    parsed_question: Dict[str, Any]
    unique_nouns: List[str]
    sql_query: str
    results: List[Any]
    visualization: Annotated[str, operator.add]

class OutputState(TypedDict):
    parsed_question: Dict[str, Any]
    unique_nouns: List[str]
    sql_query: str
    sql_valid: bool
    sql_issues: str
    results: List[Any]
    answer: Annotated[str, operator.add]
    error: str
    visualization: Annotated[str, operator.add]
    visualization_reason: Annotated[str, operator.add]
    formatted_data_for_visualization: Dict[str, Any]
############

import mysql.connector
from mysql.connector import Error
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


def execute_query( query: str) -> List[Any]:
    """Execute SQL query on the MySQL database and return results."""
    try:
        # Connect to MySQL
        connection = mysql.connector.connect(
            host="localhost",
            port=3306,
            user="root",
            password="",
            database="walmart"
        )
        cursor = connection.cursor()

        # Execute query
        cursor.execute(query)
        results = cursor.fetchall()

        cursor.close()
        connection.close()

        return results
    except mysql.connector.Error as e:
        raise Exception(f"Error executing query: {str(e)}")

# Data Formatter Functions
llm = ChatGroq(model="llama-3.3-70b-specdec",api_key="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")

def format_data_for_visualization(state: dict) -> dict:
    """Format the data for the chosen visualization type."""
    visualization = state['visualization']
    results = state['results']
    question = state['question']
    sql_query = state['sql_query']

    if visualization == "none":
        return {"formatted_data_for_visualization": None}
    
    if visualization == "scatter":
        try:
            return _format_scatter_data(results)
        except Exception as e:
            return _format_other_visualizations(visualization, question, sql_query, results)
    
    if visualization == "bar" or visualization == "horizontal_bar":
        try:
            return _format_bar_data(results, question)
        except Exception as e:
            return _format_other_visualizations(visualization, question, sql_query, results)
    
    if visualization == "line":
        try:
            return _format_line_data(results, question)
        except Exception as e:
            return _format_other_visualizations(visualization, question, sql_query, results)
    
    return _format_other_visualizations(visualization, question, sql_query, results)

def _format_line_data(results, question):
    if isinstance(results, str):
        results = eval(results)

    if len(results[0]) == 2:
        x_values = [str(row[0]) for row in results]
        y_values = [float(row[1]) for row in results]

        prompt = ChatPromptTemplate.from_messages([
            ("system", "You are a data labeling expert. Given a question and some data, provide a concise and relevant label for the data series."),
            ("human", "Question: {question}\n Data (first few rows): {data}\n\nProvide a concise label for this y axis. For example, if the data is the sales figures over time, the label could be 'Sales'. If the data is the population growth, the label could be 'Population'. If the data is the revenue trend, the label could be 'Revenue'."),
        ])
        label = llm.invoke(prompt.format_messages(question=question, data=str(results[:2]))).content

        formatted_data = {
            "xValues": x_values,
            "yValues": [
                {
                    "data": y_values,
                    "label": label.strip()
                }
            ]
        }
    elif len(results[0]) == 3:
        data_by_label = {}
        x_values = []
        labels = list(set(item2 for item1, item2, item3 in results 
                          if isinstance(item2, str) and not item2.replace(".", "").isdigit() and "/" not in item2))
        
        if not labels:
            labels = list(set(item1 for item1, item2, item3 in results 
                          if isinstance(item1, str) and not item1.replace(".", "").isdigit() and "/" not in item1))

        for item1, item2, item3 in results:
            if isinstance(item1, str) and not item1.replace(".", "").isdigit() and "/" not in item1:
                label, x, y = item1, item2, item3
            else:
                x, label, y = item1, item2, item3
                
            if str(x) not in x_values:
                x_values.append(str(x))
            if label not in data_by_label:
                data_by_label[label] = []
            data_by_label[label].append(float(y))
            for other_label in labels:
                if other_label != label:
                    if other_label not in data_by_label:
                        data_by_label[other_label] = []
                    data_by_label[other_label].append(None)

        y_values = [
            {
                "data": data,
                "label": label
            }
            for label, data in data_by_label.items()
        ]

        formatted_data = {
            "xValues": x_values,
            "yValues": y_values,
            "yAxisLabel": ""
        }

        prompt = ChatPromptTemplate.from_messages([
            ("system", "You are a data labeling expert. Given a question and some data, provide a concise and relevant label for the y-axis."),
            ("human", "Question: {question}\n Data (first few rows): {data}\n\nProvide a concise label for the y-axis. For example, if the data represents sales figures over time for different categories, the label could be 'Sales'. If it's about population growth for different groups, it could be 'Population'."),
        ])
        y_axis_label = llm.invoke(prompt.format_messages(question=question, data=str(results[:2]))).content

        formatted_data["yAxisLabel"] = y_axis_label.strip()

    return {"formatted_data_for_visualization": formatted_data}

def _format_scatter_data(results):
    if isinstance(results, str):
        results = eval(results)

    formatted_data = {"series": []}
    
    if len(results[0]) == 2:
        formatted_data["series"].append({
            "data": [
                {"x": float(x), "y": float(y), "id": i+1}
                for i, (x, y) in enumerate(results)
            ],
            "label": "Data Points"
        })
    elif len(results[0]) == 3:
        entities = {}
        for item1, item2, item3 in results:
            if isinstance(item1, str) and not item1.replace(".", "").isdigit() and "/" not in item1:
                label, x, y = item1, item2, item3
            else:
                x, label, y = item1, item2, item3
            if label not in entities:
                entities[label] = []
            entities[label].append({"x": float(x), "y": float(y), "id": len(entities[label])+1})
        
        for label, data in entities.items():
            formatted_data["series"].append({
                "data": data,
                "label": label
            })
    else:
        raise ValueError("Unexpected data format in results")                

    return {"formatted_data_for_visualization": formatted_data}

def _format_bar_data(results, question):
    if isinstance(results, str):
        results = eval(results)

    if len(results[0]) == 2:
        labels = [str(row[0]) for row in results]
        data = [float(row[1]) for row in results]
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", "You are a data labeling expert. Given a question and some data, provide a concise and relevant label for the data series."),
            ("human", "Question: {question}\nData (first few rows): {data}\n\nProvide a concise label for this y axis. For example, if the data is the sales figures for products, the label could be 'Sales'. If the data is the population of cities, the label could be 'Population'. If the data is the revenue by region, the label could be 'Revenue'."),
        ])
        label = llm.invoke(prompt.format_messages(question=question, data=str(results[:2]))).content
        
        values = [{"data": data, "label": label}]
    elif len(results[0]) == 3:
        categories = set(row[1] for row in results)
        labels = list(categories)
        entities = set(row[0] for row in results)
        values = []
        for entity in entities:
            entity_data = [float(row[2]) for row in results if row[0] == entity]
            values.append({"data": entity_data, "label": str(entity)})
    else:
        raise ValueError("Unexpected data format in results")

    formatted_data = {
        "labels": labels,
        "values": values
    }

    return {"formatted_data_for_visualization": formatted_data}

def _format_other_visualizations(visualization, question, sql_query, results):
    instructions = graph_instructions[visualization]
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are a Data expert who formats data according to the required needs. You are given the question asked by the user, it's sql query, the result of the query and the format you need to format it in."),
        ("human", 'For the given question: {question}\n\nSQL query: {sql_query}\n\Result: {results}\n\nUse the following example to structure the data: {instructions}. Just give the json string. Do not format it'),
    ])
    response = llm.invoke(prompt.format_messages(question=question, sql_query=sql_query, results=results, instructions=instructions)).content
    
    try:
        formatted_data_for_visualization = json.loads(response)
        return {"formatted_data_for_visualization": formatted_data_for_visualization}
    except json.JSONDecodeError:
        return {"error": "Failed to format data for visualization", "raw_response": response}

# SQL Agent Functions
def parse_question(state: dict) -> dict:
    """Parse user question and identify relevant tables and columns."""
    question = state['question']
    schema = get_schema()

    prompt = ChatPromptTemplate.from_messages([
        ("system", '''You are a data analyst that can help summarize SQL tables and parse user questions about a database. 
Given the question and database schema, identify the relevant tables and columns. 
If the question is not relevant to the database or if there is not enough information to answer the question, set is_relevant to false.

Your response should be in the following JSON format:
{{
    "is_relevant": boolean,
    "relevant_tables": [
        {{
            "table_name": string,
            "columns": [string],
            "noun_columns": [string]
        }}
    ]
}}

The "noun_columns" field should contain only the columns that are relevant to the question and contain nouns or names, for example, the column "Artist name" contains nouns relevant to the question "What are the top selling artists?", but the column "Artist ID" is not relevant because it does not contain a noun. Do not include columns that contain numbers.
'''),
        ("human", "===Database schema:\n{schema}\n\n===User question:\n{question}\n\nIdentify relevant tables and columns:")
    ])

    output_parser = JsonOutputParser()
    
    response = llm.invoke(prompt.format_messages(schema=schema, question=question)).content
    parsed_response = output_parser.parse(response)
    return {"parsed_question": parsed_response}

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

def generate_sql(state: dict) -> dict:
    """Generate SQL query based on parsed question and unique nouns."""
    question = state['question']
    parsed_question = state['parsed_question']
    unique_nouns = state['unique_nouns']

    if not parsed_question['is_relevant']:
        return {"sql_query": "NOT_RELEVANT", "is_relevant": False}
    
    schema = get_schema()

    prompt = ChatPromptTemplate.from_messages([
        ("system", '''
You are an AI assistant that generates SQL queries based on user questions, database schema, and unique nouns found in the relevant tables. Generate a valid SQL query to answer the user's question.

If there is not enough information to write a SQL query, respond with "NOT_ENOUGH_INFO".

Here are some examples:

1. What is the top selling product?
Answer: SELECT product_name, SUM(quantity) as total_quantity FROM sales WHERE product_name IS NOT NULL AND quantity IS NOT NULL AND product_name != "" AND quantity != "" AND product_name != "N/A" AND quantity != "N/A" GROUP BY product_name ORDER BY total_quantity DESC LIMIT 1

2. What is the total revenue for each product?
Answer: SELECT \product name\, SUM(quantity * price) as total_revenue FROM sales WHERE \product name\ IS NOT NULL AND quantity IS NOT NULL AND price IS NOT NULL AND \product name\ != "" AND quantity != "" AND price != "" AND \product name\ != "N/A" AND quantity != "N/A" AND price != "N/A" GROUP BY \product name\  ORDER BY total_revenue DESC

3. What is the market share of each product?
Answer: SELECT \product name\, SUM(quantity) * 100.0 / (SELECT SUM(quantity) FROM sa  les) as market_share FROM sales WHERE \product name\ IS NOT NULL AND quantity IS NOT NULL AND \product name\ != "" AND quantity != "" AND \product name\ != "N/A" AND quantity != "N/A" GROUP BY \product name\  ORDER BY market_share DESC

4. Plot the distribution of income over time
Answer: SELECT income, COUNT(*) as count FROM users WHERE income IS NOT NULL AND income != "" AND income != "N/A" GROUP BY income

THE RESULTS SHOULD ONLY BE IN THE FOLLOWING FORMAT, SO MAKE SURE TO ONLY GIVE TWO OR THREE COLUMNS:
[[x, y]]
or 
[[label, x, y]]
             
For questions like "plot a distribution of the fares for men and women", count the frequency of each fare and plot it. The x axis should be the fare and the y axis should be the count of people who paid that fare.
SKIP ALL ROWS WHERE ANY COLUMN IS NULL or "N/A" or "".
Just give the query string. Do not format it. Make sure to use the correct spellings of nouns as provided in the unique nouns list. All the table and column names should be enclosed in backticks.
'''),
        ("human", '''===Database schema:
{schema}

===User question:
{question}

===Relevant tables and columns:
{parsed_question}

===Unique nouns in relevant tables:
{unique_nouns}

Generate SQL query string'''),
    ])

    response = llm.invoke(prompt.format_messages(schema=schema, question=question, parsed_question=parsed_question, unique_nouns=unique_nouns)).content
    
    if response.strip() == "NOT_ENOUGH_INFO":
        return {"sql_query": "NOT_RELEVANT"}
    else:
        return {"sql_query": response}

def validate_and_fix_sql(state: dict) -> dict:
    """Validate and fix the generated SQL query."""
    sql_query = state['sql_query']

    if sql_query == "NOT_RELEVANT":
        return {"sql_query": "NOT_RELEVANT", "sql_valid": False}
    
    schema = get_schema()

    prompt = ChatPromptTemplate.from_messages([
        ("system", r'''
You are an AI assistant that validates and fixes SQL queries. Your task is to:
1. Check if the SQL query is valid.
2. Ensure all table and column names are correctly spelled and exist in the schema. All the table and column names should be enclosed in backticks.
3. If there are any issues, fix them and provide the corrected SQL query.
4. If no issues are found, return the original query.

Respond in JSON format with the following structure. Only respond with the JSON:
{{
    "valid": boolean,
    "issues": string or null,
    "corrected_query": string
}}
'''),
        ("human", r"""===Database schema:
{schema}

===Generated SQL query:
{sql_query}

Respond in JSON format with the following structure. Only respond with the JSON:
{{
    "valid": boolean,
    "issues": string or null,
    "corrected_query": string
}}

For example:
1. {{
    "valid": true,
    "issues": null,
    "corrected_query": "None"
}}
             
2. {{
    "valid": false,
    "issues": "Column USERS does not exist",
    "corrected_query": "SELECT * FROM \users\ WHERE age > 25"
}}

3. {{
    "valid": false,
    "issues": "Column names and table names should be enclosed in backticks if they contain spaces or special characters",
    "corrected_query": "SELECT * FROM \gross income\ WHERE \age\ > 25"
}}
             
""")
    ])

    output_parser = JsonOutputParser()
    response = llm.invoke(prompt.format_messages(schema=schema, sql_query=sql_query)).content
    result = output_parser.parse(response)

    if result["valid"] and result["issues"] is None:
        return {"sql_query": sql_query, "sql_valid": True}
    else:
        return {
            "sql_query": result["corrected_query"],
            "sql_valid": result["valid"],
            "sql_issues": result["issues"]
        }

def execute_sql(state: dict) -> dict:
    """Execute SQL query and return results."""
    query = state['sql_query']
    
    if query == "NOT_RELEVANT":
        return {"results": "NOT_RELEVANT"}

    try:
        results = execute_query(query)
        return {"results": results}
    except Exception as e:
        return {"error": str(e)}

def format_results(state: dict) -> dict:
    """Format query results into a human-readable response."""
    question = state['question']
    results = state['results']

    if results == "NOT_RELEVANT":
        return {"answer": "Sorry, I can only give answers relevant to the database."}

    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are an AI assistant that formats database query results into a human-readable response. Give a conclusion to the user's question based on the query results. Do not give the answer in markdown format. Only give the answer in one line."),
        ("human", "User question: {question}\n\nQuery results: {results}\n\nFormatted response:"),
    ])

    response = llm.invoke(prompt.format_messages(question=question, results=results)).content
    return {"answer": response}

def choose_visualization(state: dict) -> dict:
    """Choose an appropriate visualization for the data."""
    question = state['question']
    results = state['results']
    sql_query = state['sql_query']

    if results == "NOT_RELEVANT":
        return {"visualization": "none", "visualization_reasoning": "No visualization needed for irrelevant questions."}

    prompt = ChatPromptTemplate.from_messages([
        ("system", '''
You are an AI assistant that recommends appropriate data visualizations. Based on the user's question, SQL query, and query results, suggest the most suitable type of graph or chart to visualize the data. If no visualization is appropriate, indicate that.

Available chart types and their use cases:
- Bar Graphs: Best for comparing categorical data or showing changes over time when categories are discrete and the number of categories is more than 2. Use for questions like "What are the sales figures for each product?" or "How does the population of cities compare? or "What percentage of each city is male?"
- Horizontal Bar Graphs: Best for comparing categorical data or showing changes over time when the number of categories is small or the disparity between categories is large. Use for questions like "Show the revenue of A and B?" or "How does the population of 2 cities compare?" or "How many men and women got promoted?" or "What percentage of men and what percentage of women got promoted?" when the disparity between categories is large.
- Scatter Plots: Useful for identifying relationships or correlations between two numerical variables or plotting distributions of data. Best used when both x axis and y axis are continuous. Use for questions like "Plot a distribution of the fares (where the x axis is the fare and the y axis is the count of people who paid that fare)" or "Is there a relationship between advertising spend and sales?" or "How do height and weight correlate in the dataset? Do not use it for questions that do not have a continuous x axis."
- Pie Charts: Ideal for showing proportions or percentages within a whole. Use for questions like "What is the market share distribution among different companies?" or "What percentage of the total revenue comes from each product?"
- Line Graphs: Best for showing trends and distributionsover time. Best used when both x axis and y axis are continuous. Used for questions like "How have website visits changed over the year?" or "What is the trend in temperature over the past decade?". Do not use it for questions that do not have a continuous x axis or a time based x axis.

Consider these types of questions when recommending a visualization:
1. Aggregations and Summarizations (e.g., "What is the average revenue by month?" - Line Graph)
2. Comparisons (e.g., "Compare the sales figures of Product A and Product B over the last year." - Line or Column Graph)
3. Plotting Distributions (e.g., "Plot a distribution of the age of users" - Scatter Plot)
4. Trends Over Time (e.g., "What is the trend in the number of active users over the past year?" - Line Graph)
5. Proportions (e.g., "What is the market share of the products?" - Pie Chart)
6. Correlations (e.g., "Is there a correlation between marketing spend and revenue?" - Scatter Plot)

Provide your response in the following format:
Recommended Visualization: [Chart type or "None"]. ONLY use the following names: bar, horizontal_bar, line, pie, scatter, none
Reason: [Brief explanation for your recommendation]
'''),
        ("human", '''
User question: {question}
SQL query: {sql_query}
Query results: {results}

Recommend a visualization:'''),
    ])

    response = llm.invoke(prompt.format_messages(question=question, sql_query=sql_query, results=results)).content
    
    lines = response.split('\n')
    visualization = lines[0].split(': ')[1]
    reason = lines[1].split(': ')[1]

    return {"visualization": visualization, "visualization_reason": reason}

# Workflow Manager Functions
def create_workflow() -> StateGraph:
    """Create and configure the workflow graph."""
    workflow = StateGraph(input=InputState, output=OutputState)

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
    workflow.add_edge("parse_question", "get_unique_nouns")
    workflow.add_edge("get_unique_nouns", "generate_sql")
    workflow.add_edge("generate_sql", "validate_and_fix_sql")
    workflow.add_edge("validate_and_fix_sql", "execute_sql")
    workflow.add_edge("execute_sql", "format_results")
    workflow.add_edge("execute_sql", "choose_visualization")
    workflow.add_edge("choose_visualization", "format_data_for_visualization")
    workflow.add_edge("format_data_for_visualization", END)
    workflow.add_edge("format_results", END)
    workflow.set_entry_point("parse_question")

    return workflow

def returnGraph():
    return create_workflow().compile()

def run_sql_agent(question: str) -> dict:
    """Run the SQL agent workflow and return the formatted answer and visualization recommendation."""
    app = create_workflow().compile()
    result = app.invoke({"question": question})
    return {
        "answer": result['answer'],
        "visualization": result['visualization'],
        "visualization_reason": result['visualization_reason'],
        "formatted_data_for_visualization": result['formatted_data_for_visualization']
    }

# Graph Instructions
barGraphIntstruction = '''
  Where data is: {
    labels: string[]
    values: {\data: number[], label: string}[]
  }

// Examples of usage:
Each label represents a column on the x axis.
Each array in values represents a different entity. 

Here we are looking at average income for each month.
1. data = {
  labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
  values: [{data:[21.5, 25.0, 47.5, 64.8, 105.5, 133.2], label: 'Income'}],
}

Here we are looking at the performance of american and european players for each series. Since there are two entities, we have two arrays in values.
2. data = {
  labels: ['series A', 'series B', 'series C'],
  values: [{data:[10, 15, 20], label: 'American'}, {data:[20, 25, 30], label: 'European'}],
}
'''

horizontalBarGraphIntstruction = '''
  Where data is: {
    labels: string[]
    values: {\data: number[], label: string}[]
  }

// Examples of usage:
Each label represents a column on the x axis.
Each array in values represents a different entity. 

Here we are looking at average income for each month.
1. data = {
  labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
  values: [{data:[21.5, 25.0, 47.5, 64.8, 105.5, 133.2], label: 'Income'}],
}

Here we are looking at the performance of american and european players for each series. Since there are two entities, we have two arrays in values.
2. data = {
  labels: ['series A', 'series B', 'series C'],
  values: [{data:[10, 15, 20], label: 'American'}, {data:[20, 25, 30], label: 'European'}],
}

'''

lineGraphIntstruction = '''
  Where data is: {
  xValues: number[] | string[]
  yValues: { data: number[]; label: string }[]
}

// Examples of usage:

Here we are looking at the momentum of a body as a function of mass.
1. data = {
  xValues: ['2020', '2021', '2022', '2023', '2024'],
  yValues: [
    { data: [2, 5.5, 2, 8.5, 1.5]},
  ],
}

Here we are looking at the performance of american and european players for each year. Since there are two entities, we have two arrays in yValues.
2. data = {
  xValues: ['2020', '2021', '2022', '2023', '2024'],
  yValues: [
    { data: [2, 5.5, 2, 8.5, 1.5], label: 'American' },
    { data: [2, 5.5, 2, 8.5, 1.5], label: 'European' },
  ],
}
'''

pieChartIntstruction = '''
  Where data is: {
    labels: string
    values: number
  }[]

// Example usage:
 data = [
        { id: 0, value: 10, label: 'series A' },
        { id: 1, value: 15, label: 'series B' },
        { id: 2, value: 20, label: 'series C' },
      ],
'''

scatterPlotIntstruction = '''
Where data is: {
  series: {
    data: { x: number; y: number; id: number }[]
    label: string
  }[]
}

// Examples of usage:
1. Here each data array represents the points for a different entity. 
We are looking for correlation between amount spent and quantity bought for men and women.
data = {
  series: [
    {
      data: [
        { x: 100, y: 200, id: 1 },
        { x: 120, y: 100, id: 2 },
        { x: 170, y: 300, id: 3 },
      ],
      label: 'Men',
    },
    {
      data: [
        { x: 300, y: 300, id: 1 },
        { x: 400, y: 500, id: 2 },
        { x: 200, y: 700, id: 3 },
      ],
      label: 'Women',
    }
  ],
}

2. Here we are looking for correlation between the height and weight of players.
data = {
  series: [
    {
      data: [
        { x: 180, y: 80, id: 1 },
        { x: 170, y: 70, id: 2 },
        { x: 160, y: 60, id: 3 },
      ],
      label: 'Players',
    },
  ],
}

// Note: Each object in the 'data' array represents a point on the scatter plot.
// The 'x' and 'y' values determine the position of the point, and 'id' is a unique identifier.
// Multiple series can be represented, each as an object in the outer array.
'''

graph_instructions = {
    "bar": barGraphIntstruction,
    "horizontal_bar": horizontalBarGraphIntstruction,
    "line": lineGraphIntstruction,
    "pie": pieChartIntstruction,
    "scatter": scatterPlotIntstruction
}

# Example usage
# graph = returnGraph()
# result = run_sql_agent("city wise sales")
# print(result)
print(get_schema())
