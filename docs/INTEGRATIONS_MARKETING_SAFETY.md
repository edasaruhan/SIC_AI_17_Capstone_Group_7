# Integrations and marketing safety

Provider flow is `provider → private raw object → validation → canonical daily fact`.
Accounts store only environment secret references. Meta `v25.0` and Google Ads `v25`
origins are fixed HTTPS endpoints; redirects are disabled. Synchronization has durable
PostgreSQL state and bounded outbox delivery. Live credentials, app review and account
behavior have not been validated.

Attribution is deterministic 30-day same-customer last touch, versioned and explicitly
noncausal. Audience definitions are validated data, while snapshots freeze membership,
reason codes and consent channels. Consent must be rechecked before eventual send because
a snapshot can age.

Campaign state is explicit: draft → pending approval → approved → queued. Only permitted
humans can approve; queueing also requires the global kill switch off and a configured
budget ceiling. Defaults block execution. Provider mutation is not implemented or
claimed, and no advertising spend was executed.

Generative copy receives server-derived fact packets, not arbitrary user-supplied facts.
Unsupported numbers and outcome guarantees fail closed. Drafts are append-only evidence,
require human approval and never authorize an action.
