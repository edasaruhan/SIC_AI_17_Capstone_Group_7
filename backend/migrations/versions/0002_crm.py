"""CRM, append-only audit and durable outbox."""

from pathlib import Path

from alembic import op
from sqlalchemy import text

revision = "0002"
down_revision = "0001"


def upgrade() -> None:
    op.execute(text((Path(__file__).resolve().parents[1] / "sql" / "0002_crm.sql").read_text()))


def downgrade() -> None:
    raise RuntimeError("Destructive rollback requires a reviewed backup/restore procedure")
