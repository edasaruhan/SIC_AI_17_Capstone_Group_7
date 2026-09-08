# Product Scope

Status: High-level Release 1 scope captured; sequencing and architecture remain subject to Project Lead decisions.

## A. Release 1 product capabilities

Release 1 is one commercially oriented product delivered through internal milestones. Items below are not automatically deferred merely because they are broad.

### Customer operations and CRM

- Customer create/edit, profiles, contact information, search, filtering, tags, and status.
- Purchase and interaction history, activity timeline, notes where appropriate, and marketing permissions.
- Customer 360 views joining operational history with segments, value, risk, and recommendations.

### ERP-lite commerce and inventory

- Sales, orders, order items, dates, quantities, pricing, discounts, and refund/return representation.
- Products, categories, prices, inventory levels, inventory movements, and product-sales relationships.
- Customer-order relationships and auditable sales history.

### Imports and external systems

- CSV and Excel import with mapping, preview, validation, duplicate detection, partial-failure policy, error reporting, provenance, and auditability.
- Provider adapters for external ERP/CRM systems: external schema → connector → validation → normalization → canonical domain.
- Connector behavior designed for idempotency, checkpoints, retries, rate limits, schema drift, provenance, and safe replay where applicable.

### Business analytics and customer intelligence

- Dashboards for revenue, orders, customers, product/inventory performance, retention, churn, customer value, and marketing performance.
- RFM, customer value/CLV methods supported by available data, useful segmentation, and customer prioritization.
- Explainable churn risk, customer-level explanations, commercial importance, and recommended actions.
- Centralized, versioned metric and decision definitions; no scattered frontend thresholds.

### Marketing intelligence and measurement

- Campaign analytics, targeting/prioritization, response and propensity modeling where supported, channel analysis, recommendations, measurement, and sales-marketing linkage.
- Attribution that explicitly distinguishes observed, platform-attributed, deterministically linked, inferred, and unknown outcomes.
- Dynamic, versioned, reproducible, refreshable audiences.
- Algorithmic budget optimization that incorporates constraints, uncertainty, and marginal response rather than a simple ROAS comparison.

### Marketing integrations and orchestration

- Meta Ads and Google Ads authorization/account mapping, campaign and metric ingestion, and permitted campaign/audience/budget operations after current official API capabilities are verified.
- Provider-neutral core marketing concepts so further channels can be added without rewriting the domain.
- Draft → review → approval → execution → audit workflows for meaningful spend or publishing actions.

### Generative AI

- Ad-copy variants, campaign drafts, insight summaries, recommendation explanations, and creative ideation grounded in trusted structured facts.
- No invented customer attributes, model scores, financial results, campaign performance, or unsupported explanations.

### SaaS platform requirements

- Organization/tenant ownership, memberships, tenant-scoped access, server-side RBAC, authentication, audit events, and tenant-owned imports, connectors, predictions, and actions.
- Appropriate batch, scheduled, webhook, event-driven, or request/response freshness per workflow; no blanket real-time infrastructure requirement.
- Security, privacy, data quality, observability, and human oversight as product capabilities.

## B. Current capstone ML focus

The initial supervised learning problem is customer churn classification: identify customers at risk of becoming inactive early enough for a useful marketing intervention.

This work requires dataset research, a written and approved temporal target definition, leakage-safe feature snapshots, business baselines, model-family comparison, untouched holdout evaluation, calibration, top-k/lift analysis, SHAP-based explanation where suitable, and a provenance-aware recommendation layer.

Churn is the first deep capstone ML problem. It is not a substitute for the complete Release 1 product.

## Scope controls

- No provider capability is assumed until current official documentation and permissions are verified.
- RFM is descriptive analysis, not an ML model.
- Observational ROAS does not prove incrementality or causation.
- Dataset limitations must not be filled with fabricated fields.
- Exact architecture, dataset, target, thresholds, and production technology choices remain undecided.
