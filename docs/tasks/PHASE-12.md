# PHASE-12 — Refinement, calibration and untouched final test

Status: COMPLETE — frozen candidate evaluated once
Goal: Tune a bounded candidate set, freeze probability calibration/capacity threshold,
then evaluate exactly once on the untouched final period.
Context: Logistic narrowly led fixed exploration PR-AUC; all models need calibration review.
In scope: Validation-only tuning, train+validation refit, separate calibration-date
sigmoid fit, top-10% capacity cutoff, frozen artifact/hash and one final-test report.
Out of scope: Retuning after final results, causal retention value or live deployment.
Dependencies: PHASE-11 comparison and local MLflow.
Acceptance: Final test is never read by refinement script; candidate metadata/artifact
exist before evaluation; test results are immutable, complete and honestly reported.
Validation: Reproducible seeds, artifact hash, calibration/metric tests and rerun guard.
Risks: Validation overfit, same customers across dates, calibration in-sample optimism,
Q4 distribution shift and temptation to alter choices after test inspection.

Review: Five logistic, six forest and twelve seeded Optuna LightGBM trials used only
the validation date. Logistic C=0.01 won PR-AUC 0.812223. It was refit on historical
train+validation, sigmoid-calibrated on the separate 2011-06-01 snapshot, and a
top-10%-capacity threshold of 0.812509305136 was frozen with artifact SHA-256
`942d705d66a9469d57494626a99da83c91a9a895a3a2b2d7e977ff3ba56952ad`.
The guarded script then read the 2,772-row 2011-09-01 holdout exactly once.
Final results: prevalence 0.392857; PR-AUC 0.647525 (row-bootstrap 95% interval
0.618131–0.678937); ROC-AUC 0.765878 (0.748534–0.782761); Brier 0.199854
(0.192598–0.207125); log loss 0.582761; ECE-10 0.095054. Top-10% ranking precision
was 0.748201, recall 0.191001 and lift 1.904513. The fixed calibration threshold
selected 302/2,772 (10.8947%), precision 0.735099 and recall 0.203857.
Files: refinement/one-shot evaluation scripts, candidate/final JSON and reviewed
precision-recall/calibration figure. MLflow run `f39712c90301499a992427cc3becb008`.
Limitations: material validation-to-test prevalence/PR shift; calibration remains
imperfect and calibration-fit metrics are in-sample. Bootstrap treats rows as the
sampling unit and does not establish cross-retailer/general temporal uncertainty.
No post-test retuning is permitted. Next: explanations and decision semantics.
