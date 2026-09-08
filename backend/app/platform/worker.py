"""Dramatiq transport entrypoint. Business state and authorization stay in PostgreSQL."""

from uuid import UUID

import dramatiq
from dramatiq.brokers.redis import RedisBroker

from app.platform.config import get_settings
from app.platform.jobs import process_event

# RedisBroker's third-party constructor lacks annotations in Dramatiq 2.2.1.
broker = RedisBroker(  # type: ignore[no-untyped-call]
    url=get_settings().redis_url.get_secret_value(),
    namespace=get_settings().redis_namespace,
)
dramatiq.set_broker(broker)


@dramatiq.actor(max_retries=0, time_limit=120000)
def deliver_event(tenant_id: str, event_id: str) -> None:
    # Bounded retries/leases are in the outbox, not two competing retry loops.
    try:
        process_event(UUID(tenant_id), UUID(event_id))
    except Exception:
        raise RuntimeError("Worker execution failed; durable outbox will retry") from None


def enqueue(tenant_id: str, event_id: str) -> None:
    deliver_event.send(tenant_id, event_id)
