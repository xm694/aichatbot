from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain_core.prompts import PromptTemplate, ChatPromptTemplate, FewShotChatMessagePromptTemplate
from langchain_core.example_selectors import SemanticSimilarityExampleSelector
from langchain.chains import create_sql_query_chain
from langchain_community.tools.sql_database.tool import QuerySQLDataBaseTool

#langchain csv experiment
from langchain_experimental.agents import create_pandas_dataframe_agent

from operator import itemgetter
from keys_manager import get_api_configuration
import os
import dotenv
import re


from conn import create_db

# configure credentials for openai and langchain
# dotenv.load_dotenv()
# openai_api_key = os.getenv("OPENAI_API_KEY")

config = get_api_configuration()

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0, api_key=config["openai_api_key"])

LANGCHAIN_TRACING_V2="true"
LANGCHAIN_ENDPOINT="https://api.smith.langchain.com"
# LANGCHAIN_API_KEY = os.getenv("LANGCHAIN_API_KEY")
LANGCHAIN_API_KEY = config["langchain_api_key"]
LANGCHAIN_PROJECT="database-chatbot"

db = create_db()
#get table context info for prompt
get_table_info = db.get_context()["table_info"]
#prompts engineering
sql_template = """You are a PostgreSQL expert. Given an input question, first create a syntactically correct PostgreSQL query to run, ONLY the SQL query without prefix "SQLQuery: ".
, then look at the results of the query and return the answer to the input question.
    Unless the user specifies in the question a specific number of examples to obtain, query for at most {top_k} results using the LIMIT clause as per PostgreSQL. You can order the results to return the most informative data in the database.
    Never query for all columns from a table. You must query only the columns that are needed to answer the question. Wrap each column name in double quotes (") to denote them as delimited identifiers.
    Pay attention to use only the column names you can see in the tables below. Be careful to not query for columns that do not exist. Also, pay attention to which column is in which table.
    Pay attention to use CURRENT_DATE function to get the current date, if the question involves "today".

    Use the following format:

    Question: Question here
    SQLQuery: SQL Query to run, NO MARKDOWN, NO EXPLANATION
    SQLResult: Result of the SQLQuery
    Answer: Final answer here

    Referent to the relavant database information:
    {table_info}

    Question: {input}

    """

SQL_PROMPT = PromptTemplate(
    template = sql_template,
    input_variables = ["input"],
    partial_variables = {"table_info":get_table_info, "top_k":3},
    )

# prompt for generate final answer based on sql query result
answer_prompt = PromptTemplate.from_template(
    """Given the following user question, corresponding SQL query, and SQL result, answer the user question.

    Question: {question}
    SQL Query: {query}
    SQL Result: {result}
    Answer: """
    )

#sql extract helper function
def extract_sql_query(output):
    # Use regex to find the SQL query
    match = re.search(r'SQLQuery:\s*(.*?)(?:\nSQLResult:|$)', output, re.DOTALL)
    if match:
        # Extract the query and remove any leading/trailing whitespace
        sql_query = match.group(1).strip()
        return sql_query
    else:
        raise ValueError("No SQL query found in the output")

# Steps for SQL Q&A
# # step 1: read database schema image from user upload
# def read_image(image_url):
#     #code to use multimodal input - image to text
#     image_data = base64.b64encode(httpx.get(image_url).content).decode("utf-8")
#     return image_data

# step 2: generate sql query based on user input and database schema
def generate_sql_query():
    if db is None:
        raise ValueError("Failed to connect to database.")
    db_chain = create_sql_query_chain(llm, db, SQL_PROMPT)
    return db_chain

#step 3: answer question in natural language
def answer_question():
    if db is None:
        raise ValueError("Failed to connect to database.")
    write_query = generate_sql_query()
    execute_query = QuerySQLDataBaseTool(db=db)
    ans_chain = (
        RunnablePassthrough.assign(query= write_query).assign(
            result=itemgetter("query") | execute_query
        )
        | answer_prompt
        | llm
        | StrOutputParser()
    )
    return ans_chain

"""CSV helper"""
def csv_agent(df):
    csv_agent = create_pandas_dataframe_agent(
        llm,
        df=df,
        agent_type = "openai-tools", verbose=True, allow_dangerous_code = True
    )
    return csv_agent


# todos:
# report: generate daily report if user click on generate report button
"""User can choose to generate a daily report, if "generate report button" be clicked,
app need to retrieved relevant data from the database and plot data into charts,
user will get a pre-formatted report including charts and summary"""
# def generate_report(data, openai_api_key, llm_model):
#     client = OpenAI(api_key=openai_api_key)
#     prompt = f"""
#     Base on related retrieved data from the database: {data}
#     Generate a summary report in markdown format.
#     """
#     response = client.chat.completions.create(model=llm_model, #user choose llm model
#                                         prompt=prompt)

#     report = response.choices[0].text.strip()
#     return report


