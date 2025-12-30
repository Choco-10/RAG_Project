import faiss
import numpy as np

class VectorStore:
    def __init__(self, dim: int):
        self.dim = dim
        self.index = faiss.IndexFlatL2(dim)
        self.texts = []
        self.metadata = []

    def add(self, vectors: list, texts: list, metadata: list = None):
        if metadata is None:
            metadata = [{} for _ in texts]

        self.index.add(np.array(vectors).astype("float32"))
        self.texts.extend(texts)
        self.metadata.extend(metadata)
