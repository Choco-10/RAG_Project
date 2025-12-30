from typing import List, Dict
import numpy as np
from app.rag.vectorstore import VectorStore

class Retriever:
    def __init__(self, vector_store: VectorStore):
        self.vector_store = vector_store

    def retrieve(
        self,
        query_vector: List[float],
        top_k: int = 5,
        score_threshold: float = None
    ) -> List[Dict]:
        """
        Returns list of:
        {
            "text": str,
            "score": float,
            "metadata": dict
        }
        """

        if not self.vector_store.texts:
            return []

        D, I = self.vector_store.index.search(
            np.array([query_vector]).astype("float32"),
            top_k
        )

        results = []

        for idx, dist in zip(I[0], D[0]):
            if idx < 0 or idx >= len(self.vector_store.texts):
                continue

            score = float(dist)

            if score_threshold is not None and score > score_threshold:
                continue

            results.append({
                "text": self.vector_store.texts[idx],
                "score": score,
                "metadata": self.vector_store.metadata[idx]
            })

        return results
