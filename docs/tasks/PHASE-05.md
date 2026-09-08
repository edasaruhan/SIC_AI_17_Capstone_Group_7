# PHASE-05 — Commerce and inventory

Status: COMPLETE — commerce backend workflows
Goal: Real catalog, orders and inventory ledger with atomic stock and return accounting.
In scope: Categories/products, whole-unit inventory, line discounts, sales, payment
records, partial returns/refunds, customer purchase history, idempotency and audit.
Out of scope: Card processing, tax engine, multi-currency FX, multi-location inventory.
Dependencies: Tested CRM/tenancy and money/currency contracts.
Acceptance: Stock cannot oversell under concurrency; failed orders roll back; retries
do not double-charge stock/payments/refunds; partial returns reconcile; tenant FKs hold.
Validation: PostgreSQL integration tests with concurrent sales and duplicate retries.
Risks: Money rounding, double execution, lock ordering, unauthorized product references.

Review: Real concurrent sales test proves one last unit cannot be sold twice; order,
stock, payment and partial/full refund idempotency and rollback tests pass. Exact
per-unit discounts reconcile through returns. Prices/currency are server-controlled.
Files: catalog/commerce modules, 0003 migration, test_commerce.py.
Limitations: Payments/refunds are accounting records, not card processing or real
bank payouts. No tax/FX/multi-location engine claimed. UI integration is PHASE-15.
Decision required: None. Next: secure staged imports.
