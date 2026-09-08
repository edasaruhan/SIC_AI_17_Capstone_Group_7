from typing import Literal
from uuid import UUID

from fastapi import APIRouter, Depends, Header, Query, Request, Response
from sqlalchemy import select
from starlette.concurrency import run_in_threadpool

from app.identity.context import TenantContext, permitted
from app.identity.permissions import Permission
from app.imports.models import ImportBatch
from app.imports.schemas import BatchRead, MappingRequest
from app.imports.service import get_batch, queue_commit, upload, validate_mapping
from app.platform.config import get_settings
from app.platform.csv_export import safe_csv
from app.platform.errors import DomainError

router = APIRouter(prefix="/api/v1/imports", tags=["imports"])


@router.get("/{batch_id}/errors.csv")
def error_report(
    batch_id: UUID, ctx: TenantContext = Depends(permitted(Permission.IMPORT))
) -> Response:
    batch = get_batch(ctx, batch_id)
    rows: list[list[object]] = [["row", "code", "message", "fields"]]
    rows.extend(
        [
            [error.get("row"), error.get("code"), error.get("message"), error.get("fields")]
            for error in batch.errors
        ]
    )
    return Response(
        safe_csv(rows),
        media_type="text/csv",
        headers={"Content-Disposition": 'attachment; filename="import-errors.csv"'},
    )


@router.get("", response_model=list[BatchRead])
def batches(
    ctx: TenantContext = Depends(permitted(Permission.IMPORT)),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
) -> list[ImportBatch]:
    return list(
        ctx.session.scalars(
            select(ImportBatch)
            .where(ImportBatch.tenant_id == ctx.tenant_id)
            .order_by(ImportBatch.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
    )


@router.post("", response_model=BatchRead, status_code=201)
async def upload_file(
    request: Request,
    filename: str = Header(alias="X-File-Name", max_length=200),
    kind: Literal["customers", "products"] = Header(alias="X-Import-Kind"),
    key: str = Header(alias="Idempotency-Key", min_length=1, max_length=150),
    ctx: TenantContext = Depends(permitted(Permission.IMPORT)),
) -> ImportBatch:
    content = bytearray()
    async for chunk in request.stream():
        if len(content) + len(chunk) > get_settings().max_upload_bytes:
            raise DomainError("File exceeds upload size limit", 413)
        content.extend(chunk)
    return await run_in_threadpool(upload, ctx, filename, kind, key, bytes(content))


@router.get("/{batch_id}", response_model=BatchRead)
def detail(
    batch_id: UUID, ctx: TenantContext = Depends(permitted(Permission.IMPORT))
) -> ImportBatch:
    return get_batch(ctx, batch_id)


@router.get("/{batch_id}/preview")
def preview(
    batch_id: UUID, ctx: TenantContext = Depends(permitted(Permission.IMPORT))
) -> dict[str, object]:
    batch = get_batch(ctx, batch_id)
    return {
        "headers": batch.headers,
        "source": batch.source_rows[:20],
        "normalized": batch.normalized_rows[:20],
        "total_rows": len(batch.source_rows),
    }


@router.put("/{batch_id}/mapping", response_model=BatchRead)
def mapping(
    batch_id: UUID,
    payload: MappingRequest,
    ctx: TenantContext = Depends(permitted(Permission.IMPORT)),
) -> ImportBatch:
    return validate_mapping(ctx, get_batch(ctx, batch_id, lock=True), payload.fields)


@router.post("/{batch_id}/commit", response_model=BatchRead, status_code=202)
def commit(
    batch_id: UUID, ctx: TenantContext = Depends(permitted(Permission.IMPORT))
) -> ImportBatch:
    return queue_commit(ctx, get_batch(ctx, batch_id, lock=True))
