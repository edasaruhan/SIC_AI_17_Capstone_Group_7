from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy import select

from app.crm.service import get_customer
from app.identity.context import TenantContext, permitted
from app.identity.permissions import Permission
from app.intelligence import service
from app.intelligence.models import CustomerPrediction, ScoringJob
from app.intelligence.schemas import PredictionRead, ScoringJobRead
from app.platform.errors import DomainError

router = APIRouter(prefix="/api/v1/intelligence", tags=["Intelligence"])


def response(row: CustomerPrediction) -> PredictionRead:
    return PredictionRead.model_validate(
        {
            **row.__dict__,
            "human_approval_required": row.decision_state != "monitor",
            "action_authorized": False,
        }
    )


@router.post("/customers/{customer_id}/score", response_model=PredictionRead, status_code=201)
def score(
    customer_id: UUID, ctx: TenantContext = Depends(permitted(Permission.SCORE))
) -> PredictionRead:
    return response(service.score_customer(ctx, customer_id))


@router.get("/customers/{customer_id}/predictions", response_model=list[PredictionRead])
def predictions(
    customer_id: UUID, ctx: TenantContext = Depends(permitted(Permission.READ))
) -> list[PredictionRead]:
    get_customer(ctx, customer_id)
    rows = ctx.session.scalars(
        select(CustomerPrediction)
        .where(
            CustomerPrediction.tenant_id == ctx.tenant_id,
            CustomerPrediction.customer_id == customer_id,
        )
        .order_by(CustomerPrediction.scored_at.desc())
        .limit(100)
    )
    return [response(row) for row in rows]


@router.post("/batch-scores", response_model=ScoringJobRead, status_code=202)
def batch_score(
    ctx: TenantContext = Depends(permitted(Permission.SCORE)),
) -> ScoringJobRead:
    return ScoringJobRead.model_validate(service.queue_batch_score(ctx))


@router.get("/batch-scores/{job_id}", response_model=ScoringJobRead)
def batch_score_status(
    job_id: UUID, ctx: TenantContext = Depends(permitted(Permission.READ))
) -> ScoringJobRead:
    row = ctx.session.scalar(
        select(ScoringJob).where(ScoringJob.tenant_id == ctx.tenant_id, ScoringJob.id == job_id)
    )
    if row is None:
        raise DomainError("Scoring job not found", 404)
    return ScoringJobRead.model_validate(row)
