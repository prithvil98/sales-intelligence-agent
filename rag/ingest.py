import os
import chromadb
from chromadb.utils import embedding_functions


DOCS_DIR   = os.path.join(os.path.dirname(__file__), "..", "data", "knowledge_docs")
CHROMA_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "chroma_db")

"""
Start at rag/ingest.py
Go up one folder (..) → now at Sales Agent/
Go into data/knowledge_docs/ → that's DOCS_DIR
Go into data/chroma_db/ → that's CHROMA_DIR (ChromaDB will create this folder automatically)
"""

def chunk_text(text,size,overlap):
    chunks=[]
    start=0

    while(start < len(text)):
        end= start + size 
        chunk = text[start:end]
        if chunk.strip():
            chunks.append(chunk.strip())
        start= start + (size - overlap)

    return chunks

def ingest():    
    # Step 1 — create ChromaDB client
    ef= embedding_functions.SentenceTransformerEmbeddingFunction(
        model_name="all-MiniLM-L6-v2"
    )
    client=chromadb.PersistentClient(CHROMA_DIR)

    # Step 2 — get or create collection
    collection = client.get_or_create_collection("sales_knowledge",embedding_function= ef)

    """
    os.listdir()     → ["product_catalog.txt", "credit_policy.txt", "sales_guidelines.txt"]
                              ↓
    endswith(".txt") → skip any non-txt files
                                ↓
    os.path.join()   → builds full file path
                                ↓
    open() + read()  → loads entire file content into text variable
                                ↓
    chunk_text()     → splits text into chunks  ← next step
    """

    # Step 3 — loop over files in DOCS_DIR
    for fname in os.listdir(DOCS_DIR):
        if not fname.endswith(".txt"):
            continue

        fpath = os.path.join(DOCS_DIR,fname)

        with open(fpath,encoding="utf-8") as f:
            text= f.read() #Opens the file and stores the entire content in one big string

        # Step 5 — chunk it
        chunks= chunk_text(text,400,80)

        source = fname.replace(".txt", "")   # → "product_catalog"

        ids=[]
        metas=[]
        for i, chunk in enumerate(chunks):
            ids.append(f"{source}_{i}")   # → "product_catalog_0", "product_catalog_1"
            metas.append({"source": source})   # → {"source": "product_catalog"}

        collection.add(
            documents=chunks,
            ids=ids,
            metadatas=metas

        )

        # Step 8 — print result
        print(f"✓ {fname} — {len(chunks)} chunks ingested")

        """
        documents — the actual text chunks. This is what gets embedded into vectors and searched later.

        ids — unique identifier for each chunk. Must be a string. Used to avoid duplicates. If you add the same id twice, ChromaDB throws an error.

        metadatas — extra info stored alongside each chunk. When the agent retrieves a chunk, it can also see where it came from — "source": "credit_policy" tells the agent this answer came from the credit policy doc.
        """


if __name__ == "__main__":
    ingest()



