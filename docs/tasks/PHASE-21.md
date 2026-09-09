# PHASE-21 — Security, privacy and observability hardening

Status: COMPLETE FOR LOCAL REFERENCE BUILD
Goal: Harden trust boundaries and expose useful operational evidence.
Context: Marketing, ML and integrations increase impact and data sensitivity.
In scope: Secure headers, OTel-compatible spans, metrics, audit API, webhook HMAC,
privacy-safe rate keys, fixed provider origins, no redirects, recovery/privacy runbooks.
Out of scope: External SIEM/APM connection, penetration-test certification or legal claim.
Dependencies: All application domains.
Acceptance: Tenant/RBAC controls remain server-side; secrets/PII stay out of logs/keys;
health/audit/metrics boundaries and recovery requirements are documented.
Validation: Security boundary tests, full tenant suite, dependency/secret scans.
Risks: External deployment configuration and incident process remain to be exercised.
