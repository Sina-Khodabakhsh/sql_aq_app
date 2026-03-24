import pandas as pd
from pydantic import BaseModel, Field
from sqlalchemy import create_engine
from sqlalchemy.engine import URL
from sqlalchemy import inspect
from langchain_openai import ChatOpenAI
from langchain_community.utilities import SQLDatabase
from langchain_core.messages import SystemMessage, HumanMessage
import streamlit as st
import os
from dotenv import load_dotenv

load_dotenv()

os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY", "")
os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_API_KEY"] = os.getenv("LANGCHAIN_API_KEY", "")

class SQLResponse(BaseModel):
    sql: str = Field(description="Exactly one valid Microsoft SQL Server SELECT query.")
    answer_intent: str = Field(description="Short business meaning of the SQL query.")

class FinalAnswer(BaseModel):
    answer: str = Field(description="A clear business-friendly answer based on the SQL result.")

connection_url = URL.create(
    "mssql+pyodbc",
    host="YOUR_SERVER_NAME",
    database="YOUR_DATABASE_NAME",
    query={
        "driver": "ODBC Driver 17 for SQL Server",
        "trusted_connection": "yes",
    },
)

engine = create_engine(connection_url)

inspector = inspect(engine)
allowed_schema = 'dbo'
tables= inspector.get_table_names(schema=allowed_schema)

#Exluding Unnecessary sys tables
excluded_tables = {"sysdiagrams"}
tables = [t for t in tables if t not in excluded_tables]

db = SQLDatabase(
    engine,
    include_tables=tables
)

SCHEMA_INFO = db.get_table_info()

llm = ChatOpenAI(model="gpt-4.1-mini", temperature=0)
sql_llm = llm.with_structured_output(SQLResponse)
answer_llm = llm.with_structured_output(FinalAnswer)

def generate_sql_from_question(user_question: str) -> SQLResponse:
    system_prompt = f"""
You are a senior SQL generator for Microsoft SQL Server.

Your task is to convert the user's business question into SQL.

Rules:
- Return exactly one SQL statement
- Only SELECT is allowed
- The SQL must be valid for Microsoft SQL Server
- Use TOP, not LIMIT
- Do not generate INSERT, UPDATE, DELETE, DROP, ALTER, TRUNCATE, EXEC, or MERGE
- Use only the tables that exist in the provided schema
- Prefer clear joins using keys
- Keep the query as simple and efficient as possible
- Do not invent columns or tables

Available schema:
{SCHEMA_INFO}
"""
    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=user_question)
    ]
    return sql_llm.invoke(messages)

def validate_sql(sql_text: str) -> None:
    sql_upper = sql_text.strip().upper()

    forbidden = [
        "INSERT ", "UPDATE ", "DELETE ", "DROP ",
        "ALTER ", "TRUNCATE ", "EXEC ", "MERGE "
    ]

    if not sql_upper.startswith("SELECT"):
        raise ValueError("Only SELECT statements are allowed.")

    if any(word in sql_upper for word in forbidden):
        raise ValueError("Unsafe SQL detected.")

def run_sql_query(sql_query: str) -> pd.DataFrame:
    return pd.read_sql_query(sql_query, engine)

def dataframe_to_compact_text(df, max_rows=20):
    if df.empty:
        return "No rows returned."
    return df.head(max_rows).to_csv(index=False)

def generate_text_answer(user_question: str, sql_query: str, sql_result_preview: str) -> str:
    system_prompt = """
You are a business analyst.

Your task is to write a short, clear, user-friendly answer based ONLY on:
1) the user's question
2) the SQL query
3) the SQL execution result preview

Rules:
- Do not invent numbers
- Do not add information not present in the result
- Keep the answer concise and natural
- If the result is empty, clearly say that no matching data was found
"""
    human_prompt = f"""
User question:
{user_question}

Generated SQL:
{sql_query}

SQL result preview:
{sql_result_preview}
"""
    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=human_prompt)
    ]
    return answer_llm.invoke(messages).answer

def ask_database(user_question: str):
    sql_response = generate_sql_from_question(user_question)
    validate_sql(sql_response.sql)

    df = run_sql_query(sql_response.sql)
    result_preview = dataframe_to_compact_text(df)

    final_answer = generate_text_answer(
        user_question=user_question,
        sql_query=sql_response.sql,
        sql_result_preview=result_preview
    )

    return {
        "intent": sql_response.answer_intent,
        "sql": sql_response.sql,
        "dataframe": df,
        "answer": final_answer
    }

st.set_page_config(page_title="SQL QA App", layout="wide")
st.title("SQL Question Answering App")

with st.form("question_form"):
    user_question = st.text_area("Enter your question:")
    submitted = st.form_submit_button("Run")

if submitted:
    try:
        output = ask_database(user_question)

        st.subheader("Intent")
        st.write(output["intent"])

        st.subheader("Generated SQL")
        st.code(output["sql"], language="sql")

        st.subheader("Answer")
        st.write(output["answer"])

        with st.expander("SQL Result Table"):
            st.dataframe(output["dataframe"])

    except Exception as e:
        st.error(str(e))