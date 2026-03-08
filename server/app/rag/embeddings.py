from sentence_transformers import SentenceTransformer
from typing import List

# Load small, fast pre-trained model
embed_model = SentenceTransformer('all-MiniLM-L6-v2')

def get_embedding(text: str) -> List[float]:
    """
    Converts text into an embedding vector.
    
    Args:
        text: Text string to embed.
    
    Returns:
        List of floats representing embedding.
    """
    return embed_model.encode(text).tolist()
