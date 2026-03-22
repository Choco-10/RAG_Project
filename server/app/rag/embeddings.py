import os
from sentence_transformers import SentenceTransformer
from typing import List


def _env_true(name: str) -> bool:
    return os.getenv(name, "").strip().lower() in {"1", "true", "yes", "on"}


EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")
LOCAL_FILES_ONLY = (
    _env_true("LOCAL_FILES_ONLY")
    or _env_true("HF_HUB_OFFLINE")
    or _env_true("TRANSFORMERS_OFFLINE")
)

# Load small, fast pre-trained model
try:
    embed_model = SentenceTransformer(
        EMBEDDING_MODEL,
        local_files_only=LOCAL_FILES_ONLY,
    )
except Exception as e:
    raise RuntimeError(
        f"Failed to load embedding model '{EMBEDDING_MODEL}'. "
        "If running offline, first download model files with internet once, "
        "then set HF_HUB_OFFLINE=1 and TRANSFORMERS_OFFLINE=1. "
        f"Original error: {e}"
    ) from e

def get_embedding(text: str) -> List[float]:
    """
    Converts text into an embedding vector.
    
    Args:
        text: Text string to embed.
    
    Returns:
        List of floats representing embedding.
    """
    return embed_model.encode(text).tolist()
