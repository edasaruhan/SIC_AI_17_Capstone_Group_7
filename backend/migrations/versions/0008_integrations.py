"""Integration accounts, durable syncs, and canonical ad facts."""

from pathlib import Path

from alembic import op
from sqlalchemy import text

revision = "0008"
down_revision = "0007"


def upgrade() -> None:
    source = Path(__file__).resolve().parents[1] / "sql" / "0008_integrations.sql"
    op.execute(text(source.read_text()))


def downgrade() -> None:
    raise RuntimeError("Destructive rollback requires reviewed backup/restore")
