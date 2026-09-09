import logging
import time
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from uuid import uuid4

from fastapi import Depends, FastAPI, Request, Response
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from opentelemetry import trace
from prometheus_client import CONTENT_TYPE_LATEST, Counter, generate_latest
from sqlalchemy import select, text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from starlette.middleware.base import RequestResponseEndpoint

from app.identity.context import TenantContext, permitted
from app.identity.models import Organization
from app.identity.permissions import ROLE_PERMISSIONS, Permission
from app.platform.config import get_settings
from app.platform.db import get_engine, verify_runtime_role
from app.platform.errors import DomainError

requests_total = Counter("growthpilot_http_requests_total", "HTTP requests", ["method", "status"])
logger = logging.getLogger("growthpilot.http")
tracer = trace.get_tracer("growthpilot.api")


@asynccontextmanager
async def lifespan(application: FastAPI) -> AsyncIterator[None]:
    with Session(get_engine()) as session:
        verify_runtime_role(session)
    yield
    get_engine().dispose()


def create_app() -> FastAPI:
    from app.analytics.router import router as analytics_router
    from app.catalog.router import router as catalog_router
    from app.commerce.router import router as commerce_router
    from app.crm.router import router as crm_router
    from app.generation.router import router as generation_router
    from app.imports.router import router as imports_router
    from app.integrations.router import router as integrations_router
    from app.intelligence.router import router as intelligence_router
    from app.marketing.router import router as marketing_router
    from app.platform.audit_router import router as audit_router

    settings = get_settings()
    application = FastAPI(title="GrowthPilot API", version="0.1.0", lifespan=lifespan)
    application.add_middleware(
        CORSMiddleware,
        allow_origins=settings.allowed_origins,
        allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE"],
        allow_headers=[
            "Authorization",
            "Content-Type",
            "X-Organization-ID",
            "X-File-Name",
            "X-Import-Kind",
            "Idempotency-Key",
            "X-Hub-Signature-256",
        ],
    )

    @application.middleware("http")
    async def request_boundary(request: Request, call_next: RequestResponseEndpoint) -> Response:
        request_id = str(uuid4())
        started = time.perf_counter()
        request.state.request_id = request_id
        with tracer.start_as_current_span(
            "http.request", attributes={"http.request.method": request.method}
        ) as span:
            response = await call_next(request)
            span.set_attribute("http.response.status_code", response.status_code)
        response.headers["X-Request-ID"] = request_id
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["Referrer-Policy"] = "no-referrer"
        response.headers["Cache-Control"] = "no-store"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=()"
        response.headers["Content-Security-Policy"] = "default-src 'none'; frame-ancestors 'none'"
        if settings.environment == "production":
            response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        requests_total.labels(request.method, str(response.status_code)).inc()
        logger.info(
            "request",
            extra={
                "request_id": request_id,
                "method": request.method,
                "status": response.status_code,
                "duration_ms": round((time.perf_counter() - started) * 1000),
            },
        )
        return response

    @application.exception_handler(DomainError)
    async def domain_error(request: Request, error: DomainError) -> JSONResponse:
        return JSONResponse({"detail": error.message}, status_code=error.status)

    @application.exception_handler(IntegrityError)
    async def integrity_error(request: Request, error: IntegrityError) -> JSONResponse:
        # Database details can disclose identifiers or another tenant's unique values.
        return JSONResponse({"detail": "Operation conflicts with existing data"}, status_code=409)

    @application.exception_handler(RequestValidationError)
    async def validation_error(request: Request, error: RequestValidationError) -> JSONResponse:
        return JSONResponse(
            {
                "detail": [
                    {"loc": list(item["loc"]), "msg": item["msg"], "type": item["type"]}
                    for item in error.errors()
                ]
            },
            status_code=422,
        )

    @application.get("/health/live")
    def live() -> dict[str, str]:
        return {"status": "ok"}

    @application.get("/health/ready")
    def ready() -> Response:
        try:
            with Session(get_engine()) as session:
                session.execute(text("SELECT 1"))
                verify_runtime_role(session)
        except Exception:
            return JSONResponse({"status": "unavailable"}, status_code=503)
        return JSONResponse({"status": "ready"})

    @application.get("/api/v1/workspace")
    def workspace(ctx: TenantContext = Depends(permitted(Permission.READ))) -> dict[str, object]:
        org = ctx.session.scalar(select(Organization).where(Organization.id == ctx.tenant_id))
        assert org is not None
        return {
            "id": str(org.id),
            "name": org.name,
            "currency": org.currency,
            "timezone": org.timezone,
            "is_demo": org.is_demo,
            "role": ctx.role,
            "permissions": sorted(ROLE_PERMISSIONS[ctx.role]),
        }

    @application.get("/api/v1/metrics", include_in_schema=False)
    def metrics(ctx: TenantContext = Depends(permitted(Permission.AUDIT))) -> Response:
        return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)

    application.include_router(crm_router)
    application.include_router(generation_router)
    application.include_router(catalog_router)
    application.include_router(commerce_router)
    application.include_router(imports_router)
    application.include_router(analytics_router)
    application.include_router(intelligence_router)
    application.include_router(integrations_router)
    application.include_router(marketing_router)
    application.include_router(audit_router)
    return application
