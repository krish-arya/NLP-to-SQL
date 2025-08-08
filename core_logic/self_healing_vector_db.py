import chromadb
from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
from dotenv import load_dotenv
import os, json

load_dotenv()
GOOGLE_API_KEY = os.getenv("GOOGLE_API")
EMBED_MODEL = GoogleGenerativeAIEmbeddings(
    model="models/embedding-001",
    google_api_key=GOOGLE_API_KEY
)

client = chromadb.PersistentClient(path="error_pattern_db")
collection = client.get_or_create_collection(name="error_memory")

def vectorize_error(schema, sql, error, context=""):
    text = f"SCHEMA:\n{schema}\n\nSQL:\n{sql}\n\nERROR:\n{error}\nCONTEXT:\n{context}"
    return EMBED_MODEL.embed_query(text), text

def store_error_pattern(schema, sql, error, context, fix_sql):
    embedding, text = vectorize_error(schema, sql, error, context)
    doc_id = f"err_{abs(hash(text)) % (10**12)}"
    collection.add(
        ids=[doc_id],
        embeddings=[embedding],
        documents=[text],
        metadatas=[{
            "schema": schema,
            "sql": sql,
            "error": error,
            "context": context,
            "fix_sql": fix_sql
        }]
    )

def search_similar_errors(schema, sql, error, context="", top_k=3):
    embedding, _ = vectorize_error(schema, sql, error, context)
    results = collection.query(query_embeddings=[embedding], n_results=top_k)
    found = []
    for doc, meta in zip(results['documents'][0], results['metadatas'][0]):
        found.append({"text": doc, "meta": meta})
    return found

def prompt_gemini_with_error(schema, sql, error, context, similar_case=None):
    llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash", google_api_key=GOOGLE_API_KEY)
    prompt = f"""
You are a SQL expert agent. A query failed.
Current SCHEMA:
{schema}
FAILED SQL:
{sql}
ERROR:
{error}
"""
    if similar_case:
        prompt += f"\nA similar error previously occurred:\n---\nPREVIOUS SCHEMA:\n{similar_case['schema']}\nFAILED SQL:\n{similar_case['sql']}\nERROR:\n{similar_case['error']}\nPREVIOUS FIX SQL:\n{similar_case.get('fix_sql', '')}\n---\n"
    prompt += "\nUsing all context, suggest a corrected SQL. Output only SQL."
    result = llm.invoke(prompt)
    return result['content'] if isinstance(result, dict) and 'content' in result else str(result)
