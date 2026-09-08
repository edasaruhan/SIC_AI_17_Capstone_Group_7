# Customer behavior feature contract v1

Version: `customer-behavior-v1`; target: `future-inactivity-v1`.
Evidence class: project implementation definition, not a performance result.

All aggregates use events strictly before the scoring cutoff. Eligible customers
have a purchase in the prior 180 days. Primary windows are 365 and 90 days:

- purchase event counts, spend, units, mean/max/std order value and basket size;
- unique products and total observed purchase count;
- mean/std/latest interpurchase gap, recency and observed tenure;
- return-line count/value and return-value share;
- country at latest purchase and cyclic cutoff-month terms.

Nonnegative skewed volume/value/count variables are transformed with `log1p`.
Day/cyclic features pass through. Median imputation is learned on training data and
adds missingness indicators; missing gap values mean insufficient purchase history,
not zero days. Country is imputed/one-hot encoded with infrequent and unknown-category
handling. Logistic scaling is robust and training-fitted; tree candidates use the
same engineered allowlist without scaling.

Targets, customer IDs, cutoff timestamps and version/split convenience columns are
explicitly ignored by the feature transformer. Negative values in nonnegative source
features and absent required columns fail closed. The serialized pipeline includes
the deterministic transformer and learned preprocessor so batch and on-demand paths
cannot silently diverge. Unit tests cover leakage-column mutation, missing/negative
input, missing-history imputation, unknown countries and serialization parity.

Known limits: country may proxy market context and is reviewed with permutation/SHAP
analysis; monetary values reflect historical GBP transaction price, not profit or FX;
data begins in 2009 so “observed tenure” is left-censored. No demographics, ad data,
consent, causal effect, or dataset-end status enters the model.
