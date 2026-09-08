# Imports, storage and durable delivery

Import v1 accepts insert-only customer and catalog records, not implicit merges,
historical orders or consent grants. Customers require external IDs, products SKUs.
Use the commerce API for stock/order actions so inventory rules remain authoritative.

1. POST `/api/v1/imports`: raw bytes, `X-File-Name`, `X-Import-Kind`
   (`customers`/`products`), `Idempotency-Key` and authenticated workspace headers.
2. GET `/{id}/preview`: first 20 rows and total count.
3. PUT `/{id}/mapping`: `{ "fields": { "name": "source header", ... } }`.
4. Review errors and normalized preview. Invalid batches cannot commit.
5. POST `/{id}/commit`: returns 202/queued, never reports completed before execution.
6. Poll detail; download `/{id}/errors.csv` if invalid/failed.

Every import preserves a SHA-256 source checksum, private UUID object reference,
source rows, mapping, transformation version, errors and audit events. A retry with
different bytes under the same key is a conflict. A preview-time duplicate or a
commit-time conflict cannot partially insert canonical rows. Revalidate failures
before retrying. No silent drops, destructive updates or opt-in consent inference.

Limits: 5 MiB raw, 1,000 data rows, 64 unique columns, 5,000 characters/cell.
UTF-8 CSV or genuine single-sheet XLSX only. ZIP member/expansion/ratio limits,
safe XML parsing, no macros/embeddings/external relationships or formulas.
CSV exports neutralize formula prefixes. Raw objects are outside webroot and have
no public download route. Filesystem creation is exclusive/mode 600; S3 uses
immutable puts and server-side encryption with ambient workload credentials.
These controls follow the [OWASP upload guidance](https://cheatsheetseries.owasp.org/cheatsheets/File_Upload_Cheat_Sheet.html)
and [openpyxl XML safety requirement](https://openpyxl.readthedocs.io/en/stable/).

## Delivery contract

Business state and outbox are PostgreSQL-backed. A trusted dispatcher is explicitly
configured for each organization's UUID; it does not accept an unauthenticated API
tenant claim. Redis messages contain only tenant/event UUIDs. A worker reads the
stored actor, revalidates active membership/capability, locks the event/batch and
commits canonical rows plus acknowledgement together. Duplicate delivery is safe.

Delivery statuses: pending → queued → published (consumer acknowledged), or failed.
Five delivery attempts maximum with 60×attempt-second leases. Redis failures retain
safe error codes; exhausted imports transition to failed for operator review.
Dramatiq internal retries are disabled to avoid competing retry loops. Domain-only
events currently acknowledge to the local consumer; live-provider handlers are not
implied. See [Dramatiq's retry semantics](https://dramatiq.io/guide.html).

```sh
uv run python scripts/local_redis.py
uv run dramatiq app.platform.worker --processes 1 --threads 2
uv run python scripts/dispatch_outbox.py --tenant ORGANIZATION_UUID --watch
```

Production requirements: private Redis with auth/TLS, S3 policy and retention review,
trusted tenant-subscription provisioning, worker monitoring and capacity limits.
S3 behavior is contract-tested, not cloud-validated. Malware scanning is not present;
raw files are never publicly served. Retention/orphan reconciliation is a security
hardening follow-up; an interrupted object-write/DB-commit can leave a private orphan.
