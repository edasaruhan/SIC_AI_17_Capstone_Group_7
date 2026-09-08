CREATE TABLE users (
 id uuid PRIMARY KEY, issuer varchar(512) NOT NULL, subject varchar(256) NOT NULL,
 display_name varchar(200) NOT NULL, UNIQUE (issuer, subject)
);
CREATE TABLE organizations (
 id uuid PRIMARY KEY, name varchar(200) NOT NULL, currency varchar(3) NOT NULL DEFAULT 'TRY',
 timezone varchar(64) NOT NULL DEFAULT 'Europe/Istanbul', is_demo boolean NOT NULL DEFAULT false,
 CHECK (currency ~ '^[A-Z]{3}$')
);
CREATE TABLE memberships (
 id uuid PRIMARY KEY, tenant_id uuid NOT NULL REFERENCES organizations(id),
 user_id uuid NOT NULL REFERENCES users(id), role varchar(32) NOT NULL,
 active boolean NOT NULL DEFAULT true, created_at timestamptz NOT NULL DEFAULT now(),
 UNIQUE (tenant_id, user_id), CHECK (role IN ('OWNER','ADMIN','MARKETING_MANAGER','ANALYST','OPERATOR'))
);
CREATE INDEX ix_memberships_user ON memberships(user_id);

CREATE FUNCTION current_actor_id() RETURNS uuid LANGUAGE sql STABLE AS
$$ SELECT nullif(current_setting('app.actor_id', true), '')::uuid $$;
CREATE FUNCTION current_tenant_id() RETURNS uuid LANGUAGE sql STABLE AS
$$ SELECT nullif(current_setting('app.tenant_id', true), '')::uuid $$;

-- Resolve only a pre-authenticated identity; fixed search_path prevents shadowing.
CREATE FUNCTION resolve_actor(p_issuer text, p_subject text) RETURNS uuid
LANGUAGE sql STABLE SECURITY DEFINER SET search_path = pg_catalog, public AS
$$ SELECT id FROM public.users WHERE issuer=p_issuer AND subject=p_subject $$;
REVOKE ALL ON FUNCTION resolve_actor(text, text) FROM PUBLIC;
GRANT EXECUTE ON FUNCTION resolve_actor(text, text) TO growthpilot_app;

ALTER TABLE users ENABLE ROW LEVEL SECURITY;
-- The migration owner is deliberately allowed to resolve authenticated identities.
CREATE POLICY users_self ON users USING (id=current_actor_id());
ALTER TABLE organizations ENABLE ROW LEVEL SECURITY;
ALTER TABLE organizations FORCE ROW LEVEL SECURITY;
CREATE POLICY organization_scope ON organizations USING (id=current_tenant_id());
ALTER TABLE memberships ENABLE ROW LEVEL SECURITY;
ALTER TABLE memberships FORCE ROW LEVEL SECURITY;
CREATE POLICY membership_read ON memberships FOR SELECT
 USING (user_id=current_actor_id() OR tenant_id=current_tenant_id());
CREATE POLICY membership_write ON memberships FOR ALL
 USING (tenant_id=current_tenant_id()) WITH CHECK (tenant_id=current_tenant_id());

GRANT SELECT ON users, organizations, memberships TO growthpilot_app;
GRANT INSERT, UPDATE ON memberships TO growthpilot_app;
