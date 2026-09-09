from fastapi import APIRouter, Depends

from app.generation import service
from app.generation.schemas import DraftRead, DraftRequest
from app.identity.context import TenantContext, permitted
from app.identity.permissions import Permission

router = APIRouter(prefix="/api/v1/assistant", tags=["Assistant"])


@router.post("/drafts", response_model=DraftRead, status_code=201)
def draft(
    payload: DraftRequest,
    ctx: TenantContext = Depends(permitted(Permission.MARKETING_WRITE)),
) -> DraftRead:
    return DraftRead.model_validate(service.generate_draft(ctx, payload))
