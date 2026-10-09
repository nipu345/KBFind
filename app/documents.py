from dataclasses import dataclass, field
from pathlib import PurePosixPath

import frontmatter
import numpy as np


@dataclass
class Entry:
    id: str
    title: str
    body: str
    source: str
    tags: list[str] = field(default_factory=list)
    embedding: np.ndarray | None = None

    def text_for_embedding(self) -> str:
        # Title carries the official terminology, body carries the symptoms
        # people actually describe. Embedding both lets either kind of query match.
        return f"{self.title}\n\n{self.body}"


def parse_markdown(raw: str, source: str) -> Entry:
    """Parse a KB entry: YAML front matter (title, tags) followed by a markdown body."""
    post = frontmatter.loads(raw)
    doc_id = PurePosixPath(source).stem
    return Entry(
        id=doc_id,
        title=str(post.get("title", doc_id)),
        body=post.content.strip(),
        source=source,
        tags=[str(tag) for tag in post.get("tags", [])],
    )
