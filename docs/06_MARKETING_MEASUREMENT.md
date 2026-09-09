# Marketing Measurement

Status: Measurement principles and definition register. Final KPI formulas, time windows, exclusions, currencies, and attribution bases require Project Lead approval.

## Canonical-definition rule

Each metric will have one versioned definition with owner, numerator, denominator, eligible population, event-time rule, reporting window, timezone, currency/FX treatment, attribution basis, refund/cancellation treatment, exclusions, data sources, freshness, and known limitations. Frontend code and reports must consume the canonical definition rather than redefine it.

## Evidence taxonomy

Every marketing/conversion claim must identify one of these evidence classes:

1. **Observed fact** — a directly recorded event or amount from a defined system of record.
2. **Platform-attributed** — an outcome reported by an advertising platform under that provider's attribution rules and window.
3. **GrowthPilot deterministically linked** — a linkage supported by explicit identifiers/rules (for example, a valid click identifier tied to an order) under a versioned rule.
4. **GrowthPilot probabilistically inferred** — an estimate with a documented method, uncertainty, and limitations.
5. **Unknown/unattributed** — no defensible linkage.

Platform-attributed and GrowthPilot-linked figures must not be silently merged or presented as causal incrementality.

## KPI definition register

| KPI | Concept to finalize | Required decision fields | Status |
|---|---|---|---|
| Spend | Eligible media cost in a period | Currency/FX, tax and fee treatment, service date versus billing date, provider/account scope | Definition pending |
| Impressions | Provider-recorded eligible ad | Provider scope, deduplication, invalid-traffic handling | Definition pending |
| Clicks / CTR | Eligible clicks divided by eligible impressions | Click type, invalid clicks, period alignment | Definition pending |
| Conversions / conversion rate | Qualifying conversion count divided by an approved opportunity base | Conversion event, denominator, window, deduplication, attribution class | Definition pending |
| Revenue | Recognized order revenue | Gross/net basis, discounts, refunds, tax/shipping treatment, currency, order status | Definition pending |
| Attributed revenue | Revenue linked under a named/versioned attribution method | Evidence class, method, window, exclusions, overlap handling | Definition pending |
| CAC | Eligible acquisition cost divided by newly acquired customers | Cost scope, new-customer rule, cohort/window, attribution basis | Definition pending |
| ROAS | Attributed revenue divided by eligible ad spend | Attribution basis, revenue basis, time alignment, zero-spend behavior | Definition pending |
| Customer value / LTV | Historical or expected customer economic value | Horizon, revenue versus contribution, discounting, censoring, model/method | Definition pending |
| LTV:CAC | Compatible LTV divided by compatible CAC | Cohort, horizon, cost/revenue basis, zero/undefined handling | Definition pending |
| Churn proxy | No eligible purchase in the frozen 90-day future window (`future-inactivity-v1`) | Strict pre-cutoff features, fully observed outcome, temporal split and eligibility rules | Implemented for capstone; not contractual churn |
| Retention | Eligible customers retained under an approved cohort rule | Cohort start, retained event, horizon, reactivation handling | Definition pending |
| Repeat purchase | Customers with qualifying subsequent purchase | Cohort, order validity, time horizon | Definition pending |
| Campaign response | Qualifying customer response to a campaign | Response event, exposure rule, time window, evidence class | Definition pending |

## Attribution data flow

Ad spend → provider campaign/ad group/creative → touchpoint/click/session/provider attribution → customer identity when defensible → conversion → order → revenue.

Required controls include versioned methods, immutable source facts where appropriate, lineage to raw provider records, identity/linkage confidence, replayable derivation, and visible unknown/unattributed amounts. Attribution windows and model changes must not rewrite history without versioning.

## Customer and campaign decisions

Customer prioritization may combine risk, value, RFM, response propensity, lifecycle, category affinity, and business constraints. Definitions and thresholds are versioned; model scores alone do not authorize action.

Dynamic audiences must be reproducible from a versioned definition and data cutoff, with refresh history, membership provenance, marketing-consent checks, and provider-policy compliance.

## Budget optimization

Budget allocation is a constrained optimization problem, not “move money to the channel with higher observed ROAS.” A defensible method may consider marginal response, saturation, uncertainty, customer value, propensity, minimum/maximum spend, campaign/channel constraints, business objective, and risk controls. Exact objective and method remain undecided.

Observational performance can support decisions but does not prove causal incrementality. Causal claims require an appropriate experimental or causal-identification design.

## Human oversight

Recommendations and drafts may be generated automatically. Meaningful spend, publishing, audience activation, or budget changes follow draft → review → approval → execution → audit, with approver identity, exact payload, provider result, and rollback/stop controls where feasible.
