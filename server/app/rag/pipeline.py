from app.memory.redis import RedisMemory
from app.rag.retriever import Retriever
from app.rag.vectorstore import VectorStore
from app.rag.embeddings import get_embedding
from app.llm.llm_model import generate_answer

# 1. Initialize components
vector_store = VectorStore(dim=384)   # embedding dim of sentence-transformers 'all-MiniLM-L6-v2'
retriever = Retriever(vector_store)
memory = RedisMemory()

# 2. Function to add document chunks
def add_document_chunks(chunks: list, source: str):
    """
    Adds text chunks to vector store with metadata.
    """
    vectors = []
    metadata = []

    for i, chunk in enumerate(chunks):
        vectors.append(get_embedding(chunk))
        metadata.append({
            "source": source,
            "chunk_id": i
        })

    vector_store.add(vectors, chunks, metadata)

# 3. Query function
def query_rag(
    question: str,
    session_id: str,
    top_k: int = 5
):
    """
    Full RAG query pipeline:
    1. Store user message in memory
    2. Retrieve relevant context from vector store
    3. Generate LLM answer using context
    4. Store assistant answer in memory
    5. Return answer, sources, and chat history
    """
    # --- Store user message ---
    memory.add_message(session_id, "user", question)

    # --- Retrieve relevant chunks ---
    q_vec = get_embedding(question)
    retrieved = retriever.retrieve(q_vec, top_k=top_k)

    context = "\n\n".join([r["text"] for r in retrieved]) if retrieved else "No relevant documents found."

    # --- Generate answer ---
    answer = generate_answer(question, context)

    # --- Store assistant message ---
    memory.add_message(session_id, "assistant", answer)

    return {
        "answer": answer,
        "sources": retrieved,
        "history": memory.get_history(session_id)
    }
