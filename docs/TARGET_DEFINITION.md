# Target Definition Memo — future-purchase inactivity v1

Status: FROZEN before label construction on 2026-09-08.
Owner: Project Lead methodology; implemented/reproduced by Codex.
Evidence: UCI Online Retail II project profile, not a contractual churn flag.

## Prediction question

For an identified customer who purchased in the 180 calendar days before a scoring
cutoff, will the customer make **no eligible purchase in the next 90 calendar days**?
`target_inactive_90d=1` means no future purchase in `[cutoff, cutoff + 90 days)`;
zero means at least one. This is an observable operational proxy for prioritizing a
retention review, not proof that the relationship permanently ended.

## Why 90 days

Among 31,155 observed gaps between purchase events, the reproduced median is 24.197
days, p75 61.194, p90 134.134 and p95 206.042. Ninety days gives roughly three median
cycles and exceeds p75 while retaining enough horizon inside the two-year source for
separate evaluation dates. It will necessarily mark some slow/cyclic repeat buyers
inactive; the product and reports must preserve that limitation. No threshold was
chosen from model performance.

## Population and event rules

- Unit: `(customer_id, cutoff)`; customer IDs must be present and numeric.
- Eligible population: at least one eligible purchase event in `[cutoff-180d, cutoff)`.
- Purchase line: valid date, customer ID, positive quantity and unit price, invoice
  not prefixed `C`; exact duplicate raw lines removed. Multiple lines for the same
  customer/invoice/timestamp form one purchase event.
- Cancellations/negative lines are retained separately for past return-behavior
  features, never counted as purchases or silently netted against another date.
- Feature window: data strictly before cutoff; primary aggregates use trailing 365
  and 90 days. No label-period values or dataset-end-derived customer status are features.
- Label window must be fully observed. The dataset ends 2011-12-09; final labels end
  2011-11-30, leaving source coverage beyond the exclusive boundary.

## Frozen temporal split v1

| Purpose | Cutoffs | May affect model/tuning? |
|---|---|---|
| Training | monthly 2010-06-01 through 2010-12-01 | Yes; preprocessing fitted here |
| Validation | 2011-03-01 | Yes; model family/hyperparameters/feature review |
| Calibration | 2011-06-01 | Calibration and operational threshold only |
| Final test | 2011-09-01 | No access until candidate, features, calibration and threshold are frozen |

Customers may recur at later cutoffs because the production task repeatedly scores an
installed customer base. All validation/test cutoffs occur after training label windows;
the estimate is temporal performance, not performance on never-before-seen identities.
Seasonality (especially final Q4) is a deliberate stress, but one retailer/year cannot
establish general seasonal robustness.

## Evaluation and decision boundary

Primary model metric: PR-AUC because the positive rate and intervention capacity matter.
Secondary: ROC-AUC, log loss, Brier score and calibration error. Operational evidence:
precision/recall/lift and captured positives at top 5%, 10% and 20%. A validation/
calibration-selected threshold is frozen before final test. Accuracy alone and a 0.5
threshold are not acceptance criteria. Models predict this label only; they do not
authorize outreach, imply causal lift, or override consent/action approval.

## Revisions

Any horizon, eligibility, event, cutoff or split change creates a new target/split
version and reruns experiments. `future-inactivity-v1` and `temporal-split-v1` remain
immutable identifiers for all resulting artifacts and MLflow runs.
