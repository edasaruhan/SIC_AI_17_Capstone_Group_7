# Literature, data and technology research foundation

Status: PHASE-08 working synthesis. Evidence class is external-source unless stated.

## Problem framing

Retail here is non-contractual: inactivity is not an observed cancellation. The
customer-base literature treats whether a customer is still active as latent and
compares repeat-purchase/dropout processes such as Pareto/NBD and BG/NBD. This is the
central reason GrowthPilot calls its supervised outcome an *operational future-purchase
inactivity label*, records the definition/version, and avoids claiming biological or
contractual “death.” Batislam, Denizel and Filiztekin empirically compare these models
in grocery retail; Fader and Hardie's work discusses the transaction-time dropout
assumption and alternatives. Purchase regularity research also warns that memoryless
timing assumptions can miss cyclic buying. Sources: [Marketing Science, DOI 10.1287/mksc.1110.0654](https://pubsonline.informs.org/doi/10.1287/mksc.1110.0654),
[International Journal of Research in Marketing, DOI 10.1016/j.ijresmar.2006.12.005](https://doi.org/10.1016/j.ijresmar.2006.12.005),
[Marketing Science purchase-regularity study, DOI 10.1287/mksc.2015.0963](https://pubsonline.informs.org/doi/10.1287/mksc.2015.0963).

Consequences for the experiment:

- infer a purchase-cycle-informed horizon from training history, then freeze it;
- observe every label window completely and exclude right-censored snapshots;
- split chronologically; fit preprocessing/tuning/calibration on pre-test time only;
- compare a trivial prevalence/business baseline and logistic regression before trees;
- report discrimination, calibration and top-k operational utility, not accuracy alone;
- keep prediction separate from causal claims and actual campaign authorization.

## Data research

Online Retail II is selected in `DATASET_DECISION.md` because its two-year event
history and stable customer/time identifiers allow multiple temporal snapshots and a
final holdout. CC BY 4.0 is explicit. Its retailer/UK/wholesale mix, historical period,
missing IDs and cancellations limit external validity. The single-year subset cannot
add independent evidence because it overlaps the same retailer/source. Session
conversion data answers another question. A richer grocery dataset was considered but
not selected without explicit reusable licence terms.

## Technology research

The approved stack is intentionally conventional and auditable. PostgreSQL is both
the transactional store and initial versioned analytical layer; security-invoker
views preserve the caller's base-table privileges and RLS. scikit-learn pipelines
keep preprocessing/model execution together; calibrated probabilities and held-out
evaluation are required. LightGBM is a candidate gradient-boosted tree, never assumed
the winner. SHAP is an explanatory diagnostic, not a causal attribution engine.
MLflow stores parameters, dataset/target/feature/split/git versions, metrics and
artifacts for every reported run. The canonical feature module is shared by training
and inference; no separate feature-store platform is introduced without evidence.

Primary implementation sources are maintained alongside code and ADR-005:
[scikit-learn model evaluation](https://scikit-learn.org/stable/modules/model_evaluation.html),
[probability calibration](https://scikit-learn.org/stable/modules/calibration.html),
[LightGBM Python API](https://lightgbm.readthedocs.io/en/stable/Python-API.html),
[SHAP documentation](https://shap.readthedocs.io/en/latest/), and
[MLflow tracking](https://mlflow.org/docs/latest/ml/tracking/).

## Evidence boundary

This synthesis motivates methodology; it contains no performance result. Final
academic prose must cite the original publications, dataset DOI/licence and exact
executed experiment artifacts. AI-assisted drafting must be disclosed where required.
