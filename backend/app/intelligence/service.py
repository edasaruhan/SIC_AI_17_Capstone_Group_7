"""Demo-gated, tenant-safe feature extraction and frozen-candidate scoring."""

import hashlib
import json
from datetime import UTC, datetime, timedelta
from functools import lru_cache
from pathlib import Path
from typing import Any, Protocol
from uuid import UUID

import joblib  # type: ignore[import-untyped]
import numpy as np
import pandas as pd
from sqlalchemy import select

from app.commerce.models import Order, OrderItem, Refund
from app.crm.models import Customer, MarketingConsent
from app.crm.service import get_customer
from app.identity.context import TenantContext
from app.identity.models import Organization
from app.intelligence.decision import Channel, DecisionEvidence, DecisionInput, decide
from app.intelligence.models import CustomerPrediction, ScoringJob
from app.platform.audit import record_event
from app.platform.config import get_settings
from app.platform.errors import DomainError


class Predictor(Protocol):
    manifest: dict[str, Any]

    def predict(self, features: pd.DataFrame) -> float: ...


class LocalCandidatePredictor:
    def __init__(self, model_path: Path, manifest_path: Path) -> None:
        self.manifest = json.loads(manifest_path.read_text())
        actual = hashlib.sha256(model_path.read_bytes()).hexdigest()
        if actual != self.manifest.get("artifact_sha256"):
            raise RuntimeError("Frozen candidate checksum mismatch")
        self._model = joblib.load(model_path)

    def predict(self, features: pd.DataFrame) -> float:
        return float(self._model.predict_proba(features)[0, 1])


@lru_cache
def get_predictor() -> Predictor:
    settings = get_settings()
    return LocalCandidatePredictor(settings.model_path, settings.model_manifest_path)


def _std(values: list[float]) -> float:
    return float(np.std(values, ddof=1)) if len(values) > 1 else 0.0


def build_operational_features(
    ctx: TenantContext, customer_id: UUID, cutoff: datetime
) -> pd.DataFrame:
    get_customer(ctx, customer_id)
    orders = list(
        ctx.session.scalars(
            select(Order)
            .where(
                Order.tenant_id == ctx.tenant_id,
                Order.customer_id == customer_id,
                Order.placed_at < cutoff,
                Order.total > 0,
            )
            .order_by(Order.placed_at)
        )
    )
    if not orders or orders[-1].placed_at < cutoff - timedelta(days=180):
        raise DomainError("Customer is outside the frozen 180-day scoring eligibility window", 409)
    history = [order for order in orders if order.placed_at >= cutoff - timedelta(days=365)]
    trailing = [order for order in history if order.placed_at >= cutoff - timedelta(days=90)]
    order_ids = [order.id for order in history]
    items = list(
        ctx.session.scalars(
            select(OrderItem).where(
                OrderItem.tenant_id == ctx.tenant_id, OrderItem.order_id.in_(order_ids)
            )
        )
    )
    refunds = list(
        ctx.session.scalars(
            select(Refund).where(
                Refund.tenant_id == ctx.tenant_id,
                Refund.order_id.in_(order_ids),
                Refund.created_at >= cutoff - timedelta(days=365),
                Refund.created_at < cutoff,
            )
        )
    )
    order_values = [float(order.total) for order in history]
    trailing_values = [float(order.total) for order in trailing]
    units_by_order: dict[UUID, int] = {order.id: 0 for order in history}
    products_by_order: dict[UUID, set[UUID]] = {order.id: set() for order in history}
    for item in items:
        units_by_order[item.order_id] += item.quantity
        products_by_order[item.order_id].add(item.product_id)
    dates = [order.placed_at for order in history]
    gaps = [
        (right - left).total_seconds() / 86400
        for left, right in zip(dates, dates[1:], strict=False)
    ]
    spend = sum(order_values)
    return_value = sum(float(refund.amount) for refund in refunds)
    values: dict[str, object] = {
        "purchase_count_365": len(history),
        "spend_365": spend,
        "units_365": sum(units_by_order.values()),
        "avg_order_value_365": float(np.mean(order_values)),
        "max_order_value_365": max(order_values),
        "order_value_std_365": _std(order_values),
        "avg_basket_units_365": float(np.mean(list(units_by_order.values()))),
        "avg_products_per_order_365": float(
            np.mean([len(products) for products in products_by_order.values()])
        ),
        "purchase_count_90": len(trailing),
        "spend_90": sum(trailing_values),
        "units_90": sum(units_by_order[order.id] for order in trailing),
        "unique_products_365": len({item.product_id for item in items}),
        "purchase_count_observed": len(orders),
        "mean_gap_days_365": float(np.mean(gaps)) if gaps else np.nan,
        "std_gap_days_365": _std(gaps) if gaps else np.nan,
        "last_gap_days": gaps[-1] if gaps else np.nan,
        "return_line_count_365": len(refunds),
        "return_value_365": return_value,
        "recency_days": (cutoff - orders[-1].placed_at).total_seconds() / 86400,
        "tenure_days": (cutoff - orders[0].placed_at).total_seconds() / 86400,
        "return_value_share_365": return_value / spend if spend else 0,
        "cutoff_month_sin": np.sin(2 * np.pi * cutoff.month / 12),
        "cutoff_month_cos": np.cos(2 * np.pi * cutoff.month / 12),
        "country": "__missing__",
    }
    return pd.DataFrame([values])


def latest_consent(ctx: TenantContext, customer_id: UUID) -> dict[Channel, bool]:
    rows = ctx.session.scalars(
        select(MarketingConsent)
        .where(
            MarketingConsent.tenant_id == ctx.tenant_id,
            MarketingConsent.customer_id == customer_id,
        )
        .order_by(MarketingConsent.created_at.desc(), MarketingConsent.id.desc())
    )
    result: dict[Channel, bool] = {"email": False, "sms": False, "ads": False}
    observed: set[str] = set()
    for row in rows:
        if row.channel not in observed and row.channel in result:
            result[row.channel] = row.granted
            observed.add(row.channel)
    return result


def score_customer(ctx: TenantContext, customer_id: UUID) -> CustomerPrediction:
    organization = ctx.session.get(Organization, ctx.tenant_id)
    assert organization is not None
    if get_settings().experimental_scoring_demo_only and not organization.is_demo:
        raise DomainError("The external-data candidate is enabled only for demo workspaces", 409)
    now = datetime.now(UTC)
    features = build_operational_features(ctx, customer_id, now)
    predictor = get_predictor()
    probability = predictor.predict(features)
    manifest = predictor.manifest
    threshold = float(manifest["threshold_metrics"]["threshold"])
    evidence = DecisionEvidence(
        target_version=str(manifest["target_version"]),
        feature_version=str(manifest["feature_version"]),
        split_version=str(manifest["split_version"]),
        model_version=str(manifest["mlflow_run_id"]),
        model_sha256=str(manifest["artifact_sha256"]),
        explanation_method="linear_shap_log_odds",
    )
    decision = decide(
        DecisionInput(
            inactivity_probability=probability,
            frozen_threshold=threshold,
            consent=latest_consent(ctx, customer_id),
            evidence=evidence,
            recency_days=float(features.iloc[0]["recency_days"]),
            monetary_365=float(features.iloc[0]["spend_365"]),
        )
    )
    safe_features = {
        key: None if pd.isna(value) else float(value)
        for key, value in features.iloc[0].items()
        if key != "country"
    }
    row = CustomerPrediction(
        tenant_id=ctx.tenant_id,
        customer_id=customer_id,
        actor_id=ctx.actor_id,
        scored_at=now,
        feature_cutoff=now,
        inactivity_probability=probability,
        frozen_threshold=threshold,
        decision_state=decision.state.value,
        eligible_channels=list(decision.eligible_channels),
        reason_codes=list(decision.reason_codes),
        feature_snapshot=safe_features,
        provenance=evidence.model_dump(),
    )
    ctx.session.add(row)
    ctx.session.flush()
    record_event(
        ctx,
        "customer.prediction_created",
        row.id,
        {"customer_id": str(customer_id), "model_sha256": evidence.model_sha256},
    )
    return row


def queue_batch_score(ctx: TenantContext) -> ScoringJob:
    predictor = get_predictor()
    row = ScoringJob(
        tenant_id=ctx.tenant_id,
        requested_by=ctx.actor_id,
        model_sha256=str(predictor.manifest["artifact_sha256"]),
    )
    ctx.session.add(row)
    ctx.session.flush()
    record_event(ctx, "intelligence.batch_score_requested", row.id)
    return row


def execute_batch_score(ctx: TenantContext, job_id: UUID) -> ScoringJob:
    job = ctx.session.scalar(
        select(ScoringJob)
        .where(ScoringJob.tenant_id == ctx.tenant_id, ScoringJob.id == job_id)
        .with_for_update()
    )
    if job is None:
        raise DomainError("Scoring job not found", 404)
    if job.status in {"succeeded", "partial"}:
        return job
    job.status = "running"
    job.started_at = datetime.now(UTC)
    customers = list(
        ctx.session.scalars(
            select(Customer.id).where(
                Customer.tenant_id == ctx.tenant_id, Customer.status == "active"
            )
        )
    )
    job.total_customers = len(customers)
    for customer_id in customers:
        try:
            score_customer(ctx, customer_id)
            job.scored_customers += 1
        except DomainError as error:
            if error.status == 409:
                job.skipped_customers += 1
            else:
                job.failed_customers += 1
        except Exception:
            job.failed_customers += 1
    job.completed_at = datetime.now(UTC)
    job.status = "partial" if job.failed_customers else "succeeded"
    record_event(
        ctx,
        "intelligence.batch_score_completed",
        job.id,
        {
            "scored": job.scored_customers,
            "skipped": job.skipped_customers,
            "failed": job.failed_customers,
        },
    )
    return job
