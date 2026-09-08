"""Durable outbox delivery lease and safe error metadata."""

from pathlib import Path

from alembic import op
from sqlalchemy import text

revision = "0005"
down_revision = "0004"


def upgrade() -> None:
    source = Path(__file__).resolve().parents[1] / "sql" / "0005_delivery.sql"
    op.execute(text(source.read_text()))


def downgrade() -> None:
    raise RuntimeError("Destructive rollback requires reviewed backup/restore")
