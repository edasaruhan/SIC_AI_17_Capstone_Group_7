# PHASE-17 — Meta Ads and Google Ads adapters

Status: COMPLETE TO CREDENTIAL-FREE BOUNDARY
Goal: Implement current pinned read/reporting adapters without fabricating live access.
Context: Release 1 requires both providers; no provider credentials are present.
In scope: Official-doc review, HTTPS fixed origins, no redirects, OAuth headers, pinned
versions, paged/cursor contracts, daily campaign metric normalization and mock tests.
Out of scope: Live account validation, app review, token issuance and campaign mutation.
Dependencies: PHASE-16 hub.
Acceptance: Mock requests match provider boundary and invalid/negative facts fail closed.
Validation: Three contract tests inspect URL, auth/header handling and normalized values.
Risks: Version deprecation, account-specific attribution fields and permission review.

Review: Meta reporting is pinned to supported Marketing API `v25.0`; Google Ads REST is
pinned to `v25`. Google requires OAuth plus a developer token; Meta requires access tier
and permissions. Google’s official release notes identify v25 as the July 2026 major
release and its official guide requires the developer token and customer ID. No live
status is claimed. Sources: [Google release notes](https://developers.google.com/google-ads/api/docs/release-notes),
[Google REST authorization](https://developers.google.com/google-ads/api/rest/auth),
[Google developer token](https://developers.google.com/google-ads/api/docs/api-policy/developer-token),
[Meta Marketing API documentation](https://developers.facebook.com/docs/marketing-apis/).
