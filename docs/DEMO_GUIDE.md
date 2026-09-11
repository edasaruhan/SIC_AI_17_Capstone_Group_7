# GrowthPilot demo guide

Status: Local demonstration runbook. Do not represent demo fixtures as academic or business outcomes.

## Demonstration objective

Show one traceable path from tenant-scoped operating records to an explainable, consent-aware
decision while preserving the difference between a model score and an authorized action.

## Preparation

1. Follow `LOCAL_DEVELOPMENT.md`; migrate both development and dedicated test databases.
2. Start the loopback Redis instance, API, outbox dispatcher/worker and Next.js server.
3. Use only an explicitly demo-marked organization and a separately provisioned development
   token. `local_setup.py` creates infrastructure and local secrets; it does not seed demo users,
   organizations or browser-facing credentials.
4. Confirm `/health/live`, `/health/ready` and the web overview load. Do not expose `.env`.

## Demonstration flow

1. **Organization and permissions:** show the resolved organization, role and server-provided
   capabilities. Explain that request fields cannot select an arbitrary tenant.
2. **Import:** upload a small safe CSV/XLSX fixture; preview validation, commit the staged import,
   and show rejected-row/error provenance. Label the records as demo data.
3. **Customer 360:** open a customer to show canonical orders, RFM/value context, consent and
   history. Avoid implying that demo values are real company results.
4. **Analytics:** show that revenue/order/customer metrics come from one versioned service and that
   unavailable advertising facts remain null/empty rather than invented.
5. **Intelligence:** score an eligible demo customer only with demo-gated on-demand scoring or run a
   durable batch job. Show model/feature/target versions, checksum and the noncausal explanation.
6. **Audience and campaign:** create a validated audience definition, freeze an immutable snapshot,
   draft a campaign and request approval. Show current-consent and permission checks.
7. **Safety stop:** attempt to queue execution. The default kill switch and zero budget ceiling must
   block it. Do not change these controls or contact a live provider for the demo.
8. **Audit:** show the append-only record of import, score, snapshot and approval-related events.

## Academic evidence segment

Present `academic/presentation/GrowthPilot_AI_Final_Presentation.pptx`. The key result is the
single untouched temporal holdout: PR-AUC 0.647525, ROC-AUC 0.765878, Brier 0.199854 and top-10%
lift 1.904513. State the 90-day inactivity-proxy definition, single-retailer limitation,
bootstrap intervals and prohibition on post-test retuning.

## Failure paths worth showing

- Missing server configuration produces an explicit frontend unconfigured state.
- Unauthorized role/action returns a denial from the API, independent of UI visibility.
- Malformed import or invalid formula-like content is rejected without partial canonical writes.
- Missing provider/LLM credentials produce a disabled/unvalidated result, not simulated success.

## End state

Close by distinguishing local implementation evidence from remaining production evidence:
credentialed provider tests, browser/accessibility/load testing, managed restore rehearsal,
security review and a randomized campaign-impact pilot. No push or deployment occurs in this demo.
