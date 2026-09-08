from uuid import UUID

from sqlalchemy import String, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.platform.db import Base
from app.platform.records import TenantRecord


class ImportBatch(TenantRecord, Base):
    __tablename__ = "import_batches"
    actor_id: Mapped[UUID]
    kind: Mapped[str] = mapped_column(String(24))
    filename: Mapped[str] = mapped_column(String(200))
    checksum: Mapped[str] = mapped_column(String(64))
    object_id: Mapped[UUID]
    idempotency_key: Mapped[str] = mapped_column(String(150))
    status: Mapped[str] = mapped_column(String(24), default="uploaded")
    headers: Mapped[list[str]] = mapped_column(JSONB)
    source_rows: Mapped[list[dict[str, str]]] = mapped_column(JSONB)
    mapping: Mapped[dict[str, str]] = mapped_column(JSONB, default=dict)
    normalized_rows: Mapped[list[dict[str, object]]] = mapped_column(JSONB, default=list)
    errors: Mapped[list[dict[str, object]]] = mapped_column(JSONB, default=list)
    committed_count: Mapped[int] = mapped_column(default=0)
    attempts: Mapped[int] = mapped_column(default=0)
    transform_version: Mapped[str] = mapped_column(String(32), default="canonical-import-v1")
    __table_args__ = (
        UniqueConstraint("tenant_id", "id"),
        UniqueConstraint("tenant_id", "idempotency_key"),
    )
