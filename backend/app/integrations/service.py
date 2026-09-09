import hashlib
from datetime import UTC, datetime
from uuid import UUID, uuid4

from sqlalchemy import select

from app.identity.context import TenantContext
from app.integrations.models import AdPerformanceDaily, Integration, IntegrationSyncRun
from app.integrations.providers import AdsProvider, resolve_secret
from app.integrations.schemas import IntegrationCreate
from app.platform.audit import record_event
from app.platform.config import get_settings
from app.platform.errors import DomainError
from app.platform.storage import ObjectStore

PROVIDER_VERSIONS = {"meta_ads": "v25.0", "google_ads": "v25"}


def get_integration(ctx: TenantContext, integration_id: UUID) -> Integration:
    row = ctx.session.scalar(
        select(Integration).where(
            Integration.tenant_id == ctx.tenant_id, Integration.id == integration_id
        )
    )
    if row is None:
        raise DomainError("Integration not found", 404)
    return row


def create_integration(ctx: TenantContext, payload: IntegrationCreate) -> Integration:
    row = Integration(
        tenant_id=ctx.tenant_id,
        created_by=ctx.actor_id,
        api_version=PROVIDER_VERSIONS[payload.provider],
        **payload.model_dump(),
    )
    ctx.session.add(row)
    ctx.session.flush()
    record_event(ctx, "integration.configured", row.id, {"provider": row.provider})
    return row


def queue_sync(ctx: TenantContext, integration_id: UUID) -> IntegrationSyncRun:
    integration = get_integration(ctx, integration_id)
    if integration.status == "disabled":
        raise DomainError("Disabled integration cannot sync", 409)
    row = IntegrationSyncRun(
        tenant_id=ctx.tenant_id,
        integration_id=integration.id,
        requested_by=ctx.actor_id,
        input_cursor=integration.cursor,
    )
    ctx.session.add(row)
    ctx.session.flush()
    record_event(ctx, "integration.sync_requested", row.id, {"integration_id": str(integration.id)})
    return row


def execute_sync(
    ctx: TenantContext, sync_run_id: UUID, adapter: AdsProvider, object_store: ObjectStore
) -> IntegrationSyncRun:
    run = ctx.session.scalar(
        select(IntegrationSyncRun)
        .where(
            IntegrationSyncRun.tenant_id == ctx.tenant_id,
            IntegrationSyncRun.id == sync_run_id,
        )
        .with_for_update()
    )
    if run is None:
        raise DomainError("Integration sync not found", 404)
    if run.status == "succeeded":
        return run
    if run.status not in {"queued", "failed"}:
        raise DomainError("Integration sync is already running", 409)
    integration = get_integration(ctx, run.integration_id)
    run.status = "running"
    run.started_at = datetime.now(UTC)
    integration.status = "syncing"
    ctx.session.flush()
    try:
        page = adapter.fetch(
            integration.external_account_id,
            resolve_secret(integration.secret_ref),
            run.input_cursor,
        )
        if len(page.raw_payload) > get_settings().max_upload_bytes:
            raise DomainError("Provider payload exceeds the configured limit", 413)
        object_id = uuid4()
        object_store.put(ctx.tenant_id, object_id, page.raw_payload)
        for fact in page.facts:
            exists = ctx.session.scalar(
                select(AdPerformanceDaily.id).where(
                    AdPerformanceDaily.tenant_id == ctx.tenant_id,
                    AdPerformanceDaily.integration_id == integration.id,
                    AdPerformanceDaily.metric_date == fact.metric_date,
                    AdPerformanceDaily.external_campaign_id == fact.external_campaign_id,
                )
            )
            if exists is None:
                ctx.session.add(
                    AdPerformanceDaily(
                        tenant_id=ctx.tenant_id,
                        integration_id=integration.id,
                        sync_run_id=run.id,
                        provider=integration.provider,
                        **fact.__dict__,
                    )
                )
        run.raw_object_id = object_id
        run.raw_sha256 = hashlib.sha256(page.raw_payload).hexdigest()
        run.output_cursor = page.cursor
        run.records_received = len(page.facts)
        run.status = "succeeded"
        run.completed_at = datetime.now(UTC)
        integration.status = "healthy"
        integration.cursor = page.cursor
        integration.last_success_at = run.completed_at
        integration.last_error_code = None
        record_event(ctx, "integration.sync_succeeded", run.id, {"records": len(page.facts)})
    except Exception:
        # Provider bodies and exceptions can contain credentials or customer data.
        run.status = "failed"
        run.completed_at = datetime.now(UTC)
        run.error_code = "provider_sync_failed"
        integration.status = "error"
        integration.last_error_code = run.error_code
    return run
