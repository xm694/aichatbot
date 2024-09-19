import pandas as pd
from sqlalchemy import create_engine, text
from langchain import SQLDatabase
from dotenv import load_dotenv
import os

load_dotenv()
# connect to database
def create_db():
    # variables for database connection
    db_user = os.getenv("db_user")
    db_password = os.getenv("db_password")
    db_host = "localhost"
    db_port = "5432"  # default PostgreSQL port
    db_name = "Chinook"

    # Create the SQLAlchemy engine
    db_url = f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
    engine = create_engine(db_url)

    # Create the LangChain SQLDatabase object
    db = SQLDatabase(engine)

    return db


# # fetch data from database
# def fetch_data(query):
#     with engine.connect() as connection:
#         result = connection.execute(text(query))
#         df = pd.DataFrame(result.fetchall(), columns=result.keys())

#         return df
