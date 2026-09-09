CREATE TABLE marketing_touchpoints (
 id uuid PRIMARY KEY, tenant_id uuid NOT NULL REFERENCES organizations(id), created_at timestamptz NOT NULL DEFAULT now(),
 customer_id uuid, occurred_at timestamptz NOT NULL, source varchar(40) NOT NULL,
 session_hash varchar(64), click_hash varchar(64), utm_source varchar(160), utm_medium varchar(160),
 utm_campaign varchar(300), external_campaign_id varchar(160),
 UNIQUE(tenant_id,id), FOREIGN KEY(tenant_id,customer_id) REFERENCES customers(tenant_id,id),
 CHECK(customer_id IS NOT NULL OR session_hash IS NOT NULL OR click_hash IS NOT NULL)
);
CREATE INDEX ix_touchpoints_customer_time ON marketing_touchpoints(tenant_id,customer_id,occurred_at DESC);
CREATE TABLE order_attributions (
 id uuid PRIMARY KEY, tenant_id uuid NOT NULL REFERENCES organizations(id), created_at timestamptz NOT NULL DEFAULT now(),
 order_id uuid NOT NULL, touchpoint_id uuid NOT NULL, method varchar(40) NOT NULL,
 method_version varchar(40) NOT NULL, evidence varchar(80) NOT NULL, quality varchar(40) NOT NULL,
 UNIQUE(tenant_id,id), UNIQUE(tenant_id,order_id,method_version),
 FOREIGN KEY(tenant_id,order_id) REFERENCES orders(tenant_id,id),
 FOREIGN KEY(tenant_id,touchpoint_id) REFERENCES marketing_touchpoints(tenant_id,id),
 CHECK(method='deterministic_last_touch'), CHECK(evidence='first_party_observed'),
 CHECK(quality IN ('exact_customer','exact_click','exact_session'))
);
CREATE TABLE audience_definitions (
 id uuid PRIMARY KEY, tenant_id uuid NOT NULL REFERENCES organizations(id), created_at timestamptz NOT NULL DEFAULT now(),
 created_by uuid NOT NULL REFERENCES users(id), name varchar(160) NOT NULL, version integer NOT NULL DEFAULT 1,
 status varchar(24) NOT NULL DEFAULT 'active', rule jsonb NOT NULL,
 UNIQUE(tenant_id,id), UNIQUE(tenant_id,name,version), CHECK(version>0),
 CHECK(status IN ('active','archived')), CHECK(jsonb_typeof(rule)='object')
);
CREATE TABLE audience_snapshots (
 id uuid PRIMARY KEY, tenant_id uuid NOT NULL REFERENCES organizations(id), created_at timestamptz NOT NULL DEFAULT now(),
 audience_id uuid NOT NULL, definition_version integer NOT NULL, generated_by uuid NOT NULL REFERENCES users(id),
 member_count integer NOT NULL DEFAULT 0, evidence varchar(80) NOT NULL DEFAULT 'canonical_operational_data',
 UNIQUE(tenant_id,id), FOREIGN KEY(tenant_id,audience_id) REFERENCES audience_definitions(tenant_id,id),
 CHECK(member_count>=0)
);
CREATE TABLE audience_members (
 id uuid PRIMARY KEY, tenant_id uuid NOT NULL REFERENCES organizations(id), created_at timestamptz NOT NULL DEFAULT now(),
 snapshot_id uuid NOT NULL, customer_id uuid NOT NULL, reason_codes jsonb NOT NULL, consent_channels jsonb NOT NULL,
 UNIQUE(tenant_id,id), UNIQUE(tenant_id,snapshot_id,customer_id),
 FOREIGN KEY(tenant_id,snapshot_id) REFERENCES audience_snapshots(tenant_id,id),
 FOREIGN KEY(tenant_id,customer_id) REFERENCES customers(tenant_id,id),
 CHECK(jsonb_typeof(reason_codes)='array'), CHECK(jsonb_typeof(consent_channels)='array')
);
CREATE TABLE campaigns (
 id uuid PRIMARY KEY, tenant_id uuid NOT NULL REFERENCES organizations(id), created_at timestamptz NOT NULL DEFAULT now(),
 created_by uuid NOT NULL REFERENCES users(id), integration_id uuid, audience_snapshot_id uuid,
 name varchar(200) NOT NULL, provider varchar(24) NOT NULL, budget numeric(14,2) NOT NULL,
 currency varchar(3) NOT NULL, status varchar(32) NOT NULL DEFAULT 'draft', provider_campaign_id varchar(160),
 approved_by uuid REFERENCES users(id), approved_at timestamptz, failure_code varchar(80),
 UNIQUE(tenant_id,id), FOREIGN KEY(tenant_id,integration_id) REFERENCES integrations(tenant_id,id),
 FOREIGN KEY(tenant_id,audience_snapshot_id) REFERENCES audience_snapshots(tenant_id,id),
 CHECK(provider IN ('meta_ads','google_ads')), CHECK(budget>=0),
 CHECK(status IN ('draft','pending_approval','approved','queued','executing','active','succeeded','failed','paused','cancelled'))
);
CREATE TABLE campaign_actions (
 id uuid PRIMARY KEY, tenant_id uuid NOT NULL REFERENCES organizations(id), created_at timestamptz NOT NULL DEFAULT now(),
 campaign_id uuid NOT NULL, actor_id uuid NOT NULL REFERENCES users(id), from_status varchar(32) NOT NULL,
 to_status varchar(32) NOT NULL, reason varchar(500) NOT NULL, idempotency_key varchar(160) NOT NULL,
 UNIQUE(tenant_id,id), UNIQUE(tenant_id,idempotency_key),
 FOREIGN KEY(tenant_id,campaign_id) REFERENCES campaigns(tenant_id,id)
);
DO $$ DECLARE t text; BEGIN
 FOREACH t IN ARRAY ARRAY['marketing_touchpoints','order_attributions','audience_definitions','audience_snapshots','audience_members','campaigns','campaign_actions'] LOOP
  EXECUTE format('ALTER TABLE %I ENABLE ROW LEVEL SECURITY', t);
  EXECUTE format('ALTER TABLE %I FORCE ROW LEVEL SECURITY', t);
  EXECUTE format('CREATE POLICY tenant_scope ON %I USING (tenant_id=current_tenant_id()) WITH CHECK (tenant_id=current_tenant_id())', t);
  EXECUTE format('GRANT SELECT,INSERT ON %I TO growthpilot_app', t);
 END LOOP;
END $$;
GRANT UPDATE ON audience_definitions,campaigns TO growthpilot_app;
