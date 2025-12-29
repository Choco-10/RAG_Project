import os
from fastapi import APIRouter, UploadFile, File
from app.loaders.pdf import load_pdf
from app.rag.pipeline import add_document_chunks  # import the function

router = APIRouter()

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.post("/")
async def upload_file(file: UploadFile = File(...)):
    """
    Upload a file, extract text (with OCR if needed), and add chunks to vector store.
    """
    file_path = os.path.join(UPLOAD_DIR, file.filename)

    # Save uploaded file
    with open(file_path, "wb") as f:
        f.write(await file.read())

    # Only handle PDFs for now
    if file.filename.lower().endswith(".pdf"):
        try:
            text = load_pdf(file_path)

            # Split text into chunks (example: 500 chars each)
            chunk_size = 500
            chunks = [text[i:i+chunk_size] for i in range(0, len(text), chunk_size)]

            # Add chunks to vector store
            add_document_chunks(chunks)

            return {
                "filename": file.filename,
                "text_length": len(text),
                "chunks": len(chunks),
                "message": "Text extracted and added to vector store"
            }
        except Exception as e:
            return {
                "filename": file.filename,
                "text_length": 0,
                "error": str(e)
            }

    return {
        "filename": file.filename,
        "message": "Unsupported file type (only PDF for now)"
    }
