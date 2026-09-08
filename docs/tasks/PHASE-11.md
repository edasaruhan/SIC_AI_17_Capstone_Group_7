# PHASE-11 — Baselines and model-family exploration

Status: COMPLETE — validation-only family comparison
Goal: Compare simple and candidate classifiers on the frozen validation date.
Context: Training/validation splits and shared feature pipeline are fixed.
In scope: Prevalence and recency baselines, logistic regression, random forest,
LightGBM, PR/ROC/log-loss/Brier/calibration/top-k metrics and local MLflow runs.
Out of scope: Calibration-set fitting, final-test access, SHAP claims or deployment.
Dependencies: PHASE-10 feature contract and prepared train/validation tables.
Acceptance: Every result traces to data/target/feature/split/git versions; selection
uses validation PR-AUC with calibration and operational utility reviewed.
Validation: Deterministic rerun, metric unit tests, serialized pipelines and MLflow.
Risks: Validation-period shift, repeated customer snapshots, overfitting and treating
ranking discrimination as causal campaign value.

Review: All candidates used the same allowlisted feature pipeline and inverse
customer-snapshot training weights. The fixed validation comparison was logged to
local MLflow; calibration and final-test files were not opened. Logistic regression
ranked first by the frozen primary metric, by only 0.000099 PR-AUC over LightGBM.
Results on 2011-03-01 validation: prevalence baseline PR-AUC 0.577187; recency
heuristic 0.715529; logistic 0.805322; LightGBM 0.805223; random forest 0.803517.
Logistic ROC-AUC was 0.782819, but Brier 0.213300/ECE 0.169377 show calibration work
is needed. LightGBM led top-5% precision (0.910714) while logistic was 0.880952;
this does not justify a winner change because primary selection was predeclared.
Files: evaluation module/tests, training script, `artifacts/ml/model_exploration.json`,
local uncommitted model/MLflow artifacts (ignored).
Limitations: one validation date and near-tie; fixed exploration parameters only.
Failed preliminary MLflow serialization attempts remain visibly failed local runs;
trusted project/custom LightGBM types were then explicitly allowlisted and rerun.
Decision required: None. Next: bounded validation tuning and separate calibration.
