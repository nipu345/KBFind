"""Where source documents come from and where the embedded index is kept.

LocalStore: markdown in a folder, index in a JSON file. Used for development.
AwsStore:   markdown in S3, index in DynamoDB. Used on Lambda, where the
            filesystem is read-only apart from /tmp and doesn't survive
            between instances anyway.
"""

import json
from pathlib import Path

import numpy as np

from .config import Settings
from .documents import Entry, parse_markdown


class LocalStore:
    def __init__(self, kb_dir: str, index_path: str):
        self.kb_dir = Path(kb_dir)
        self.index_path = Path(index_path)

    def load_documents(self) -> list[Entry]:
        return [
            parse_markdown(path.read_text(encoding="utf-8"), source=str(path))
            for path in sorted(self.kb_dir.glob("*.md"))
        ]

    def save_index(self, entries: list[Entry]) -> None:
        self.index_path.parent.mkdir(parents=True, exist_ok=True)
        rows = [
            {
                "id": e.id,
                "title": e.title,
                "body": e.body,
                "source": e.source,
                "tags": e.tags,
                "embedding": e.embedding.tolist(),
            }
            for e in entries
        ]
        self.index_path.write_text(json.dumps(rows), encoding="utf-8")

    def load_index(self) -> list[Entry]:
        if not self.index_path.exists():
            return []
        rows = json.loads(self.index_path.read_text(encoding="utf-8"))
        return [
            Entry(
                id=row["id"],
                title=row["title"],
                body=row["body"],
                source=row["source"],
                tags=row["tags"],
                embedding=np.array(row["embedding"], dtype=np.float32),
            )
            for row in rows
        ]


class AwsStore:
    def __init__(self, bucket: str, prefix: str, table_name: str):
        import boto3

        self.bucket = bucket
        self.prefix = prefix
        self.s3 = boto3.client("s3")
        self.table = boto3.resource("dynamodb").Table(table_name)

    def load_documents(self) -> list[Entry]:
        entries = []
        paginator = self.s3.get_paginator("list_objects_v2")
        for page in paginator.paginate(Bucket=self.bucket, Prefix=self.prefix):
            for obj in page.get("Contents", []):
                key = obj["Key"]
                if not key.endswith(".md"):
                    continue
                raw = self.s3.get_object(Bucket=self.bucket, Key=key)["Body"].read()
                entries.append(parse_markdown(raw.decode("utf-8"), source=f"s3://{self.bucket}/{key}"))
        return entries

    def save_index(self, entries: list[Entry]) -> None:
        new_ids = {e.id for e in entries}
        stale_ids = [
            item["id"]
            for item in self._scan(ProjectionExpression="#id", ExpressionAttributeNames={"#id": "id"})
            if item["id"] not in new_ids
        ]
        with self.table.batch_writer() as batch:
            for e in entries:
                batch.put_item(
                    Item={
                        "id": e.id,
                        "title": e.title,
                        "body": e.body,
                        "source": e.source,
                        "tags": e.tags,
                        # float32 bytes: 384 dims = ~1.5 KB per item, well under DynamoDB's 400 KB limit
                        "embedding": e.embedding.astype(np.float32).tobytes(),
                    }
                )
            for doc_id in stale_ids:
                batch.delete_item(Key={"id": doc_id})

    def load_index(self) -> list[Entry]:
        return [
            Entry(
                id=item["id"],
                title=item["title"],
                body=item["body"],
                source=item["source"],
                tags=list(item.get("tags", [])),
                embedding=np.frombuffer(item["embedding"].value, dtype=np.float32),
            )
            for item in self._scan()
        ]

    def _scan(self, **kwargs):
        while True:
            page = self.table.scan(**kwargs)
            yield from page.get("Items", [])
            if "LastEvaluatedKey" not in page:
                return
            kwargs["ExclusiveStartKey"] = page["LastEvaluatedKey"]


def make_store(settings: Settings) -> LocalStore | AwsStore:
    if settings.storage == "aws":
        return AwsStore(settings.s3_bucket, settings.s3_prefix, settings.table_name)
    return LocalStore(settings.kb_dir, settings.index_path)
