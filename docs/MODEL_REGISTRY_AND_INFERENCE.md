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

Training used `country` as a varying feature, but `build_operational_features` currently
sets it to `__missing__` for every request because the operational model has no country
field. This is a training-serving skew risk and production-readiness gate, not a minor
fallback. Before production use, provide a reliable operational country field, evaluate a
country-free candidate, or run an all-country-missing sensitivity/holdout test. Do not tune
against the frozen final test.

Each prediction is append-only under forced PostgreSQL RLS and stores score time,
feature cutoff, aggregate feature snapshot, frozen threshold, review state, explicit
consented-channel result and model checksum/version provenance. It emits audit/outbox
evidence. It stores no email, phone or raw transaction lines. The endpoint does not
authorize or send communication. Failed model checksum, absent recent activity and
non-demo use are surfaced instead of silently falling back.

The production lifecycle still requires an external artifact store/registry backup,
signed promotion procedure, drift/performance monitoring with delayed labels,
representative business validation and an approved rollback runbook.

For container builds, the approved binary is supplied out-of-repository as the required
BuildKit secret `growthpilot_model`. `app.platform.model_artifact` streams and verifies its
SHA-256 against the committed manifest before installing it read-only at
`/app/models/final_candidate.joblib`; it does not deserialize the secret during the build.
The application repeats the checksum check before `joblib.load`. This is a tested local
artifact contract, not evidence of a built, scanned, signed or deployed production image.
