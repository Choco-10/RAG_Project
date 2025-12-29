from fastapi import FastAPI
from app.api import upload, chat

app = FastAPI(title="RAG Server")

# register routes
app.include_router(upload.router, prefix="/upload", tags=["Upload"])
app.include_router(chat.router, prefix="/chat", tags=["Chat"])

@app.get("/")
def health_check():
    return {"status": "RAG server running"}
