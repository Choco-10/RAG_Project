from sentence_transformers import SentenceTransformer

# Load a free pre-trained model
model = SentenceTransformer('all-MiniLM-L6-v2')  # small, fast, free

def get_embedding(text: str) -> list:
    """
    Converts text to embedding vector using local model.
    """
    return model.encode(text).tolist()  # returns a float list
