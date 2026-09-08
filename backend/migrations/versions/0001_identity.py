"""Identity, restricted runtime access, and transaction-local RLS."""

from pathlib import Path

from alembic import op
from sqlalchemy import text

revision = "0001"
down_revision = None


def upgrade() -> None:
    sql = Path(__file__).resolve().parents[1] / "sql" / "0001_identity.sql"
    op.execute(text(sql.read_text()))


def downgrade() -> None:
    raise RuntimeError("Destructive rollback requires a reviewed backup/restore procedure")
