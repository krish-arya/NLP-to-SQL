import chromadb
from langchain_community.embeddings import GoogleGenerativeAIEmbeddings

EMBED_MODEL = GoogleGenerativeAIEmbeddings(model="models/embedding-001")

def create_schema_store(schema_text_chunks, persist_dir="schema_db"):
    """
    Store schema chunks in a vector DB for retrieval.
    """
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
