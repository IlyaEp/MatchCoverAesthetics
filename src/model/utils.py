import faiss
import numpy as np
from typing import List


class SongRetrieval:
    def __init__(self, dim: int):
        self._index = faiss.IndexFlatL2(dim)
        self._labels = None

    def fit(self, embeddings: np.array, labels: List[str]):
        faiss.normalize_L2(embeddings)
        self._index.add(embeddings)
        self._labels = np.asarray(labels)

    def predict(self, embedding: np.array, k: int) -> List[str]:
        faiss.normalize_L2(embedding)
        _, neighbors_idx = self._index.search(embedding, k)
        return self._labels[neighbors_idx].tolist()[0]
