# PHASE-12 — Refinement, calibration and untouched final test

Status: IN PROGRESS
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
