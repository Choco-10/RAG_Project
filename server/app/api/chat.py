from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
import json

from app.rag.pipeline import query_rag, retriever, memory
from app.llm.llm_model import stream_answer

router = APIRouter()

class ChatRequest(BaseModel):
    session_id: str
    question: str
    top_k: int = Field(default=5, ge=1, le=20)

def _format_history(messages, max_messages: int = 6) -> str:
    recent = messages[-max_messages:]
    lines = []
    for msg in recent:
        role = msg.get("role", "user")
        content = msg.get("content", "")
        lines.append(f"{role}: {content}")
    return "\n".join(lines)

@router.post("")
def chat(req: ChatRequest):
    return query_rag(
        question=req.question,
        session_id=req.session_id,
        top_k=req.top_k
    )

@router.post("/stream")
def chat_stream(req: ChatRequest):
    def event_generator():
        memory.add_message(req.session_id, "user", req.question)

        retrieved = retriever.retrieve(req.question, top_k=req.top_k)
        history = memory.get_history(req.session_id)
        history_text = _format_history(history)

        if not retrieved:
            answer = "No relevant documents found."
            yield f"data: {json.dumps({'token': answer})}\n\n"
            memory.add_message(req.session_id, "assistant", answer)
            yield "data: [DONE]\n\n"
            return

        context = "\n".join([r["text"] for r in retrieved])
        sources = [{"source": r.get("source", "unknown"), "chunk_id": r.get("chunk_id", -1)} for r in retrieved]

        parts = []
        for token in stream_answer(req.question, context, history=history_text):
            parts.append(token)
            yield f"data: {json.dumps({'token': token})}\n\n"

        final_answer = "".join(parts).strip() or "No response generated."
        memory.add_message(req.session_id, "assistant", final_answer)

        yield f"data: {json.dumps({'sources': sources, 'done': True})}\n\n"
        yield "data: [DONE]\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")