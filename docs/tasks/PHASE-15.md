# PHASE-15 — Production frontend integration

Status: COMPLETE
Goal: Provide a responsive, accessible B2B workspace over real API states.
Context: Core CRM, commerce, analytics, imports and intelligence APIs are available.
In scope: Next.js workspace shell, required navigation areas, dashboard, record lists,
Customer 360, server-only API credentials and loading/error/empty configuration states.
Out of scope: Managed OIDC screen branding and external production deployment.
Dependencies: PHASE-03 authentication boundary and operational APIs.
Acceptance: No placeholder metrics; responsive layout; secrets remain server-side;
typecheck, lint and production build pass; browser review is an external validation gate.
Validation: `pnpm typecheck`, ESLint, Vitest and Webpack production build passed.
Risks: OIDC-provider UI cannot be validated until a deployment provider is configured.

Review: The product shell covers overview, customers, Customer 360, intelligence,
audiences, orders, products, inventory, imports, integrations, campaigns, decisions,
settings and audit. Available sections read the API; unavailable facts show an honest
state. Turbopack cannot bind its CSS worker port in this environment, so the supported
Webpack production build is pinned and succeeds. The in-app browser controller was not
callable in this environment; no browser/accessibility pass is claimed. Next: connector hub.
