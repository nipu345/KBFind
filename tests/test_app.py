import numpy as np
import pytest
from fastapi.testclient import TestClient

from app.config import Settings
from app.documents import Entry, parse_markdown
from app.main import create_app
from app.search import SearchIndex
from app.store import LocalStore

VOCAB = ["password", "login", "locked", "wifi", "network", "printer", "paper"]


class FakeEmbedder:
    """Bag-of-words stand-in so tests run fast and never download a model."""

    def _vector(self, text: str) -> np.ndarray:
        words = text.lower().split()
        counts = [sum(word.startswith(v) for word in words) for v in VOCAB]
        return np.array(counts, dtype=np.float32) + 1e-3

    def embed_passages(self, texts):
        return np.vstack([self._vector(t) for t in texts])

    def embed_query(self, text):
        return self._vector(text)


DOCS = {
    "account-lockout.md": "---\ntitle: Account Lockout\ntags: [accounts]\n---\nLocked out after too many password attempts. Login fails.",
    "wireless.md": "---\ntitle: Wireless Profile\ntags: [network]\n---\nLaptop won't join the wifi network.",
    "printing.md": "---\ntitle: Print Queue\ntags: [printing]\n---\nPrinter shows jobs but no paper comes out.",
}


@pytest.fixture
def kb_dir(tmp_path):
    kb = tmp_path / "kb"
    kb.mkdir()
    for name, text in DOCS.items():
        (kb / name).write_text(text)
    return kb


def make_client(kb_dir, **overrides):
    settings = Settings(kb_dir=str(kb_dir), index_path=str(kb_dir.parent / "index.json"), **overrides)
    store = LocalStore(settings.kb_dir, settings.index_path)
    return TestClient(create_app(settings, store=store, embedder=FakeEmbedder()))


def test_parse_markdown_reads_front_matter():
    entry = parse_markdown(DOCS["wireless.md"], source="kb/wireless.md")
    assert entry.id == "wireless"
    assert entry.title == "Wireless Profile"
    assert entry.tags == ["network"]
    assert entry.body.startswith("Laptop")


def test_search_index_ranks_by_cosine_similarity():
    entries = [
        Entry(id="a", title="", body="", source="", embedding=np.array([1, 0], dtype=np.float32)),
        Entry(id="b", title="", body="", source="", embedding=np.array([0, 1], dtype=np.float32)),
    ]
    hits = SearchIndex(entries).search(np.array([0.2, 0.9], dtype=np.float32), k=2)
    assert [entry.id for entry, _ in hits] == ["b", "a"]
    assert hits[0][1] > hits[1][1]


def test_search_before_ingest_returns_409(kb_dir):
    response = make_client(kb_dir).get("/api/search", params={"q": "wifi"})
    assert response.status_code == 409


def test_ingest_then_search_returns_best_match(kb_dir):
    client = make_client(kb_dir)
    assert client.post("/api/ingest").json() == {"indexed": 3}

    results = client.get("/api/search", params={"q": "locked out, password not working", "k": 2}).json()["results"]
    assert len(results) == 2
    assert results[0]["id"] == "account-lockout"


def test_index_persists_across_app_restarts(kb_dir):
    make_client(kb_dir).post("/api/ingest")
    results = make_client(kb_dir).get("/api/search", params={"q": "printer paper"}).json()["results"]
    assert results[0]["id"] == "printing"


def test_ingest_requires_token_when_configured(kb_dir):
    client = make_client(kb_dir, ingest_token="s3cret")
    assert client.post("/api/ingest").status_code == 401
    assert client.post("/api/ingest", headers={"X-Ingest-Token": "wrong"}).status_code == 401
    assert client.post("/api/ingest", headers={"X-Ingest-Token": "s3cret"}).status_code == 200


def test_ingest_disabled_in_aws_mode_without_token(kb_dir):
    client = make_client(kb_dir, storage="aws")
    assert client.post("/api/ingest").status_code == 403
