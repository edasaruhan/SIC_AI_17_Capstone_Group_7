# TASK-GITHUB-001 — Reviewer-facing repository navigation

**Status:** COMPLETE — LOCAL DOCUMENTATION ONLY

**Date:** 2026-09-22

**Owner:** Codex

## Task contract

**Goal:** Make the official repository easy for instructors to inspect, with a clear
five-minute route from academic deliverables to implementation and reproducible evidence.

**Context:** The existing README contained substantial technical content, but its first
screen did not link directly to the final files, terminology was inconsistent, and one
repository-map count no longer matched the seven instructor originals.

**In scope:** Root README information architecture, direct delivery links, Turkish
navigation guides, evidence boundaries, and relevant status/documentation corrections.

**Out of scope:** Moving instructor originals or stable source/evidence paths, changing
product behavior or architecture, creating new academic claims, deploying, or publishing
to GitHub without final authorization.

**Dependencies:** Existing academic package, frozen ML artifacts, accepted architecture,
production-readiness report and TASK-DEPLOY-001 evidence.

**Acceptance criteria:**

- An instructor can open every numbered delivery from the root README in one click.
- A short guide maps important claims to source, code, tests and limitations.
- Root, academic, delivery and documentation guides use consistent navigation.
- Relative links, files, numerical claims and publication language pass review.
- No instructor original, product code or academic outcome is changed.

**Validation:** Resolve relative Markdown links and heading anchors in changed files;
compare counts, metrics, paths and commands against repository evidence; inspect the diff
and run Git whitespace checks. A GitHub-rendered visual check remains publication-dependent.

**Risks:** Stale links, overclaiming production readiness, conflating local tests with
GitHub-hosted checks, and presenting internal academic audit as instructor acceptance.

## Completion record

**Files changed:** `README.md`, `academic/README.md`, `ödevler/README.md`,
`docs/README.md`, `docs/INSTRUCTOR_REVIEW_GUIDE.md`,
`docs/PRODUCTION_READINESS_REPORT.md`, `docs/10_TASK_LOG.md`,
`docs/tasks/README.md`, and this task record.

**Implementation summary:** Added direct deliverable links and a guided review route;
linked the frozen metrics to artifacts and runtime safeguards; clarified reproducibility
and external release gates; corrected the instructor-original count and test/publication
status language.

**Tests / commands run:** Local relative-link and anchor validation, artifact/count/path
cross-checks, `git diff --check`, and documentation diff review.

**Results:** All newly changed relative links and anchors resolved, reported ML figures
matched the frozen JSON, and whitespace checks passed. This was a documentation-only pass.

**Known limitations:** GitHub rendering and remote visibility cannot be asserted until
an authorized push and post-publication check. No new model or frontend/backend test
result is claimed by this task.

**Residual risks:** External links may change; instructor grading and production
readiness require external review and validation.

**Open questions:** Whether the founder authorizes publication of the finished local
documentation commit to the official remote.

**Decisions required:** Final publication authorization; none for the local documentation.

**Recommended next task:** After explicit authorization, push normal history without
squash/rewrite and visually verify the GitHub landing page and delivery links.
