"""Private import staging and durable workflow state."""

from pathlib import Path

from alembic import op
from sqlalchemy import text

revision = "0004"
down_revision = "0003"


def upgrade() -> None:
    source = Path(__file__).resolve().parents[1] / "sql" / "0004_imports.sql"
    op.execute(text(source.read_text()))


def downgrade() -> None:
    raise RuntimeError("Destructive rollback requires reviewed backup/restore")
