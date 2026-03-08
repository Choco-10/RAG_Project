from app.rag.vectorstore import ChromaVectorStore
from app.rag.retriever import HybridRetriever
from app.memory.redis import RedisMemory
from app.llm.llm_model import generate_answer
from app.utils.chunking import semantic_chunk_text
from app.celery_worker import celery_app

vector_store = ChromaVectorStore(persist_dir="chroma")
retriever = HybridRetriever(vector_store)
memory = RedisMemory()

def _format_history(messages, max_messages: int = 6) -> str:
    recent = messages[-max_messages:]
    lines = []
    for msg in recent:
        role = msg.get("role", "user")
        content = msg.get("content", "")
        lines.append(f"{role}: {content}")
    return "\n".join(lines)

@celery_app.task
def ingest_document(text: str, source: str):
    chunks = semantic_chunk_text(text)
    vector_store.add(chunks, source)
    return {"source": source, "chunks": len(chunks)}

def query_rag(question: str, session_id: str, top_k: int = 5):
    memory.add_message(session_id, "user", question)

    retrieved = retriever.retrieve(question, top_k=top_k)
    history = memory.get_history(session_id)
    history_text = _format_history(history)

    if not retrieved:
        answer = "No relevant documents found."
        sources = []
    else:
        context = "\n".join([r["text"] for r in retrieved])
        answer = generate_answer(question, context, history=history_text)
        sources = [{"source": r.get("source", "unknown"), "chunk_id": r.get("chunk_id", -1)} for r in retrieved]

    memory.add_message(session_id, "assistant", answer)
    return {"answer": answer, "sources": sources}