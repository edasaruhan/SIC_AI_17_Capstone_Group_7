"""Versioned, security-invoker analytical read model."""

from pathlib import Path

from alembic import op
from sqlalchemy import text

revision = "0006"
down_revision = "0005"


def upgrade() -> None:
    source = Path(__file__).resolve().parents[1] / "sql" / "0006_analytics.sql"
    op.execute(text(source.read_text()))


def downgrade() -> None:
    raise RuntimeError("Destructive rollback requires reviewed backup/restore")
