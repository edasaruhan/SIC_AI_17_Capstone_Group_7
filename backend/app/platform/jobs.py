"""Tenant-scoped durable dispatch. Redis loss results in redelivery, not lost state."""

from collections.abc import Callable
from datetime import UTC, datetime, timedelta
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.identity.context import TenantContext
from app.identity.models import Membership
from app.identity.permissions import ROLE_PERMISSIONS, Permission
from app.imports.service import commit_batch, get_batch
from app.integrations import service as integration_service
from app.integrations.models import IntegrationSyncRun
from app.integrations.providers import provider_for
from app.intelligence import service as intelligence_service
from app.intelligence.models import ScoringJob
from app.platform.audit import OutboxEvent
from app.platform.db import get_engine, set_context
from app.platform.storage import get_object_store

MAX_DELIVERIES = 5


def dispatch(tenant_id: UUID, enqueue: Callable[[str, str], None]) -> int:
    count = 0
    with Session(get_engine()) as session, session.begin():
        set_context(session, actor_id=UUID(int=0), tenant_id=tenant_id)
        events = session.scalars(
            select(OutboxEvent)
            .where(
                OutboxEvent.tenant_id == tenant_id,
                OutboxEvent.status.in_(["pending", "queued"]),
                OutboxEvent.available_at <= datetime.now(UTC),
            )
            .order_by(OutboxEvent.created_at)
            .limit(100)
            .with_for_update(skip_locked=True)
        )
        for event in events:
            if event.attempts >= MAX_DELIVERIES:
                event.status = "failed"
                event.last_error = "delivery_attempts_exhausted"
                if event.event_type == "import.commit_requested":
                    ctx = TenantContext(
                        session, tenant_id, UUID(str(event.payload["actor_id"])), ""
                    )
                    batch = get_batch(ctx, UUID(str(event.payload["entity_id"])), lock=True)
                    if batch.status == "queued":
                        batch.status = "failed"
                        batch.errors = [
                            {
                                "code": "delivery_exhausted",
                                "message": "Delivery exhausted; review and revalidate to retry",
                            }
                        ]
                continue
            event.attempts += 1
            event.available_at = datetime.now(UTC) + timedelta(seconds=60 * event.attempts)
            try:
                enqueue(str(tenant_id), str(event.id))
            except Exception:
                # Never persist or log exception text: broker URLs may contain credentials.
                event.last_error = "broker_unavailable"
            else:
                event.status = "queued"
                event.last_error = None
                count += 1
    return count


def process_event(tenant_id: UUID, event_id: UUID) -> None:
    with Session(get_engine()) as session, session.begin():
        set_context(session, actor_id=UUID(int=0), tenant_id=tenant_id)
        event = session.scalar(
            select(OutboxEvent)
            .where(
                OutboxEvent.tenant_id == tenant_id,
                OutboxEvent.id == event_id,
            )
            .with_for_update()
        )
        if not event or event.status in {"published", "failed"}:
            return
        actor_id = UUID(str(event.payload["actor_id"]))
        membership = session.scalar(
            select(Membership).where(
                Membership.tenant_id == tenant_id,
                Membership.user_id == actor_id,
                Membership.active.is_(True),
            )
        )
        if event.event_type == "import.commit_requested":
            ctx = TenantContext(session, tenant_id, actor_id, membership.role if membership else "")
            batch = get_batch(ctx, UUID(str(event.payload["entity_id"])), lock=True)
            if not membership or Permission.IMPORT not in ROLE_PERMISSIONS[membership.role]:
                batch.status = "failed"
                batch.errors = [
                    {
                        "code": "authorization_revoked",
                        "message": "Commit permission is no longer valid",
                    }
                ]
                event.status = "failed"
                event.last_error = "authorization_revoked"
                return
            set_context(session, actor_id=actor_id, tenant_id=tenant_id)
            commit_batch(ctx, batch)
        elif event.event_type == "intelligence.batch_score_requested":
            job = session.get(ScoringJob, UUID(str(event.payload["entity_id"])))
            if not membership or Permission.SCORE not in ROLE_PERMISSIONS[membership.role]:
                if job:
                    job.status = "failed"
                    job.error_code = "authorization_revoked"
                event.status = "failed"
                event.last_error = "authorization_revoked"
                return
            ctx = TenantContext(session, tenant_id, actor_id, membership.role)
            intelligence_service.execute_batch_score(ctx, UUID(str(event.payload["entity_id"])))
        elif event.event_type == "integration.sync_requested":
            run = session.get(IntegrationSyncRun, UUID(str(event.payload["entity_id"])))
            if (
                not membership
                or Permission.INTEGRATION_WRITE not in ROLE_PERMISSIONS[membership.role]
            ):
                if run:
                    run.status = "failed"
                    run.error_code = "authorization_revoked"
                event.status = "failed"
                event.last_error = "authorization_revoked"
                return
            assert run is not None
            ctx = TenantContext(session, tenant_id, actor_id, membership.role)
            integration = integration_service.get_integration(ctx, run.integration_id)
            integration_service.execute_sync(
                ctx, run.id, provider_for(integration.provider), get_object_store()
            )
        # Non-command events are acknowledged as delivered to the local audit/domain
        # consumer. External integrations must register explicit handlers later.
        event.status = "published"
        event.last_error = None
