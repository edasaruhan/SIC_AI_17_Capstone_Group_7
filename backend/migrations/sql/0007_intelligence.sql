CREATE TABLE customer_predictions (
 id uuid PRIMARY KEY,
 tenant_id uuid NOT NULL REFERENCES organizations(id),
 created_at timestamptz NOT NULL DEFAULT now(),
 customer_id uuid NOT NULL,
 actor_id uuid NOT NULL REFERENCES users(id),
 scored_at timestamptz NOT NULL,
 feature_cutoff timestamptz NOT NULL,
 inactivity_probability double precision NOT NULL,
 frozen_threshold double precision NOT NULL,
 decision_state varchar(32) NOT NULL,
 eligible_channels jsonb NOT NULL DEFAULT '[]',
 reason_codes jsonb NOT NULL DEFAULT '[]',
 feature_snapshot jsonb NOT NULL,
 provenance jsonb NOT NULL,
 UNIQUE(tenant_id,id),
 FOREIGN KEY(tenant_id,customer_id) REFERENCES customers(tenant_id,id),
 CHECK(inactivity_probability BETWEEN 0 AND 1),
 CHECK(frozen_threshold BETWEEN 0 AND 1),
 CHECK(decision_state IN ('monitor','review_retention','no_contact_review')),
 CHECK(jsonb_typeof(eligible_channels)='array'),
 CHECK(jsonb_typeof(reason_codes)='array'),
 CHECK(jsonb_typeof(feature_snapshot)='object'),
 CHECK(jsonb_typeof(provenance)='object')
);
CREATE INDEX ix_predictions_customer_time
 ON customer_predictions(tenant_id,customer_id,scored_at DESC);
ALTER TABLE customer_predictions ENABLE ROW LEVEL SECURITY;
ALTER TABLE customer_predictions FORCE ROW LEVEL SECURITY;
CREATE POLICY tenant_scope ON customer_predictions
 USING (tenant_id=current_tenant_id()) WITH CHECK (tenant_id=current_tenant_id());
GRANT SELECT,INSERT ON customer_predictions TO growthpilot_app;
