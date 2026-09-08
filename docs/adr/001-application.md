# ADR-001: Application boundaries

Status: Accepted
Date: 2026-09-08
Authority: Project Lead decisions conveyed in founder's full local authorization.

## Context

A small team must deliver one commercial product and rigorous capstone evidence.

## Decision

Use the approved monorepo and modular monolith: Python 3.12/FastAPI/Pydantic 2/SQLAlchemy 2/Alembic; Next.js/React/TypeScript/Tailwind/shadcn UI. REST under /api/v1 and generated OpenAPI types. APIs delegate use cases; modules own models, schemas and services.

## Alternatives

Microservices impose avoidable operations; Streamlit is unsuitable as the approved commercial interface; GraphQL has no current requirement.

## Consequences

Keep cross-domain mutations explicit and transactional. Package frontend/backend/ML independently within one repo. Public contracts are versioned.
