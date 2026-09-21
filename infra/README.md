# Deployment reference

This directory is a statically validated reference, not an active deployment.
No `terraform apply`, cloud account mutation, image publication or paid service was
authorized or performed.

## Containers

- `containers/backend.Dockerfile` packages the FastAPI API or Dramatiq worker.
- `containers/web.Dockerfile` packages the Next.js standalone server.
- `.dockerignore` excludes secrets, local data, model binaries, caches and instructor
  references from build contexts.

The approved model binary is intentionally not copied from ignored `.local/` state. A
release pipeline must fetch it from a private artifact store and provide it to BuildKit as
the `growthpilot_model` build secret. The backend image verifies the manifest SHA-256
before installing the file at the fixed `GP_MODEL_PATH`; a missing or mismatched artifact
fails the image build before any `joblib` deserialization. For example:

```sh
docker buildx build --secret id=growthpilot_model,src=/trusted/final_candidate.joblib \
  -f infra/containers/backend.Dockerfile .
```

The private artifact store, signed promotion policy and image publication target remain
release decisions. The Terraform worker starts `app.platform.worker`, where the Dramatiq
actor and Redis broker are defined.

## AWS Terraform reference

`terraform/aws/` describes private Fargate workloads, an HTTPS ALB, encrypted and
multi-AZ RDS PostgreSQL, encrypted Redis, a private/versioned S3 bucket, KMS,
Secrets Manager, CloudWatch logs and least-privilege task roles. Secret values are not
created in configuration; populate the named JSON secret through an authorized secret
management workflow. Migrations must run as a separate one-shot task before service
rollout, never from every API replica.

Static workflow:

```sh
terraform -chdir=infra/terraform/aws fmt -check -recursive
terraform -chdir=infra/terraform/aws init -backend=false
terraform -chdir=infra/terraform/aws validate
```

Before any apply, the Project Lead must approve region/residency, account boundaries,
domain/certificate, immutable image digests, OIDC provider, budgets, alarms, WAF policy,
database/runtime roles, model bootstrap, provider secrets and a tested rollback plan.
The documented RPO ≤15 minutes and RTO ≤4 hours remain targets until a managed
backup/restore drill proves them.
