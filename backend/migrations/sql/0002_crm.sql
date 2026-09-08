CREATE TABLE customers (
 id uuid PRIMARY KEY, tenant_id uuid NOT NULL REFERENCES organizations(id),
 created_at timestamptz NOT NULL DEFAULT now(), name varchar(200) NOT NULL,
 email varchar(320), phone varchar(32), external_id varchar(200),
 status varchar(24) NOT NULL DEFAULT 'active', tags jsonb NOT NULL DEFAULT '[]',
 UNIQUE(tenant_id,id), UNIQUE(tenant_id,external_id),
 CHECK (length(trim(name))>0), CHECK (status IN ('active','inactive','lead')),
 CHECK (jsonb_typeof(tags)='array')
);
CREATE INDEX ix_customers_tenant ON customers(tenant_id,created_at DESC);
CREATE INDEX ix_customers_email ON customers(tenant_id,email);
CREATE TABLE customer_interactions (
 id uuid PRIMARY KEY, tenant_id uuid NOT NULL REFERENCES organizations(id),
 created_at timestamptz NOT NULL DEFAULT now(), customer_id uuid NOT NULL,
 kind varchar(24) NOT NULL, body text NOT NULL, actor_id uuid NOT NULL REFERENCES users(id),
 FOREIGN KEY(tenant_id,customer_id) REFERENCES customers(tenant_id,id),
 CHECK (kind IN ('note','call','email','meeting')), CHECK (length(body) BETWEEN 1 AND 5000)
);
CREATE TABLE marketing_consents (
 id uuid PRIMARY KEY, tenant_id uuid NOT NULL REFERENCES organizations(id),
 created_at timestamptz NOT NULL DEFAULT now(), customer_id uuid NOT NULL,
 channel varchar(24) NOT NULL, granted boolean NOT NULL, source varchar(200) NOT NULL,
 actor_id uuid NOT NULL REFERENCES users(id),
 FOREIGN KEY(tenant_id,customer_id) REFERENCES customers(tenant_id,id),
 CHECK(channel IN ('email','sms','ads'))
);
CREATE INDEX ix_consents_customer ON marketing_consents(tenant_id,customer_id,channel,created_at DESC);
CREATE TABLE audit_events (
 id uuid PRIMARY KEY, tenant_id uuid NOT NULL REFERENCES organizations(id),
 created_at timestamptz NOT NULL DEFAULT now(), actor_id uuid NOT NULL REFERENCES users(id),
 event_type varchar(120) NOT NULL, entity_id uuid NOT NULL, details jsonb NOT NULL DEFAULT '{}'
);
CREATE INDEX ix_audit_tenant ON audit_events(tenant_id,created_at DESC);
CREATE TABLE outbox_events (
 id uuid PRIMARY KEY, tenant_id uuid NOT NULL REFERENCES organizations(id),
 created_at timestamptz NOT NULL DEFAULT now(), event_type varchar(120) NOT NULL,
 payload jsonb NOT NULL, status varchar(24) NOT NULL DEFAULT 'pending', attempts integer NOT NULL DEFAULT 0,
 CHECK (attempts>=0), CHECK (status IN ('pending','published','failed'))
);
CREATE INDEX ix_outbox_pending ON outbox_events(tenant_id,status,created_at);
DO $$ DECLARE t text; BEGIN
 FOREACH t IN ARRAY ARRAY['customers','customer_interactions','marketing_consents','audit_events','outbox_events'] LOOP
  EXECUTE format('ALTER TABLE %I ENABLE ROW LEVEL SECURITY', t);
  EXECUTE format('ALTER TABLE %I FORCE ROW LEVEL SECURITY', t);
  EXECUTE format('CREATE POLICY tenant_scope ON %I USING (tenant_id=current_tenant_id()) WITH CHECK (tenant_id=current_tenant_id())', t);
  EXECUTE format('GRANT SELECT, INSERT ON %I TO growthpilot_app', t);
 END LOOP;
END $$;
GRANT UPDATE ON customers,outbox_events TO growthpilot_app;
