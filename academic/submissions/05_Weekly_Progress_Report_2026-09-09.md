# Short Weekly Progress Report

**Team:** Group 7
**Project:** GrowthPilot AI
**Date:** 9 September 2026
**Reporter:** Şahin Başcı
**Status:** GREEN — local scope complete; external validation open

## 1. Progress since the previous report

Completed the production-oriented local application, temporal churn-proxy data/ML pipeline, frozen final evaluation, model registry/inference, integrations, attribution, audiences/campaign approval, security boundaries and all academic submission artifacts. No fabricated business result or live provider result is included.

## 2. Current focus

Final audit: rendered document/slide QA, clean full test suite, dependency/secret scans, evidence mapping and Phase 22–24 readiness documentation.

## 3. Status and evidence

Green for authorized local delivery. Backend: 83 tests passing before final package audit; frontend typecheck/lint/Vitest/webpack build passing. Final test: PR-AUC 0.647525, ROC-AUC 0.765878, Brier 0.199854; model SHA-256 942d705d…52ad.

## 4. Problems and risks

No live Meta, Google Ads, LLM, OIDC or cloud credentials; automated desktop/mobile Chromium and Axe checks pass, but manual multi-browser and assistive-technology review is outstanding; production backup/restore and load tests were not performed. Dataset is historical, single-retailer, UK-based; inactivity is a proxy, not contractual churn; predictive results are noncausal.

## 5. Support or decision needed

Project Lead should audit deliverables and decide whether to authorize final squash/publication. Founder must provide sandbox credentials and approve any deployment or real campaign. Submission dates in instructor files have elapsed and require instructor confirmation.

## 6. Tasks before next report

Address audit findings; run credentialed sandbox and manual browser/assistive-technology validation; rehearse backup/restore; define pilot eligibility and randomized holdout; only then request separate deployment/publication authorization.

**AI disclosure:** drafted with OpenAI Codex/ChatGPT assistance and verified against repository evidence; human review required.
