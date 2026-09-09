"""Redis-backed fixed-window boundary; keys contain no raw token or customer identifier."""

import hashlib
from typing import Protocol


class CounterStore(Protocol):
    def incr(self, key: str) -> int: ...

    def expire(self, key: str, seconds: int) -> object: ...


def protected_rate_key(namespace: str, scope: str, subject: str, window: int) -> str:
    digest = hashlib.sha256(subject.encode()).hexdigest()[:32]
    return f"{namespace}:rate:{scope}:{window}:{digest}"


def allow_request(store: CounterStore, key: str, *, limit: int, window_seconds: int) -> bool:
    count = store.incr(key)
    if count == 1:
        store.expire(key, window_seconds)
    return count <= limit
