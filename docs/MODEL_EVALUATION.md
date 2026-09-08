# Churn-proxy model evaluation

Evidence: project-executed UCI Online Retail II experiment. Target is future-purchase
inactivity (`future-inactivity-v1`), not observed contractual churn or causal response.

The selected candidate is L2 logistic regression (`C=0.01`) over the shared
`customer-behavior-v1` transformation. It narrowly improved validation ranking after
a bounded search and was sigmoid-calibrated on the separate 2011-06-01 snapshot.
Selection and the top-10%-capacity threshold were frozen before one-time test access.

| Split | Prevalence | PR-AUC | ROC-AUC | Brier | ECE-10 |
|---|---:|---:|---:|---:|---:|
| Validation (selection) | 0.577187 | 0.812223 | 0.787127 | 0.196710 | 0.106133 |
| Calibration (fit/descriptive) | 0.499436 | 0.739014 | 0.773722 | 0.193632 | 0.040863 |
| Final temporal test | 0.392857 | 0.647525 | 0.765878 | 0.199854 | 0.095054 |

Final-test 95% row-bootstrap intervals: PR-AUC 0.618131–0.678937, ROC-AUC
0.748534–0.782761, Brier 0.192598–0.207125. At the top 10% ranked capacity,
precision was 0.748201, recall 0.191001 and lift 1.904513. The calibration-frozen
numeric cutoff selected 10.8947% because the score distribution shifted/tied;
precision was 0.735099 and recall 0.203857 (TN 1603, FP 80, FN 867, TP 222).

The lower test prevalence and PR-AUC are material, not a reason to retune after seeing
the holdout. Results support a prioritization aid with human review, not automated
contact. ECE indicates predicted probabilities still need business-domain monitoring.
Same-customer temporal snapshots, one historical retailer, a Q4 test horizon, missing
customer IDs and wholesale mix limit generalization. No uplift, profit, ad response or
live-SME performance was measured. Exact manifests and plot are under `artifacts/ml/`;
local MLflow contains the run/model lineage.
