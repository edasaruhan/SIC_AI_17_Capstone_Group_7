CREATE TABLE generation_drafts (
 id uuid PRIMARY KEY, tenant_id uuid NOT NULL REFERENCES organizations(id), created_at timestamptz NOT NULL DEFAULT now(),
 customer_id uuid NOT NULL, actor_id uuid NOT NULL REFERENCES users(id), channel varchar(24) NOT NULL,
 objective varchar(500) NOT NULL, verified_facts jsonb NOT NULL, provider varchar(40) NOT NULL,
 provider_model varchar(160) NOT NULL, output text NOT NULL, status varchar(32) NOT NULL,
 human_approval_required boolean NOT NULL DEFAULT true, action_authorized boolean NOT NULL DEFAULT false,
 UNIQUE(tenant_id,id), FOREIGN KEY(tenant_id,customer_id) REFERENCES customers(tenant_id,id),
 CHECK(channel IN ('email','sms')), CHECK(jsonb_typeof(verified_facts)='object'),
 CHECK(status IN ('generated','rejected_grounding')), CHECK(human_approval_required), CHECK(NOT action_authorized)
);
ALTER TABLE generation_drafts ENABLE ROW LEVEL SECURITY;
ALTER TABLE generation_drafts FORCE ROW LEVEL SECURITY;
CREATE POLICY tenant_scope ON generation_drafts
 USING (tenant_id=current_tenant_id()) WITH CHECK (tenant_id=current_tenant_id());
GRANT SELECT,INSERT ON generation_drafts TO growthpilot_app;
