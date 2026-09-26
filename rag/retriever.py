import os
import chromadb
from chromadb.utils import embedding_functions

DOCS_DIR   = os.path.join(os.path.dirname(__file__), "..", "data", "knowledge_docs")
CHROMA_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "chroma_db")

def search_query(query, n_results=4):
    ef=embedding_functions.SentenceTransformerEmbeddingFunction(
        model_name="all-MiniLM-L6-v2"
    )
    client= chromadb.PersistentClient(CHROMA_DIR)

    collection = client.get_collection("sales_knowledge", embedding_function=ef)

    result = collection.query(query_texts=[query],n_results= n_results)

    """
    result["ids"][0]        # → ["credit_policy_3", "credit_policy_4"]
    result["documents"][0]  # → ["Utilization above 95%...", "Do NOT place order..."]
    result["metadatas"][0]  # → [{"source": "credit_policy"}, {"source": "credit_policy"}]
    result["distances"][0]  # → [0.18, 0.24]
    """

    chunks= result["documents"][0]
    sources= result["metadatas"][0]
    output=[]

    for source, chunk in  zip(sources,chunks):
        output.append(f"[{source['source']}] {chunk}")

    return output 
