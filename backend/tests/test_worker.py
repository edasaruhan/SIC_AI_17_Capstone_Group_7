from uuid import UUID, uuid4

import dramatiq
from app.platform.config import get_settings
from app.platform.jobs import dispatch, process_event
from conftest import auth_headers, identifier
from dramatiq.brokers.redis import RedisBroker
from fastapi.testclient import TestClient
from test_imports import upload_csv


def test_real_redis_delivery(client: TestClient, tenants: dict) -> None:
    # A fresh namespace cannot consume or flush any development/user queue.
    broker = RedisBroker(
        url=get_settings().redis_url.get_secret_value(), namespace=f"gp-test-{uuid4()}"
    )

    @dramatiq.actor(broker=broker, max_retries=0)
    def handle(tenant_id: str, event_id: str) -> None:
        process_event(UUID(tenant_id), UUID(event_id))

    tenant = tenants["a"]
    headers = auth_headers(tenant)
    batch = upload_csv(client, tenant, b"name,id\nRedis Synthetic,R1")
    base = f"/api/v1/imports/{batch['id']}"
    client.put(
        base + "/mapping", headers=headers, json={"fields": {"name": "name", "external_id": "id"}}
    )
    client.post(base + "/commit", headers=headers)

    def enqueue(t: str, e: str) -> None:
        handle.send(t, e)

    worker = dramatiq.Worker(broker, worker_threads=1, worker_timeout=100)
    worker.start()
    try:
        assert dispatch(identifier(tenant["tenant"]), enqueue) >= 1
        broker.join("default", timeout=10000)
        assert client.get(base, headers=headers).json()["status"] == "succeeded"
        assert client.get("/api/v1/customers", headers=headers).json()["total"] == 1
    finally:
        worker.stop(timeout=5000)
        broker.close()
