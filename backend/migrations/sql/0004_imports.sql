CREATE TABLE import_batches (
 id uuid PRIMARY KEY, tenant_id uuid NOT NULL REFERENCES organizations(id),
 created_at timestamptz NOT NULL DEFAULT now(), actor_id uuid NOT NULL REFERENCES users(id),
 kind varchar(24) NOT NULL, filename varchar(200) NOT NULL, checksum varchar(64) NOT NULL,
 object_id uuid NOT NULL, idempotency_key varchar(150) NOT NULL,
 status varchar(24) NOT NULL DEFAULT 'uploaded', headers jsonb NOT NULL,
 source_rows jsonb NOT NULL, mapping jsonb NOT NULL DEFAULT '{}',
 normalized_rows jsonb NOT NULL DEFAULT '[]', errors jsonb NOT NULL DEFAULT '[]',
 committed_count integer NOT NULL DEFAULT 0, attempts integer NOT NULL DEFAULT 0,
 transform_version varchar(32) NOT NULL DEFAULT 'canonical-import-v1',
 UNIQUE(tenant_id,id), UNIQUE(tenant_id,idempotency_key),
 CHECK(kind IN ('customers','products')),
 CHECK(status IN ('uploaded','invalid','validated','queued','succeeded','failed')),
 CHECK(committed_count>=0 AND attempts>=0)
);
CREATE INDEX ix_imports_tenant ON import_batches(tenant_id,created_at DESC);
ALTER TABLE import_batches ENABLE ROW LEVEL SECURITY;
ALTER TABLE import_batches FORCE ROW LEVEL SECURITY;
CREATE POLICY tenant_scope ON import_batches USING (tenant_id=current_tenant_id())
 WITH CHECK (tenant_id=current_tenant_id());
GRANT SELECT,INSERT,UPDATE ON import_batches TO growthpilot_app;
