"""Grounded generative draft evidence."""

from pathlib import Path

from alembic import op
from sqlalchemy import text

revision = "0011"
down_revision = "0010"


def upgrade() -> None:
    source = Path(__file__).resolve().parents[1] / "sql" / "0011_generation.sql"
    op.execute(text(source.read_text()))


def downgrade() -> None:
    raise RuntimeError("Destructive rollback requires reviewed backup/restore")
