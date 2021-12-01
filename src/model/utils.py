import faiss
import numpy as np
from typing import List, Dict, Union
from torch import FloatTensor


class SongRetriever:
    def __init__(self, dim: int):
        self._index = faiss.IndexFlatL2(dim)
        self._labels = None

    def load_from_dict(self, data: List[Dict[str, Union[str, FloatTensor]]]):
        """
        This method initializes index and labels from the passed dicts.

        :param data: list of dicts, where each dict is expected to have `embedding` and `track_id` fields
        """
        embeddings = np.asarray([image["embedding"].numpy().ravel() for image in data])
        faiss.normalize_L2(embeddings)
        self._index.add(embeddings)
        self._labels = np.asarray([image["track_id"] for image in data])

    def predict(self, embedding: np.array, k: int) -> List[str]:
        """
        This method returns labels for k nearest neighbors of given embedding.
        """
        faiss.normalize_L2(embedding)
        _, neighbors_idx = self._index.search(embedding, k)
        return self._labels[neighbors_idx].tolist()[0]
