# GrowthPilot AI Project Charter

Status: Active project charter
Initialized: 2026-09-08
Official repository: `https://github.com/edasaruhan/SIC_AI_17_Capstone_Group_7`

## Mission

GrowthPilot AI is an AI-powered, end-to-end marketing intelligence, customer operations, and marketing execution platform for small and medium businesses. It collects and normalizes business, customer, sales, inventory, and advertising data; supplies CRM/ERP-lite capabilities where those systems are absent; turns analytics and machine-learning outputs into explainable decisions; and supports controlled execution through marketing platforms.

There is one GrowthPilot project. Academic submissions document real work from the production-oriented product; they are not a separate demo.

## Business objective

Help businesses replace disconnected records and intuition-led marketing with auditable customer intelligence, measurable marketing decisions, and appropriately supervised action. The product must connect sales, customer, and advertising data without overstating attribution or causal impact.

## Governance

### Product Owner / Founder

Şahin Başcı owns commercial priorities, customer perspective, business constraints, and final product approval.

### Project Lead / Solution Architect / ML-AI Lead

ChatGPT owns major architecture, domain/data methodology, ML formulation and evaluation strategy, security principles, technical task decomposition, important audits, and Samsung submission strategy.

### Principal Implementation Engineer

Codex owns bounded implementation, repository engineering, source code, schemas, migrations, APIs, data/ML pipelines, integrations, tests, CI, observability controls, reproducibility, refactoring, and implementation documentation. Codex must escalate material objections rather than silently overriding approved decisions.

## Delivery model

Project Lead decision → bounded task → implementation → test/validation → handoff → Project Lead audit → next task.

No single autonomous run should attempt the complete Release 1 product.

## Quality principles

- Prefer the simplest design that satisfies real requirements and preserves clean upgrade paths.
- Maintain clear domain boundaries, auditability, reproducibility, security, testability, observability, and data lineage.
- Tenant isolation is non-negotiable; cross-tenant disclosure is a critical defect.
- High-impact marketing actions require review, approval, and audit.
- LLM output is advisory and grounded in trusted structured context.
- Quantitative claims require reproducible project evidence, a cited external source, or a clear planned/forecast label.
- Do not introduce distributed infrastructure, abstractions, or vendors without demonstrated need.

## Source precedence

Original instructor files govern exact assignment wording. Explicit Project Lead decisions and accepted ADRs govern project architecture and methodology. This charter and the other control documents summarize current approved context. Conflicts are logged for review rather than silently reconciled.

## Current state at TASK-000 completion

- Product vision and high-level Release 1 scope: defined.
- Official local Git repository: initialized on `main`; no commits or pushes made.
- Instructor references: inventoried and preserved.
- Production architecture and technology stack: not selected.
- Dataset and churn target: not selected or defined.
- EDA, feature engineering, training, and evaluation: not started; no ML metrics exist.
- Backend, frontend, CRM/ERP-lite, and ad connectors: not implemented.
