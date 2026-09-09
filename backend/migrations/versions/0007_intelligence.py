"""Immutable tenant-scoped model predictions."""

from pathlib import Path

from alembic import op
from sqlalchemy import text

revision = "0007"
down_revision = "0006"


def upgrade() -> None:
    source = Path(__file__).resolve().parents[1] / "sql" / "0007_intelligence.sql"
    op.execute(text(source.read_text()))


def downgrade() -> None:
    raise RuntimeError("Destructive rollback requires reviewed backup/restore")
