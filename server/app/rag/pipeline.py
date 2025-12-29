from app.rag.embeddings import get_embedding
from app.rag.vectorstore import VectorStore

vector_store = VectorStore(dim=384)  # embedding dimension for OpenAI model

def add_document_chunks(chunks: list):
    vectors = [get_embedding(c) for c in chunks]
    vector_store.add(vectors, chunks)

def query_rag(question: str, top_k=5):
    q_vec = get_embedding(question)
    relevant_chunks = vector_store.search(q_vec, k=top_k)
    # later: send relevant_chunks + question to LLM for answer
    return relevant_chunks
