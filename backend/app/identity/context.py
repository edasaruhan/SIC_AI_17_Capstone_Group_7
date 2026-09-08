from collections.abc import Callable, Generator
from dataclasses import dataclass
from uuid import UUID

from fastapi import Depends, Header, HTTPException
from sqlalchemy import select, text
from sqlalchemy.orm import Session

from app.identity.auth import Principal, authenticate
from app.identity.models import Membership
from app.identity.permissions import ROLE_PERMISSIONS, Permission
from app.platform.db import get_engine, set_context


@dataclass
class TenantContext:
    session: Session
    tenant_id: UUID
    actor_id: UUID
    role: str

    def require(self, permission: Permission) -> None:
        if permission not in ROLE_PERMISSIONS.get(self.role, frozenset()):
            raise HTTPException(403, "Permission denied")


def tenant_context(
    principal: Principal = Depends(authenticate),
    organization_id: UUID = Header(alias="X-Organization-ID"),
) -> Generator[TenantContext, None, None]:
    with Session(get_engine()) as session, session.begin():
        # Lookup only an identity already authenticated by the issuer adapter. This
        # narrowly scoped function exposes an internal ID, never credentials or PII.
        actor_id = session.execute(
            text("SELECT resolve_actor(:issuer, :subject)"),
            {"issuer": principal.issuer, "subject": principal.subject},
        ).scalar_one_or_none()
        if actor_id is None:
            raise HTTPException(403, "Workspace access unavailable")
        set_context(session, actor_id=actor_id)
        membership = session.scalar(
            select(Membership).where(
                Membership.tenant_id == organization_id,
                Membership.user_id == actor_id,
                Membership.active.is_(True),
            )
        )
        if membership is None:
            raise HTTPException(403, "Workspace access unavailable")
        set_context(session, actor_id=actor_id, tenant_id=membership.tenant_id)
        yield TenantContext(session, membership.tenant_id, actor_id, membership.role)


def permitted(permission: Permission) -> Callable[..., TenantContext]:
    def dependency(
        context: TenantContext = Depends(tenant_context, scope="function"),
    ) -> TenantContext:
        context.require(permission)
        return context

    return dependency
