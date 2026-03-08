from chromadb import PersistentClient
from typing import List
from uuid import uuid4
from pathlib import Path
from app.rag.embeddings import get_embedding

class ChromaVectorStore:
    def __init__(self, persist_dir: str | None = None):
        # Always resolve to server/chroma (absolute), so API and Celery use same path
        default_dir = Path(__file__).resolve().parents[2] / "chroma"
        self.persist_dir = Path(persist_dir) if persist_dir else default_dir
        self.persist_dir.mkdir(parents=True, exist_ok=True)

        self.client = PersistentClient(path=str(self.persist_dir))
        self.collection = self.client.get_or_create_collection(name="documents")
        self._version = 0

    def add(self, texts: List[str], source: str):
        if not texts:
            return
        batch_id = str(uuid4())
        metadatas = [{"source": source, "chunk_id": i} for i in range(len(texts))]
        ids = [f"{batch_id}-{i}" for i in range(len(texts))]
        embeddings = [get_embedding(t) for t in texts]
        self.collection.add(documents=texts, metadatas=metadatas, ids=ids, embeddings=embeddings)
        self._version += 1

    def query(self, query: str, top_k=5):
        q_vec = get_embedding(query)
        results = self.collection.query(query_embeddings=[q_vec], n_results=top_k)
        docs = []
        documents = results.get("documents", [[]])[0]
        metadatas = results.get("metadatas", [[]])[0]
        for doc, meta in zip(documents, metadatas):
            docs.append({"text": doc, **(meta or {})})
        return docs

    def list_documents(self):
        data = self.collection.get(include=["metadatas"])
        metas = data.get("metadatas") or []
        source_to_chunks = {}

        for m in metas:
            if not isinstance(m, dict):
                continue
            source = m.get("source", "unknown")
            source_to_chunks[source] = source_to_chunks.get(source, 0) + 1

        return [{"source": k, "chunks": v} for k, v in source_to_chunks.items()]
