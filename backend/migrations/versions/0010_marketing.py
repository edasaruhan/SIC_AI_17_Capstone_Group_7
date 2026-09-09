"""Attribution, audiences, and approval-controlled campaigns."""

from pathlib import Path

from alembic import op
from sqlalchemy import text

revision = "0010"
down_revision = "0009"


def upgrade() -> None:
    source = Path(__file__).resolve().parents[1] / "sql" / "0010_marketing.sql"
    op.execute(text(source.read_text()))


def downgrade() -> None:
    raise RuntimeError("Destructive rollback requires reviewed backup/restore")
