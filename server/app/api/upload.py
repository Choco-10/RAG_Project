from fastapi import APIRouter, UploadFile, File, HTTPException
from celery.result import AsyncResult
from app.rag.pipeline import ingest_document, vector_store
from app.loaders.pdf import load_pdf
from app.celery_worker import celery_app
import os
import uuid

router = APIRouter()

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

MAX_UPLOAD_MB = 25
MAX_UPLOAD_BYTES = MAX_UPLOAD_MB * 1024 * 1024
ALLOWED_EXTENSIONS = {"pdf"}
ALLOWED_CONTENT_TYPES = {"application/pdf"}

@router.post("")
async def upload_file(file: UploadFile = File(...)):
    if not file.filename:
        raise HTTPException(status_code=400, detail="Missing filename")

    ext = file.filename.rsplit(".", 1)[-1].lower() if "." in file.filename else ""
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=400, detail=f"Unsupported file type: {ext}")

    if file.content_type not in ALLOWED_CONTENT_TYPES:
        raise HTTPException(status_code=400, detail=f"Unsupported content type: {file.content_type}")

    raw = await file.read()
    if not raw:
        raise HTTPException(status_code=400, detail="Empty file")
    if len(raw) > MAX_UPLOAD_BYTES:
        raise HTTPException(status_code=413, detail=f"File too large. Max allowed is {MAX_UPLOAD_MB}MB")

    file_id = str(uuid.uuid4())
    safe_name = f"{file_id}.{ext}"
    save_path = os.path.join(UPLOAD_DIR, safe_name)

    with open(save_path, "wb") as f:
        f.write(raw)

    text = load_pdf(save_path)
    if not text or not text.strip():
        raise HTTPException(status_code=422, detail="No extractable text found in PDF")

    task = ingest_document.delay(text, source=file.filename)

    return {
        "message": "File uploaded successfully",
        "task_id": task.id,
        "status": "processing"
    }

@router.get("/task/{task_id}")
def task_status(task_id: str):
    task = AsyncResult(task_id, app=celery_app)
    response = {"task_id": task_id, "state": task.state}
    if task.state == "SUCCESS":
        response["result"] = task.result
    elif task.state == "FAILURE":
        response["error"] = str(task.result)
    return response

@router.get("/documents")
def list_documents():
    return {"documents": vector_store.list_documents()}