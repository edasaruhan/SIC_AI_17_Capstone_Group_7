# PHASE-19 — Audiences and guarded campaign orchestration

Status: COMPLETE — provider execution disabled
Goal: Build consent-aware audiences and approval-controlled action state.
Context: Predictions cannot directly trigger outreach or spend.
In scope: Validated/versioned rules, immutable membership snapshots, latest consent,
campaign state transitions, idempotent actions, approval, budget ceiling and kill switch.
Out of scope: Live provider mutation or advertising spend.
Dependencies: CRM consent, intelligence, integration hub and audit/outbox.
Acceptance: No channel without explicit consent; no queue before approval; default kill
switch blocks all execution; actions are tenant-scoped and auditable.
Validation: Audience consent and complete draft→approval→blocked-queue tests.
Risks: Stale consent after snapshot and provider-side state divergence.

Review: Audience membership stores rule-version reasons and consent channels at snapshot
time. Campaigns start in draft, transition only through the allowlist, require the
`actions:approve` capability and remain blocked by the default kill switch/zero budget
ceiling. No live spend occurred.
