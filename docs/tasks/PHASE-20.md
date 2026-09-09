# PHASE-20 — Grounded generative marketing assistant

Status: COMPLETE TO CREDENTIAL-FREE BOUNDARY
Goal: Draft reviewable copy using only verified structured operational facts.
Context: An LLM must not invent customer, financial or campaign claims.
In scope: Provider protocol, server-built fact packet, explicit consent, constrained
prompt, unsupported number/outcome rejection, append-only draft evidence and human review.
Out of scope: Live provider call, autonomous send, approval or outcome prediction.
Dependencies: Customer analytics, consent and prediction provenance.
Acceptance: User cannot inject facts; unsupported numbers/promises fail; action is never
authorized; missing provider configuration is explicit.
Validation: Four tests cover prompts, facts, consent, unsupported claims and persistence.
Risks: Language-level claims beyond lexical checks require provider/evaluation hardening.

Review: The endpoint gathers purchase/value/segment/risk facts server-side, omits direct
PII, and requires current channel consent. Stored drafts always require human approval
and set `action_authorized=false`. The provider remains deliberately disabled until a
credentialed adapter is selected and evaluated; this does not block the tested boundary.
