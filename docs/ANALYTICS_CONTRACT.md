# KPI contract v1

Evidence: project implementation definitions, not empirical business results.
Read model: `analytics_revenue_v1`; API definitions `kpi-v1` / `rfm-v1`.

| Metric | Definition |
| --- | --- |
| Sales | Sum of discounted order totals at order event time |
| Refunds | Positive sum of returns posted in the selected period |
| Net revenue | Sales minus period refunds; may be negative in a returns-only period |
| Orders / buyers | Placed order count / distinct purchasing customers in period |
| Average order value | Discounted sales / placed orders; null without orders |
| Customer / stock counts | Current state, not historical snapshots; low stock means ≤5 units |
| Customer R/F/M | Days since latest positive-value order, positive-value placed order count, ledger net value through cutoff |
| Cohort active share | Distinct purchasing cohort members in activity month / cohort size |
| Product performance | Sold and returned units and net ledger revenue in period |

Ranges include both supplied calendar dates in the organization's IANA timezone;
internally they are UTC half-open intervals. Max 366 days. Historical views are
event-time restatements, not a reconstruction of what was known before backdated
data arrived. Refunds never retroactively reduce sales-period revenue. RFM frequency
counts purchase events, even if later returned; it is not the trained churn target.
RFM labels (`no_purchase`, `one_time`, `repeat`) are descriptive, not inferred risk.

Cohorts return observed month cells only; absence of a cell is not evidence that
data collection was complete. Partial months remain partial and must be labeled by
the selected range. No causal retention lift or future customer lifetime value is claimed.
Tax, shipping, margin and FX are not modeled; payment records are not bank settlement.
ROAS/spend and churn probability are null until verified data/scoring is available.
Demo organizations report `synthetic_demo` and cannot constitute academic evidence.

The PostgreSQL view uses `security_invoker` and explicit tenant predicates, so the
base-table RLS still applies. See [PostgreSQL 17 CREATE VIEW](https://www.postgresql.org/docs/17/sql-createview.html).
