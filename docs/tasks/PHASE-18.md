# PHASE-18 — Attribution engine

Status: COMPLETE
Goal: Persist reproducible first-party attribution without causal overclaiming.
Context: Platform metrics and orders need an explicit, versioned linking method.
In scope: Protected click/session identifiers, UTM/provider campaign fields, deterministic
customer match, 30-day last-touch selection, idempotent order attribution and evidence.
Out of scope: Probabilistic identity, multi-touch credit and causal incrementality.
Dependencies: Canonical orders/customers and privacy secret boundary.
Acceptance: Future/out-of-window touches cannot win; method/version/evidence are stored.
Validation: API integration test proves deterministic idempotent reuse.
Risks: Missing first-party identifiers and last-touch bias.

Review: `deterministic-last-touch-v1` chooses only the latest same-customer touch at or
before purchase within 30 days. Raw session/click values are never stored; HMAC requires
a dedicated secret. Evidence is labelled `first_party_observed`, never causal.
