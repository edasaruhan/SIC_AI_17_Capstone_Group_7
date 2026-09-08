"""Catalog, inventory ledger and order/return/payment invariants."""

from pathlib import Path

from alembic import op
from sqlalchemy import text

revision = "0003"
down_revision = "0002"


def upgrade() -> None:
    op.execute(
        text((Path(__file__).resolve().parents[1] / "sql" / "0003_commerce.sql").read_text())
    )


def downgrade() -> None:
    raise RuntimeError("Destructive rollback requires a reviewed backup/restore procedure")
