# Model registry and inference boundary

The checksum-verified frozen candidate is registered in the local MLflow SQLite
registry as `growthpilot-churn-inactivity`, with the `champion` alias, immutable run
lineage and target/feature/split tags. The registry is local evidence, not a deployed
managed service. Only trusted project artifacts may be deserialized.

Operational inference recreates the frozen `customer-behavior-v1` aggregates from
tenant-scoped canonical orders, items and refunds at an explicit cutoff. Customers
must have an eligible purchase in the preceding 180 days. The model was developed on
one external UK retailer and has not been validated on a GrowthPilot SME population;
therefore scoring is hard-gated to demo organizations by default. Removing that gate
requires representative domain validation and Project Lead approval.

Each prediction is append-only under forced PostgreSQL RLS and stores score time,
feature cutoff, aggregate feature snapshot, frozen threshold, review state, explicit
consented-channel result and model checksum/version provenance. It emits audit/outbox
evidence. It stores no email, phone or raw transaction lines. The endpoint does not
authorize or send communication. Failed model checksum, absent recent activity and
non-demo use are surfaced instead of silently falling back.

The production lifecycle still requires an external artifact store/registry backup,
signed promotion procedure, drift/performance monitoring with delayed labels,
representative business validation and an approved rollback runbook.
