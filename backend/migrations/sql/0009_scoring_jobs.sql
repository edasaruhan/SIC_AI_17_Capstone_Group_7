CREATE TABLE scoring_jobs (
 id uuid PRIMARY KEY, tenant_id uuid NOT NULL REFERENCES organizations(id),
 created_at timestamptz NOT NULL DEFAULT now(), requested_by uuid NOT NULL REFERENCES users(id),
 status varchar(24) NOT NULL DEFAULT 'queued', started_at timestamptz, completed_at timestamptz,
 total_customers integer NOT NULL DEFAULT 0, scored_customers integer NOT NULL DEFAULT 0,
 skipped_customers integer NOT NULL DEFAULT 0, failed_customers integer NOT NULL DEFAULT 0,
 model_sha256 varchar(64) NOT NULL, error_code varchar(80), UNIQUE(tenant_id,id),
 CHECK(status IN ('queued','running','succeeded','partial','failed')),
 CHECK(total_customers>=0 AND scored_customers>=0 AND skipped_customers>=0 AND failed_customers>=0),
 CHECK(model_sha256 ~ '^[0-9a-f]{64}$')
);
CREATE INDEX ix_scoring_jobs_tenant_time ON scoring_jobs(tenant_id,created_at DESC);
ALTER TABLE scoring_jobs ENABLE ROW LEVEL SECURITY;
ALTER TABLE scoring_jobs FORCE ROW LEVEL SECURITY;
CREATE POLICY tenant_scope ON scoring_jobs
 USING (tenant_id=current_tenant_id()) WITH CHECK (tenant_id=current_tenant_id());
GRANT SELECT,INSERT,UPDATE ON scoring_jobs TO growthpilot_app;
