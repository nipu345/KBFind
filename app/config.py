"""Runtime configuration, read from environment variables.

The same container image runs locally (STORAGE=local: markdown files and a JSON
index on disk) and on Lambda (STORAGE=aws: S3 for documents, DynamoDB for the
index), so everything environment-specific is set here and nowhere else.
"""

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    storage: str = "local"
    kb_dir: str = "kb"
    index_path: str = "data/index.json"
    s3_bucket: str = ""
    s3_prefix: str = "kb/"
    table_name: str = ""
    model_name: str = "BAAI/bge-small-en-v1.5"
    model_cache_dir: str | None = None
    model_offline: bool = False
    ingest_token: str = ""

    @classmethod
    def from_env(cls) -> "Settings":
        return cls(
            storage=os.getenv("STORAGE", cls.storage),
            kb_dir=os.getenv("KB_DIR", cls.kb_dir),
            index_path=os.getenv("INDEX_PATH", cls.index_path),
            s3_bucket=os.getenv("S3_BUCKET", cls.s3_bucket),
            s3_prefix=os.getenv("S3_PREFIX", cls.s3_prefix),
            table_name=os.getenv("TABLE_NAME", cls.table_name),
            model_name=os.getenv("MODEL_NAME", cls.model_name),
            model_cache_dir=os.getenv("MODEL_CACHE_DIR") or None,
            model_offline=os.getenv("MODEL_OFFLINE", "0") == "1",
            ingest_token=os.getenv("INGEST_TOKEN", cls.ingest_token),
        )
