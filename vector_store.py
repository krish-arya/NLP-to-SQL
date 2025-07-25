import chromadb
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from dotenv import load_dotenv
import os

load_dotenv()
google_api_key = os.getenv("GOOGLE_API")

EMBED_MODEL = GoogleGenerativeAIEmbeddings(
    model="models/embedding-001",
    google_api_key=google_api_key
)

def create_schema_store(schema_text_chunks, persist_dir="schema_db"):
    client = chromadb.PersistentClient(path=persist_dir)
    collection = client.get_or_create_collection(name="schema_memory")
    for i, text in enumerate(schema_text_chunks):
        embedding = EMBED_MODEL.embed_query(text)
        collection.add(
            ids=[f"chunk_{i}"],
            embeddings=[embedding],
            documents=[text]
        )
    return collection

def query_schema_store(collection, question, k=3):
    query_embedding = EMBED_MODEL.embed_query(question)
    results = collection.query(query_embeddings=[query_embedding], n_results=k)
    return [doc for doc in results["documents"][0]]
