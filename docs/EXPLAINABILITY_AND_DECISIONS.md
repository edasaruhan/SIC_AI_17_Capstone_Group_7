# Explainability and decision safety

GrowthPilot explains the frozen logistic candidate with Linear SHAP on the separate
calibration snapshot. The explainer exactly reconstructs the underlying estimator's
log-odds (maximum observed additivity error `8.88e-16`). It does not decompose the
outer sigmoid calibrator, and its contributions must not be described as probability
points, causes, treatment effects or evidence that an intervention will work.

Global importance and three anonymous representative local cases are recorded in
`artifacts/ml/explanations.json`; no customer identifier is exported. On this
calibration sample, missing gap-history, observed purchase count, 365-day purchase
count, recency and recent purchase/spend measures have the largest mean absolute
model contributions. Correlated behavior measures can redistribute apparent
importance, so rankings are model-behavior evidence rather than independent effects.

The pure decision policy uses only the frozen probability threshold and explicit
channel consent states:

- Below threshold: monitor; no contact channel is returned.
- At or above threshold with a granted channel: retention review; a human approval is
  still required.
- At or above threshold without a granted channel: no-contact review; no channel is
  returned.

Every result carries target, feature, split, model and checksum provenance. The policy
always returns `action_authorized=false`. It never grants consent, chooses a budget,
executes outreach or claims causal benefit. Monetary and recency inputs are retained
as optional review context but do not silently alter the frozen eligibility rule.
