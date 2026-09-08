ALTER TABLE outbox_events DROP CONSTRAINT outbox_events_status_check;
ALTER TABLE outbox_events ADD CONSTRAINT outbox_events_status_check
 CHECK(status IN ('pending','queued','published','failed'));
ALTER TABLE outbox_events ADD COLUMN available_at timestamptz NOT NULL DEFAULT now();
ALTER TABLE outbox_events ADD COLUMN last_error varchar(120);
CREATE INDEX ix_outbox_due ON outbox_events(tenant_id,status,available_at);
