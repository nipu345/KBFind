import secrets
import time
from pathlib import Path

from fastapi import FastAPI, Header, HTTPException, Query
from fastapi.responses import FileResponse

from .config import Settings
from .embedder import Embedder
from .search import SearchIndex
from .store import make_store

STATIC_DIR = Path(__file__).parent / "static"


def create_app(settings: Settings | None = None, store=None, embedder=None) -> FastAPI:
    settings = settings or Settings.from_env()
    store = store or make_store(settings)
    embedder = embedder or Embedder(settings.model_name, settings.model_cache_dir, settings.model_offline)

    app = FastAPI(title="KBFind")
    # Cached per process. On Lambda each warm instance holds its own copy, so an
    # instance that didn't handle the ingest keeps serving the old index until it's recycled.
    state: dict[str, SearchIndex | None] = {"index": None}

    def get_index() -> SearchIndex:
        if state["index"] is None:
            state["index"] = SearchIndex(store.load_index())
        return state["index"]

    @app.get("/", include_in_schema=False)
    def home():
        return FileResponse(STATIC_DIR / "index.html")

    @app.get("/health")
    def health():
        return {"status": "ok", "storage": settings.storage}

    @app.get("/api/search")
    def search(
        q: str = Query(min_length=2, max_length=300),
        k: int = Query(3, ge=1, le=10),
    ):
        index = get_index()
        if len(index) == 0:
            raise HTTPException(409, "Index is empty. Run POST /api/ingest first.")
        started = time.perf_counter()
        hits = index.search(embedder.embed_query(q), k)
        return {
            "query": q,
            "took_ms": round((time.perf_counter() - started) * 1000, 1),
            "results": [
                {
                    "id": entry.id,
                    "title": entry.title,
                    "tags": entry.tags,
                    "source": entry.source,
                    "body": entry.body,
                    "score": round(score, 4),
                }
                for entry, score in hits
            ],
        }

    @app.post("/api/ingest")
    def ingest(x_ingest_token: str | None = Header(default=None)):
        check_ingest_token(settings, x_ingest_token)
        entries = store.load_documents()
        if not entries:
            raise HTTPException(400, "No markdown documents found in the source location.")
        vectors = embedder.embed_passages([e.text_for_embedding() for e in entries])
        for entry, vector in zip(entries, vectors):
            entry.embedding = vector
        store.save_index(entries)
        state["index"] = SearchIndex(entries)
        return {"indexed": len(entries)}

    return app


def check_ingest_token(settings: Settings, provided: str | None) -> None:
    """Ingest re-embeds every document, so it shouldn't be callable by anyone with the URL."""
    expected = settings.ingest_token
    if not expected:
        if settings.storage == "local":
            return
        raise HTTPException(403, "Ingest is disabled: INGEST_TOKEN is not configured.")
    if not provided or not secrets.compare_digest(provided, expected):
        raise HTTPException(401, "Missing or invalid X-Ingest-Token header.")


app = create_app()
