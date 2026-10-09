import numpy as np

from .documents import Entry


class SearchIndex:
    """Brute-force cosine similarity over an in-memory matrix.

    Fine for hundreds or a few thousand entries. Past that, the vectors belong in
    a real vector index (OpenSearch k-NN, pgvector) instead of a full scan.
    """

    def __init__(self, entries: list[Entry]):
        self.entries = entries
        if entries:
            matrix = np.vstack([entry.embedding for entry in entries]).astype(np.float32)
            self._matrix = matrix / (np.linalg.norm(matrix, axis=1, keepdims=True) + 1e-12)
        else:
            self._matrix = np.empty((0, 0), dtype=np.float32)

    def __len__(self) -> int:
        return len(self.entries)

    def search(self, query_vector: np.ndarray, k: int) -> list[tuple[Entry, float]]:
        if not self.entries:
            return []
        query = query_vector / (np.linalg.norm(query_vector) + 1e-12)
        scores = self._matrix @ query
        top = np.argsort(-scores)[:k]
        return [(self.entries[i], float(scores[i])) for i in top]
