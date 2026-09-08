# ADR-003: Durable data and asynchronous processing

Status: Accepted
Date: 2026-09-08
Authority: Project Lead decisions conveyed in founder's full local authorization.

## Context

Imports and provider sync can fail or retry and require provenance.

## Decision

PostgreSQL owns workflow/outbox state; Dramatiq/Redis transports work. Idempotent handlers use bounded retries and persisted errors/checkpoints. S3-compatible object interface supports local filesystem. CSV/XLSX validation precedes preview/staging/commit. Raw-source, canonical, analytics and feature zones remain distinct.

## Alternatives

Redis-only state risks lost business work; Kafka and event sourcing are unnecessary; a warehouse is not justified by measurements.

## Consequences

Outbox provides at-least-once delivery, never claims exactly once. Consumers deduplicate. No source secrets or PII in diagnostics. Parsing enforces size/zip/XML/formula constraints.
