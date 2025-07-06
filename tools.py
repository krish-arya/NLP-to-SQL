from langchain_core.tools import tool
import os
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API"))


@tool
def generate_sql_tool(question, schema_context):
    """
    Use Gemini to convert a question (possibly in Hindi or other Indian languages)
    plus schema context into SQL.
    """
    from google.generativeai import GenerativeModel
    model = GenerativeModel("gemini-2.0-flash")
    
    prompt = f"""
You are a highly skilled SQL expert who understands multiple languages, including Indian languages such as Hindi, Tamil, Bengali, Marathi, etc.

TASK:
- The USER QUESTION may be in Hindi or any other Indian language.
- Your job is to understand it and generate a valid SQL query in English.

RULES:
- Always produce syntactically correct SQL in English.
- Use the provided database schema context carefully.

USER QUESTION:
{question}

SCHEMA CONTEXT:
{schema_context}

Output only the SQL.
"""
    response = model.generate_content(prompt)
    return response.text.strip()


@tool
def execute_sql_tool(connection_string, sql):
    """
    Execute the SQL and return results.
    """
    from sqlalchemy import create_engine, text
    engine = create_engine(connection_string)
    with engine.connect() as conn:
        result = conn.execute(text(sql))
        rows = result.fetchall()
        columns = result.keys()
    return f"Columns: {columns}\nRows: {rows}"
