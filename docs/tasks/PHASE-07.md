# PHASE-07 — Versioned analytics foundation

Status: COMPLETE — versioned tenant-scoped analytics foundation
Goal: Trustworthy tenant-scoped financial/activity KPIs and RFM inputs.
Context: Orders, item discounts and timestamped returns now exist.
In scope: Versioned PostgreSQL read model, explicit timezone/range semantics,
daily trend, customer purchase summary, catalog rankings and empty-state contracts.
Out of scope: Forecast revenue, causal marketing lift, fabricated ad metrics or ML scores.
Dependencies: Tested canonical commerce and CRM.
Acceptance: Hand-calculated fixtures reconcile; refunds affect their posting dates;
date boundaries respect workspace timezone; undefined ratios are null, not zero.
Validation: Real database tests for period crossing, partial refunds, no data and tenant scope.
Risks: Lifetime-refund leakage into historical periods, money/timezone ambiguity and KPI drift.

Review: The `analytics-v1` read model, daily trend, customer summaries, catalog rankings and
explicit empty-state contracts are implemented. PostgreSQL integration tests reconcile period
boundaries, partial/refund posting behavior, timezone semantics and tenant isolation.
