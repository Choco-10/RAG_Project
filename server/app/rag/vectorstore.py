import faiss
import numpy as np

class VectorStore:
    def __init__(self, dim: int):
        self.dim = dim
        self.index = faiss.IndexFlatL2(dim)  # simple L2 index
        self.texts = []  # store actual chunks for retrieval

    def add(self, vectors: list, texts: list):
        self.index.add(np.array(vectors).astype("float32"))
        self.texts.extend(texts)

    def search(self, query_vec, k=5):
        if not self.texts:
            return ["No documents uploaded yet."]
        D, I = self.index.search(np.array([query_vec]), k)
        return [self.texts[i] for i in I[0]]
