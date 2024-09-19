import streamlit as st
import pandas as pd
from langchain_helper import generate_sql_query, answer_question


def main():
    st.title("Chat with your Data")
    st.write("This app allows you to ask questions about your data and generate a report based on the data.")
    st.write("The sample database is 'Chinook' in postgres sql")

    #streamlit sidebar input csv file
    st.sidebar.header("Upload CSV File (optional)")
    csv = st.sidebar.file_uploader("csv file")
    if csv:
        st.write("CSV File:", csv.name)

    #streamlit sidebar input database schema png
    st.sidebar.header("Database Schema (optional)")
    database_schema = st.sidebar.file_uploader("Database Schema")
    if database_schema:
        st.write("Database Schema:", database_schema.name)
        

    #streamlit main page input user query
    user_input = st.text_input("Ask a question that is related to your dataset")

    #streamlit main page button to generate sql query
    if st.button("Generate SQL Query"):
        try:
            sql_chain = generate_sql_query()
            sql_query = sql_chain.invoke({"question":user_input})
            st.title("SQL Query")
            st.code(sql_query)

            ans_chain = answer_question()
            answer = ans_chain.invoke({"question":user_input})
            st.title("Answer")
            st.write(answer)
        except ValueError as e:
            st.error(f"Error: {e}")


    st.image("database_schema.png", caption="database schema image")


        # if openai_api_key and database_schema and user_input:
        #     sql_query = generate_sql_query(user_input, database_schema, openai_api_key, llm_model)
        #     st.title("SQL Query")
        #     st.code(sql_query)

        #     #execute sql query
        #     conn = connect_to_database()
        #     if conn:
        #         data = conn.execute_sql_query(sql_query)

        #         if isinstance(data, pd.DataFrame):
        #             st.write("Data from the database:")
        #             st.dataframe(data)
        #         else:
        #             st.error(data)
        #     else:
        #         st.write("Failed to connect to the database.")
        # else:
        #     st.write("Please enter your OpenAI API Key, Database Schema, and your question.")


    #streamlit main page button to generate report

if __name__ == "__main__":
    main()