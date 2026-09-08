# PHASE-13 — Explanation, customer intelligence and decisions

Status: COMPLETE
Goal: Explain the frozen ranker and convert scores into auditable review guidance.
Context: A calibrated logistic model passed one-time temporal evaluation with explicit limits.
In scope: SHAP/log-odds additivity, global/local evidence, reason codes, consent-aware
review recommendation and no-automation safety semantics.
Out of scope: Causal explanation, autonomous outreach, budget allocation or live scoring claims.
Dependencies: Frozen PHASE-12 model; CRM consent and audit contracts.
Acceptance: Explanations reproduce the underlying model output; decision rules never
grant consent/approval and carry target/model/feature provenance.
Validation: Additivity and reason-rule unit tests; anonymized explanation artifacts.
Risks: Correlated-feature overinterpretation, explanation/probability mismatch and
treating model rank as an intervention effect.

Review: Linear SHAP was evaluated on all 2,659 calibration rows against the underlying
logistic estimator. Maximum log-odds reconstruction error was `8.88e-16`; the report
explicitly excludes causal and calibrated-probability interpretation. Global evidence,
an inspected plot and three identifier-free representative cases were generated. A
strict pure policy now maps the frozen threshold plus explicit email/SMS/ads consent
to monitor, reviewed-retention or no-contact-review states. It always returns
`action_authorized=false`, carries full model lineage and requires human approval for
any potential outreach. Six policy tests cover bounds, consent and non-automation.
Limitations: Explanation evidence comes from the calibration population; correlated
features share importance and operational populations may differ. No business uplift
or treatment effect is inferred. Next: register the immutable model lineage and add a
demo-gated, tenant-safe inference record path.
