# Operations, security and recovery

## Security and privacy

Authentication is OIDC/JWT with a test/dev-only signed-token adapter. Tenant selection
comes from active membership; PostgreSQL forced RLS and composite tenant foreign keys are
critical controls. Production must configure HTTPS OIDC/JWKS, explicit CORS origins,
strong secret-manager values, object encryption and the global marketing kill switch.
Never log tokens, provider bodies, raw identifiers or unnecessary PII. Session/click
identifiers use tenant-operational HMAC protection before storage; rotation requires a
reviewed relinking/retention plan. Data-subject deletion/retention procedures require
legal/product policy approval and are not represented as regulatory certification.

## Backup and restore targets

Reference targets are RPO ≤ 15 minutes for PostgreSQL and RTO ≤ 4 hours for the service;
these are planned requirements, not achieved claims. Production should use encrypted
automated database backups with point-in-time recovery, versioned object storage,
cross-account backup access and tested restore credentials. Quarterly restore exercise:
restore into an isolated account, run migrations/readiness, verify tenant isolation and
artifact checksums, document elapsed time, then destroy the isolated copy under approval.

Local backup evidence is not a production restore test. Before launch, record provider
configuration recovery, secret rotation, ML registry/artifact restoration, Redis-loss
behavior (outbox remains source of truth), incident ownership and rollback commands.

## Observability

Requests carry generated IDs, security headers, safe structured duration/status logs,
Prometheus counters and OpenTelemetry-compatible spans. Readiness checks database role
safety. Audit events are permission/tenant restricted. Production still needs an actual
trace/log/metric backend, alert thresholds, paging ownership and a fault-injection drill.
