# Conceptual Domain Model

Status: Candidate bounded domains and relationships only. No physical database schema, API contract, or aggregate design is approved.

## Bounded domains and candidate entities

### Identity and tenancy

Organization, User, Membership, Role, Permission.

Owns tenant identity and access context. Every tenant-owned resource must be unambiguously scoped to an organization.

### CRM

Customer, CustomerIdentity, CustomerContact, CustomerInteraction, CustomerNote, CustomerTag, MarketingConsent.

Owns customer profile and engagement history. Customer 360 is a read experience composed from CRM, commerce, marketing, and intelligence data rather than permission for every domain to mutate Customer directly.

### Commerce

Order, OrderItem, Payment, Refund, Discount.

Owns transaction facts, money/time semantics, customer-order linkage, and refund/cancellation representation.

### Inventory

Product, ProductCategory, InventoryBalance, InventoryMovement.

Owns catalog and stock state. Commerce refers to products using stable canonical identifiers and preserves transaction-time facts where required.

### Marketing

AdProvider, AdAccount, Campaign, AdGroup/AdSet abstraction, AdCreative, MarketingMetric, SpendMetric, Conversion, Touchpoint, Audience, AudienceMembership.

Owns provider-neutral campaign concepts and measurement records. Provider-only fields remain at integration boundaries unless promoted deliberately.

### Integration

Integration, CredentialReference, SyncRun, SyncCheckpoint, ImportJob, ImportMapping, ImportError, RawProviderRecord.

Owns provider/account connection, ingestion provenance, validation status, retries, checkpoints, and raw-to-canonical lineage. Secret values are not domain payloads.

### Analytics

MetricDefinition, MetricSnapshot, Segment, RfmSnapshot, CustomerValueSnapshot, AttributionRecord.

Owns centralized definitions and reproducible derived analytical results. Attribution records carry evidence class and method/version.

### ML

DatasetVersion, TargetDefinitionVersion, FeatureDefinition, CustomerFeatureSnapshot, ExperimentRun, ModelVersion, Prediction, Explanation.

Owns temporal feature/prediction provenance. Candidate entities do not imply a chosen tracking platform or serving design.

### Decision and action

Recommendation, RecommendationReason, DecisionRuleVersion, Decision, Approval, Action, ActionResult.

Combines trusted analytics/ML outputs with business constraints. It records why a recommendation was made, who approved it, what executed, and the measured result.

### Audit

AuditEvent.

Captures security- and business-relevant changes with tenant, actor, action, target, time, and safe metadata. Audit records must not expose secrets or unnecessary PII.

## Cross-domain relationships

- Organization is the isolation root for CRM, commerce, inventory, marketing, integration, analytics, ML, decision/action, and audit resources.
- CRM Customer links to Commerce orders and Marketing identities/touchpoints only through explicit canonical identifiers and identity-resolution evidence.
- Order/Conversion/Touchpoint relationships express the attribution evidence class; they do not imply causality.
- Product and category facts support order items, segment features, recommendations, and campaign targeting without moving inventory ownership into analytics.
- Integration normalizes provider payloads into the owning canonical domain and retains lineage to provider, sync/import run, and source identifier.
- Analytics and ML consume time-bounded facts; generated snapshots, predictions, and explanations reference definition/model versions and cutoffs.
- Decision/action consumes predictions and analytics but preserves their source provenance and its own rule/approval/execution lineage.
- Audit observes significant changes across domains without becoming the mutable source of business state.

## Unresolved modeling questions

- Organization hierarchy, legal tenant boundary, and whether sub-organizations are needed.
- User identity, membership lifecycle, invitation flow, and final RBAC permission model.
- Customer identity resolution, household/company contacts, merge/split behavior, and deletion semantics.
- Consent purpose/channel/jurisdiction model and evidence/withdrawal requirements.
- Money, currency, tax, time zone, and transaction-time price semantics.
- Refund, cancellation, partial fulfillment, inventory reservation, and negative-stock policies.
- Product variants, multi-location inventory, units of measure, and category hierarchy.
- Provider-neutral Campaign/AdGroup/AdSet abstraction boundaries and preservation of provider-specific details.
- Touchpoint identity confidence and deterministic versus inferred attribution representation.
- Raw payload retention, encryption, replay, and schema-evolution policy.
- Metric snapshot grain and operational-versus-analytical storage boundaries.
- Feature snapshot entity/time semantics and training-serving consistency.
- Model/recommendation approval lifecycle, supersession, expiration, and action idempotency.
- Audit retention, tamper evidence, PII minimization, and export/deletion interactions.
