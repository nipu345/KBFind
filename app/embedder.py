import numpy as np


class Embedder:
    """Turns text into vectors with a small sentence-embedding model.

    Uses fastembed (ONNX Runtime) instead of sentence-transformers/PyTorch, which
    keeps the container image a few hundred MB instead of several GB and makes
    Lambda cold starts tolerable. The model loads lazily on first use.
    """

    def __init__(self, model_name: str, cache_dir: str | None = None, offline: bool = False):
        self.model_name = model_name
        self._cache_dir = cache_dir
        self._offline = offline
        self._model = None

    def _get_model(self):
        if self._model is None:
            from fastembed import TextEmbedding

            self._model = TextEmbedding(
                self.model_name,
                cache_dir=self._cache_dir,
                local_files_only=self._offline,
            )
        return self._model

    def embed_passages(self, texts: list[str]) -> np.ndarray:
        return np.array(list(self._get_model().passage_embed(texts)), dtype=np.float32)

    def embed_query(self, text: str) -> np.ndarray:
        # For bge-small-en-v1.5, fastembed embeds queries and passages identically.
        # Keeping the separate calls means a model that does treat them differently
        # can be swapped in without changing the call sites.
        return np.array(next(iter(self._get_model().query_embed(text))), dtype=np.float32)
