import json
from datetime import datetime, timezone
from hashlib import sha256

from django.utils.dateparse import parse_datetime

GENESIS_TIMESTAMP = datetime(2022, 6, 7, 12, 55, 0, tzinfo=timezone.utc)
TIMESTAMP_FORMAT = '%Y-%m-%dT%H:%M:%S.%f'


def parse_timestamp(value) -> datetime:
    if value is None:
        return datetime.now(timezone.utc)

    if isinstance(value, str):
        parsed = parse_datetime(value)
        if not parsed:
            raise ValueError(f"Unparseable timestamp: {value!r}")
        value = parsed

    if not isinstance(value, datetime):
        raise TypeError(f"Unsupported timestamp type: {type(value).__name__}")

    if value.tzinfo is None:
        value = value.replace(tzinfo=timezone.utc)

    return value.astimezone(timezone.utc)


def canonical_timestamp(value) -> str:
    return parse_timestamp(value).strftime(TIMESTAMP_FORMAT) + "Z"


class Block:
    def __init__(self, index, transaction, previous_hash, created_at = None, nonce=0, hash=None, **kwargs):
        self.index = index
        self.transaction = transaction
        self.previous_hash = previous_hash
        self.nonce = nonce
        self.hash = hash
        self.created_at = parse_timestamp(created_at)

    def compute_hash(self):
        payload = {
            "index": self.index,
            "transaction": self.transaction,
            "previous_hash": self.previous_hash,
            "nonce": self.nonce,
            "created_at": canonical_timestamp(self.created_at),
        }
        return sha256(json.dumps(payload, sort_keys=True).encode()).hexdigest()

def genesis_block() -> Block:
    return Block(index=0, transaction=[], previous_hash="0", created_at=GENESIS_TIMESTAMP)


GENESIS_HASH = genesis_block().compute_hash()
