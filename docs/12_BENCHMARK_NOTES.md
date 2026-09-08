# Group 8 Benchmark Notes

Status: Read-only benchmark inspection performed 2026-09-08. Source: `https://github.com/edasaruhan/SIC_AI_17_Capstone_Group_8`.

> **THIS IS A BENCHMARK, NOT A TEMPLATE TO COPY.** GrowthPilot has a different product, data problem, and architecture. No Group 8 code or report content was copied into this repository.

## Practices worth independently evaluating

- A disciplined repository layout separates configuration, data stages, documentation, notebooks, reports, reusable source, tests, and CI workflows.
- A pinned Python/runtime and locked dependency workflow can make setup and results reproducible; Group 8 uses `uv`, but GrowthPilot's language/package tooling is not yet selected.
- A small set of commands can perform setup, checks, data generation, validation, and report reproduction without manually running notebook cells in sequence.
- Generated/derived data can be excluded from Git when it is reproducible from pinned sources and commands.
- Reusable code belongs in source modules, orchestration in commands/scripts, and notebooks in exploration/narrative roles.
- CI should run meaningful lint, formatting, type, test, and reproducibility checks once GrowthPilot's stack is approved.
- Fixed/versioned data splits and automated leakage checks protect result validity.
- Raw metric outputs, configurations, logs, and artifact provenance should be retained alongside narrative reports.
- Report provenance should distinguish reproduced project figures, external sources, and planned/forecast material.
- Weak or failed experimental results should be reported honestly rather than hidden.
- Branch/PR and contribution rules reduce inconsistent team changes; GrowthPilot's exact workflow remains undecided.
- Connector/data pipelines benefit from preflight checks, resumability, idempotent stages, redacted logs, status commands, and clear runbooks where those needs apply.

## What must not be cargo-culted

- Group 8's specific problem framing, data, model/provider choices, dependency stack, folder tree, or report prose.
- Python, `uv`, Make, particular models, or their CI configuration without GrowthPilot-specific architecture review.
- Generated-data or API collection patterns without licence, privacy, cost, provider-policy, and tenant-isolation analysis.

## GrowthPilot's additional bar

Beyond academic/ML reproducibility, GrowthPilot must support a real multi-tenant SaaS direction: CRM, ERP-lite, secure imports, customer intelligence, marketing integrations, attribution, decision/action audit, privacy, observability, and controlled marketing execution.
