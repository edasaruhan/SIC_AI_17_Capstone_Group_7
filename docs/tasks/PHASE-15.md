# PHASE-15 — Production frontend integration

Status: COMPLETE
Goal: Provide a responsive, accessible B2B workspace over real API states.
Context: Core CRM, commerce, analytics, imports and intelligence APIs are available.
In scope: Next.js workspace shell, required navigation areas, dashboard, record lists,
Customer 360, server-only API credentials and loading/error/empty configuration states.
Out of scope: Managed OIDC screen branding and external production deployment.
Dependencies: PHASE-03 authentication boundary and operational APIs.
Acceptance: No placeholder metrics; responsive layout; secrets remain server-side;
typecheck, lint, unit/E2E tests and production build pass; manual multi-browser and
assistive-technology review remains an external validation gate.
Validation: `pnpm typecheck`, ESLint, Vitest, Playwright/Axe and Webpack production build passed.
Risks: OIDC-provider UI cannot be validated until a deployment provider is configured.

Review: The product shell covers overview, customers, Customer 360, intelligence,
audiences, orders, products, inventory, imports, integrations, campaigns, decisions,
settings and audit. Available sections read the API; unavailable facts show an honest
state. Turbopack cannot bind its CSS worker port in this environment, so the supported
Webpack production build is pinned and succeeds. Playwright exercises all 13 routes in
desktop and mobile Chromium viewports; 26/26 route checks pass with no Axe WCAG 2.0/2.1
A/AA violation, page exception or horizontal overflow. This automated evidence is not a
manual multi-browser/assistive-technology certification. Next: connector hub.
