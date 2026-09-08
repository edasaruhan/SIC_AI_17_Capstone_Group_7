import hashlib
from uuid import UUID, uuid4

from pydantic import ValidationError
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from app.catalog.models import Product
from app.catalog.schemas import ProductCreate
from app.catalog.service import save_product
from app.crm.models import Customer
from app.crm.schemas import CustomerCreate
from app.crm.service import save_customer
from app.identity.context import TenantContext
from app.identity.models import Organization
from app.imports.models import ImportBatch
from app.imports.parser import inspect_file
from app.platform.audit import record_event
from app.platform.config import get_settings
from app.platform.errors import DomainError
from app.platform.idempotency import serialize_key
from app.platform.storage import get_object_store

FIELDS = {
    "customers": {"name", "email", "phone", "external_id", "status"},
    "products": {"name", "sku", "unit_price", "currency"},
}
REQUIRED = {"customers": {"name", "external_id"}, "products": {"name", "sku", "unit_price"}}


def get_batch(ctx: TenantContext, batch_id: UUID, *, lock: bool = False) -> ImportBatch:
    query = select(ImportBatch).where(
        ImportBatch.tenant_id == ctx.tenant_id, ImportBatch.id == batch_id
    )
    if lock:
        query = query.with_for_update()
    batch = ctx.session.scalar(query)
    if not batch:
        raise DomainError("Import not found", 404)
    return batch


def upload(ctx: TenantContext, filename: str, kind: str, key: str, content: bytes) -> ImportBatch:
    checksum = hashlib.sha256(content).hexdigest()
    serialize_key(ctx.session, str(ctx.tenant_id), f"import:{key}")
    prior = ctx.session.scalar(
        select(ImportBatch).where(
            ImportBatch.tenant_id == ctx.tenant_id, ImportBatch.idempotency_key == key
        )
    )
    if prior:
        if (prior.checksum, prior.kind, prior.filename) != (checksum, kind, filename):
            raise DomainError("Idempotency key already used for another upload", 409)
        return prior
    table = inspect_file(filename, content, get_settings().max_upload_bytes)
    object_id = uuid4()
    # An interrupted DB transaction may leave an unreferenced private object; it
    # cannot corrupt canonical data. Retention reconciliation handles such orphans.
    get_object_store().put(ctx.tenant_id, object_id, content)
    batch = ImportBatch(
        tenant_id=ctx.tenant_id,
        actor_id=ctx.actor_id,
        filename=filename,
        kind=kind,
        checksum=checksum,
        object_id=object_id,
        idempotency_key=key,
        headers=table.headers,
        source_rows=table.rows,
    )
    ctx.session.add(batch)
    ctx.session.flush()
    record_event(ctx, "import.uploaded", batch.id, {"checksum": checksum, "rows": len(table.rows)})
    return batch


def validate_mapping(
    ctx: TenantContext, batch: ImportBatch, mapping: dict[str, str]
) -> ImportBatch:
    if batch.status in {"queued", "succeeded"}:
        raise DomainError("A queued or completed import cannot be remapped", 409)
    if not REQUIRED[batch.kind].issubset(mapping) or not set(mapping).issubset(FIELDS[batch.kind]):
        raise DomainError("Map required fields and use only supported canonical fields")
    if not set(mapping.values()).issubset(batch.headers) or len(set(mapping.values())) != len(
        mapping
    ):
        raise DomainError("Each mapped source header must exist and may only be used once")
    organization = ctx.session.get(Organization, ctx.tenant_id)
    assert organization
    batch.mapping = mapping
    normalized: list[dict[str, object]] = []
    errors: list[dict[str, object]] = []
    seen: set[str] = set()
    value: CustomerCreate | ProductCreate
    for number, row in enumerate(batch.source_rows, start=2):
        mapped = {
            field: row[header].strip() for field, header in mapping.items() if row[header].strip()
        }
        try:
            if batch.kind == "customers":
                value = CustomerCreate.model_validate(mapped)
                identity = value.external_id
                if not identity:
                    raise DomainError(
                        "external_id is required for deterministic duplicate detection"
                    )
                exists = ctx.session.scalar(
                    select(Customer.id).where(
                        Customer.tenant_id == ctx.tenant_id, Customer.external_id == identity
                    )
                )
            else:
                mapped.setdefault("currency", organization.currency)
                product = ProductCreate.model_validate(mapped)
                if product.currency != organization.currency:
                    raise DomainError("Product currency must match workspace currency")
                value = product
                identity = product.sku
                exists = ctx.session.scalar(
                    select(Product.id).where(
                        Product.tenant_id == ctx.tenant_id, Product.sku == identity
                    )
                )
            if identity in seen or exists:
                raise DomainError(
                    "Duplicate source identifier; imports do not overwrite existing records"
                )
            seen.add(identity)
            normalized.append(value.model_dump(mode="json"))
        except ValidationError as exc:
            errors.append(
                {
                    "row": number,
                    "code": "invalid_row",
                    "fields": [
                        ".".join(str(part) for part in error["loc"]) for error in exc.errors()
                    ],
                }
            )
        except DomainError as exc:
            errors.append({"row": number, "code": "invalid_row", "message": exc.message})
    batch.errors = errors
    batch.normalized_rows = normalized if not errors else []
    batch.status = "invalid" if errors else "validated"
    record_event(ctx, "import.validated", batch.id, {"error_count": len(errors)})
    ctx.session.flush()
    return batch


def queue_commit(ctx: TenantContext, batch: ImportBatch) -> ImportBatch:
    if batch.status in {"queued", "succeeded"}:
        return batch
    if batch.status != "validated":
        raise DomainError("Validate all rows before committing", 409)
    batch.status = "queued"
    # Attribution records the reviewer initiating commit, not a stale upload identity.
    batch.actor_id = ctx.actor_id
    record_event(ctx, "import.commit_requested", batch.id)
    ctx.session.flush()
    return batch


def commit_batch(ctx: TenantContext, batch: ImportBatch) -> None:
    if batch.status == "succeeded":
        return
    if batch.status != "queued":
        raise DomainError("Import is not queued", 409)
    batch.attempts += 1
    try:
        # All canonical records/events are in one savepoint. A row conflict after
        # preview rolls back every canonical write while persisting the failure.
        with ctx.session.begin_nested():
            for row in batch.normalized_rows:
                if batch.kind == "customers":
                    save_customer(ctx, CustomerCreate.model_validate(row))
                else:
                    save_product(ctx, ProductCreate.model_validate(row))
            ctx.session.flush()
    except (IntegrityError, DomainError):
        batch.status = "failed"
        batch.errors = [
            {
                "code": "commit_conflict",
                "message": "Data changed since preview; remap and revalidate. No rows committed.",
            }
        ]
        record_event(ctx, "import.failed", batch.id)
        return
    batch.status = "succeeded"
    batch.committed_count = len(batch.normalized_rows)
    record_event(ctx, "import.succeeded", batch.id, {"rows": batch.committed_count})
