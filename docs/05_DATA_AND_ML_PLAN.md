# Data and ML Plan

Status: Methodology guardrails and research plan only. No dataset, target, features, model, or result has been approved.

## Initial supervised problem

Business question: which customers are at risk of becoming inactive or lost early enough for a useful marketing intervention?

An eventual prediction should be tenant-owned and traceable to a customer, feature snapshot, target version, model version, scoring time, explanation, and any downstream decision. Churn classification is the first capstone ML problem, not the full GrowthPilot product.

## Dataset status and evaluation

No final dataset is selected. Candidate retail/e-commerce transaction datasets must be evaluated before acquisition or modeling for:

- provenance, licence, access conditions, source authority, sensitivity, and reproducibility;
- size, date coverage, customer/transaction counts, granularity, and schema;
- stable customer identifiers, timestamps, repeated purchases, orders/values, refunds, and cancellations;
- missingness, duplicates, impossible values, seasonality, survivorship, bias, and representativeness;
- customer-history sufficiency, target feasibility, censoring, leakage risk, and marketing relevance.

If a dataset cannot support a field or experiment, the limitation will be reported rather than filled with fabricated data. Separate validated datasets may support separate research questions.

## Target Definition Memo gate

No labels may be generated until the Project Lead approves a written memo covering:

- business meaning of churn/inactivity for the dataset and domain;
- prediction unit and prediction timestamp;
- purchase-cycle and repeat-purchase interval analysis;
- observation window, prediction horizon, and any inactivity window;
- minimum history, cohort eligibility, seasonality, and right censoring;
- treatment of refunds/cancellations and customers near dataset end;
- positive/negative label rules, exclusions, target version, and leakage analysis.

A time-aware formulation such as “features available at cutoff T predict qualifying purchase behavior during T+1 through T+H” is preferred when valid; T and H remain undecided.

## Feature hypotheses

Only data-supported, cutoff-safe features may be promoted. Hypotheses include:

- RFM: recency, frequency, and monetary value;
- transaction behavior: orders, units, revenue, order-value distribution;
- temporal behavior: tenure, first/last purchase, inter-purchase intervals, and recent-versus-historical activity;
- product behavior: product/category diversity and affinity;
- discount and refund/return behavior;
- prior marketing engagement and attributed response where actually observed.

Every production feature requires a name, entity, source, definition, timestamp semantics, null semantics, transformation, leakage analysis, and version. Feature computation will live in reusable code, not UI logic.

## Baselines and candidate models

Planned evidence-based comparison includes:

- a simple business baseline;
- Logistic Regression;
- Random Forest;
- LightGBM;
- XGBoost only if justified by evidence and project cost/complexity.

The original idea presentation names LightGBM as a preferred tabular candidate and SHAP as an explanation approach. Neither is pre-declared the winner; selection requires experimental evidence.

## Validation and leakage controls

- Prefer temporal holdout and rolling/expanding validation where the data supports them.
- Use grouped or stratified strategies only when compatible with the prediction unit and time semantics.
- Fit preprocessing and feature selection only on permitted training data.
- Do not use post-cutoff transactions, future aggregates, future CLV/revenue, target-window activity, or test-set feedback in features or tuning.
- Keep an untouched final holdout until model/refinement decisions and operating threshold are frozen.
- Add automated tests for split boundaries, customer duplication, cutoff behavior, feature timestamps, and leakage-sensitive transformations.

## Evaluation and operating decision

Accuracy alone is insufficient. Planned evaluation includes precision, recall, F1, ROC-AUC, PR-AUC, confusion matrix, Brier score, calibration curve, lift/gains, top-k recall/capture, action volume, and threshold/business utility analysis.

The operating threshold is not automatically 0.5. Validation evidence must relate it to outreach capacity, false-positive cost, missed-churn cost, customer value, and intervention policy. The final holdout is for unbiased evaluation, not threshold tuning.

## Refinement and explainability

The refinement story must be real and traceable: baseline → candidates → error analysis → feature revision → tuning → validation review → imbalance strategy → calibration → justified feature selection/threshold → frozen candidate → untouched test.

For a suitable final model, global and local SHAP analysis is planned. SHAP is an associational explanation, not causal proof. Business-language explanations must be deterministically grounded in model contributions and verified feature data; an LLM may not invent reasons.

## Experiment provenance

Each meaningful run must record experiment ID, timestamp, Git commit, dataset/source version, data snapshot, feature version, target version, split version, model, hyperparameters, random seed, metrics, and artifact path/integrity. The tracking technology, registry, artifact store, and serving pattern remain architecture decisions.

## Current results

None. No dataset has been selected, no target has been approved, no EDA or feature pipeline has run, and no model metrics exist.
