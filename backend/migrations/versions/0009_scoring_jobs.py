"""Durable batch scoring workflow state."""

from pathlib import Path

from alembic import op
from sqlalchemy import text

revision = "0009"
down_revision = "0008"


def upgrade() -> None:
    source = Path(__file__).resolve().parents[1] / "sql" / "0009_scoring_jobs.sql"
    op.execute(text(source.read_text()))


def downgrade() -> None:
    raise RuntimeError("Destructive rollback requires reviewed backup/restore")
