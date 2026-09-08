-- Versioned analytical projection, evaluated with the caller's base-table RLS.
CREATE VIEW analytics_revenue_v1 WITH (security_invoker=true,security_barrier=true) AS
 SELECT tenant_id, placed_at AS occurred_at, customer_id, id AS order_id,
        'sale'::text AS kind, total AS amount
 FROM orders
 UNION ALL
 SELECT r.tenant_id, r.created_at, o.customer_id, r.order_id,
        'refund'::text, -r.amount
 FROM refunds r JOIN orders o ON (o.tenant_id=r.tenant_id AND o.id=r.order_id);
GRANT SELECT ON analytics_revenue_v1 TO growthpilot_app;
CREATE INDEX ix_refunds_reporting ON refunds(tenant_id,created_at);
