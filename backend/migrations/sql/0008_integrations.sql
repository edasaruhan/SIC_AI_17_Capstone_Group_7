CREATE TABLE integrations (
 id uuid PRIMARY KEY, tenant_id uuid NOT NULL REFERENCES organizations(id),
 created_at timestamptz NOT NULL DEFAULT now(), created_by uuid NOT NULL REFERENCES users(id),
 provider varchar(24) NOT NULL, name varchar(120) NOT NULL, external_account_id varchar(160) NOT NULL,
 secret_ref varchar(220) NOT NULL, api_version varchar(32) NOT NULL, status varchar(24) NOT NULL DEFAULT 'configured',
 cursor varchar(500), last_success_at timestamptz, last_error_code varchar(80),
 UNIQUE(tenant_id,id), UNIQUE(tenant_id,provider,external_account_id),
 CHECK(provider IN ('meta_ads','google_ads')), CHECK(status IN ('configured','syncing','healthy','error','disabled')),
 CHECK(secret_ref ~ '^env:GP_PROVIDER_[A-Z0-9_]+$')
);
CREATE TABLE integration_sync_runs (
 id uuid PRIMARY KEY, tenant_id uuid NOT NULL REFERENCES organizations(id),
 created_at timestamptz NOT NULL DEFAULT now(), integration_id uuid NOT NULL, requested_by uuid NOT NULL REFERENCES users(id),
 status varchar(24) NOT NULL DEFAULT 'queued', started_at timestamptz, completed_at timestamptz,
 input_cursor varchar(500), output_cursor varchar(500), records_received integer NOT NULL DEFAULT 0,
 raw_object_id uuid, raw_sha256 varchar(64), error_code varchar(80),
 UNIQUE(tenant_id,id), FOREIGN KEY(tenant_id,integration_id) REFERENCES integrations(tenant_id,id),
 CHECK(status IN ('queued','running','succeeded','failed')), CHECK(records_received>=0),
 CHECK(raw_sha256 IS NULL OR raw_sha256 ~ '^[0-9a-f]{64}$')
);
CREATE INDEX ix_sync_runs_integration ON integration_sync_runs(tenant_id,integration_id,created_at DESC);
CREATE TABLE ad_performance_daily (
 id uuid PRIMARY KEY, tenant_id uuid NOT NULL REFERENCES organizations(id),
 created_at timestamptz NOT NULL DEFAULT now(), integration_id uuid NOT NULL, sync_run_id uuid NOT NULL,
 provider varchar(24) NOT NULL, metric_date date NOT NULL, external_campaign_id varchar(160) NOT NULL,
 campaign_name varchar(300) NOT NULL, impressions bigint NOT NULL, clicks bigint NOT NULL,
 spend numeric(16,4) NOT NULL, conversions numeric(16,4), conversion_value numeric(16,4), currency varchar(3),
 UNIQUE(tenant_id,id), UNIQUE(tenant_id,integration_id,metric_date,external_campaign_id),
 FOREIGN KEY(tenant_id,integration_id) REFERENCES integrations(tenant_id,id),
 FOREIGN KEY(tenant_id,sync_run_id) REFERENCES integration_sync_runs(tenant_id,id),
 CHECK(provider IN ('meta_ads','google_ads')), CHECK(impressions>=0), CHECK(clicks>=0), CHECK(spend>=0),
 CHECK(conversions IS NULL OR conversions>=0), CHECK(conversion_value IS NULL OR conversion_value>=0)
);
DO $$ DECLARE t text; BEGIN
 FOREACH t IN ARRAY ARRAY['integrations','integration_sync_runs','ad_performance_daily'] LOOP
  EXECUTE format('ALTER TABLE %I ENABLE ROW LEVEL SECURITY', t);
  EXECUTE format('ALTER TABLE %I FORCE ROW LEVEL SECURITY', t);
  EXECUTE format('CREATE POLICY tenant_scope ON %I USING (tenant_id=current_tenant_id()) WITH CHECK (tenant_id=current_tenant_id())', t);
  EXECUTE format('GRANT SELECT,INSERT ON %I TO growthpilot_app', t);
 END LOOP;
END $$;
GRANT UPDATE ON integrations,integration_sync_runs TO growthpilot_app;
