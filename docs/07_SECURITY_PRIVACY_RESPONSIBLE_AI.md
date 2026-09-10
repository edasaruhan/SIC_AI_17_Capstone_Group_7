# Security, Privacy, and Responsible AI

Status: Local technical controls implemented and tested; production configuration and qualified legal review remain external.

## Security principles

- Default to least privilege, explicit ownership, defense in depth, secure failure, auditable change, and data minimization.
- Enforce authentication, authorization, tenant scope, and resource ownership on the server side.
- Treat cross-tenant access as a critical defect and test isolation at query, API, job, import, connector, artifact, prediction, and audit boundaries.
- Keep production secrets in an approved secret-management boundary; never commit them or place secret values in domain records.
- The AWS reference enforces TLS-facing load balancing and encrypted RDS, Redis, S3 and secrets/KMS resources; no cloud apply or production certification is claimed.

## Authentication and RBAC

The accepted boundary is provider-neutral OIDC/OAuth2/JWT with a deliberately gated
development token adapter. Tenant selection resolves through active membership. Owner,
admin, marketing manager, analyst and operator roles map to centralized capabilities;
high-impact action permissions are enforced server-side. The production IdP, recovery
process and service identities remain deployment configuration items.

Authorization must be centralized, deny by default, tenant-aware, and verified independently of UI visibility. Sensitive operations require stronger permissions and audit evidence.

Local PostgreSQL/API tests verify membership selection, forged/expired/wrong-audience
token rejection, restricted runtime privileges, RLS isolation and pool reuse. These tests
do not replace production IdP validation or an external penetration test.

## Uploads and imports

- Limit allowed formats, size, row count, and decompressed size; detect malformed or deceptive files.
- Store uploads outside executable paths and use generated internal names.
- Validate schema and values in staging before canonical writes.
- Prevent spreadsheet formula injection in previews/exports and unsafe XML/external-link processing.
- Provide preview, duplicate detection, partial-failure policy, row-level errors, provenance, and idempotency.
- Do not silently discard invalid records or expose one tenant's import to another.

## External APIs and webhooks

- Verify current provider documentation, scopes, API versions, rate limits, and policy before real integration.
- Constrain outbound destinations, redirects, protocols, timeouts, response sizes, and DNS/IP behavior to reduce SSRF and exfiltration risk.
- Validate webhook signatures, timestamps/replay windows, provider/account ownership, idempotency, and payload schemas.
- Use bounded retries with backoff and make failures observable; never fabricate success.

## Secrets and logging

Never log passwords, access/refresh tokens, OAuth secrets, authorization headers, private keys, session material, or unnecessary PII. Structured logs should use correlation IDs and safe identifiers with redaction. Access to logs, raw provider payloads, uploads, and ML artifacts must be tenant- and role-scoped.

## Privacy and lifecycle

Design for purpose limitation, data minimization, marketing consent, tenant ownership, correction, export, deletion, retention, and defensible pseudonymization/anonymization. Identity linkage and derived analytics must participate in deletion/retention workflows rather than leaving orphaned profiles.

Final KVKK/GDPR obligations, lawful bases, notices, retention periods, processor/controller roles, and data-transfer requirements need qualified legal review. Controls do not justify an automatic claim of “KVKK compliant” or “GDPR compliant.”

## Responsible ML

- Define churn and eligibility transparently and assess sampling, representation, censoring, leakage, and subgroup performance where lawful and meaningful.
- Preserve dataset, target, feature, model, threshold, prediction, and explanation provenance.
- Explain model association faithfully; do not describe SHAP or observed marketing correlation as causation.
- Keep humans responsible for intervention policy and monitor for harm, drift, and unintended targeting effects.

## Generative AI safeguards

LLMs receive structured, permission-checked context and are not authoritative for customer data, spend, conversions, revenue, predictions, or model explanations. Outputs must be treated as advisory unless an approved workflow permits execution.

Controls must address hallucination, false or prohibited claims, manipulation risk, brand safety, privacy, prohibited targeting, prompt/content injection, unsafe tool use, and provider data handling. Financially or reputationally meaningful actions require human review and exact-action audit records.

## Minimum verification themes

- Authentication/session and server-side authorization tests.
- Cross-tenant positive and negative tests at every data access boundary.
- Import/file parser abuse and formula-injection tests.
- Webhook signature/replay and connector idempotency tests.
- Secret/PII log-redaction checks.
- Approval and audit tests for campaign/budget actions.
- LLM grounding, unsupported-claim, and safe-failure evaluation.
