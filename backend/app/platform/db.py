from functools import lru_cache
from uuid import UUID

from sqlalchemy import Engine, create_engine, text
from sqlalchemy.orm import DeclarativeBase, Session

from app.platform.config import get_settings


class Base(DeclarativeBase):
    pass


@lru_cache
def get_engine() -> Engine:
    return create_engine(
        get_settings().database_url.get_secret_value(), pool_pre_ping=True, pool_size=10
    )


def set_context(session: Session, *, actor_id: UUID, tenant_id: UUID | None = None) -> None:
    # Transaction-local settings prevent one pooled connection retaining another tenant.
    session.execute(
        text("SELECT set_config('app.actor_id', :actor, true)"), {"actor": str(actor_id)}
    )
    session.execute(
        text("SELECT set_config('app.tenant_id', :tenant, true)"),
        {"tenant": str(tenant_id) if tenant_id else ""},
    )


def verify_runtime_role(session: Session) -> None:
    unsafe = session.execute(
        text("SELECT rolsuper OR rolbypassrls FROM pg_roles WHERE rolname = current_user")
    ).scalar_one()
    owns_tables = session.execute(
        text(
            "SELECT EXISTS (SELECT 1 FROM pg_tables WHERE schemaname='public' "
            "AND tableowner=current_user)"
        )
    ).scalar_one()
    if unsafe or owns_tables:
        raise RuntimeError("Runtime database role must not own tables or bypass RLS")
