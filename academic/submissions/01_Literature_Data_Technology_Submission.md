# Literature, Data and Technology Submission

Evidence-led research foundation for a governed retail churn decision system

**AI AUTHORSHIP DISCLOSURE:** This document was drafted with OpenAI Codex/ChatGPT assistance and checked against repository evidence. Human review remains required.

## Executive summary

GrowthPilot AI addresses a practical marketing problem: small retail teams hold customer, order, product, inventory and advertising information in disconnected tools, so retention decisions are late, difficult to explain and hard to audit. The capstone narrows the first supervised-learning problem to future-purchase inactivity in a non-contractual retail setting. This is a prediction problem, not proof that a customer has permanently churned and not evidence that an intervention causes retention.

The research synthesis supports four methodological choices: define the outcome operationally; use chronological observation and outcome windows; compare a transparent baseline and logistic model before complex learners; and evaluate probability quality plus capacity-constrained ranking rather than accuracy alone. UCI Online Retail II was selected because its two-year transaction history supports temporal snapshots. The implemented technology stack keeps data provenance, tenant isolation, model versioning, consent and human approval inside one auditable workflow.

## Part I — Literature review

### 1. Problem statement and research question

In a contractual service, a cancellation can identify churn directly. In non-contractual retail, silence is ambiguous: a customer may be between purchases, seasonally inactive or permanently lost. GrowthPilot therefore asks: How accurately and usefully can pre-cutoff transaction behavior identify customers who will make no eligible purchase during a fixed 90-day future window, while preserving calibration, explanation and governed marketing use?

### 2. Theme one: customer status is latent

Jerath, Fader and Hardie (2011) show that models of customer “death” can encode materially different assumptions about when dropout occurs. Pareto/NBD treats dropout as a calendar-time process; BG/NBD attaches the opportunity to transaction time. Their comparison matters operationally because customer-status estimates depend on model assumptions, not an observable fact. Batislam, Denizel and Filiztekin (2007) likewise compare Pareto/NBD and BG/NBD on grocery transactions and frame active status and future purchasing as distinct predictive goals.

Platzer and Reutterer (2016) add purchase regularity to non-contractual customer-base models. This is important for GrowthPilot: a memoryless rule may mark a naturally periodic buyer as inactive. The implementation therefore includes recency, frequency, tenure and interpurchase-gap features, while still naming the target future inactivity rather than true churn.

### 3. Theme two: evaluation must match a marketing decision

A marketing team cannot contact every customer. Model evaluation therefore needs both statistical discrimination and an operating policy. PR-AUC is emphasized because inactivity prevalence changes across time; ROC-AUC remains a secondary ranking measure. Brier score, log loss and expected calibration error test probability quality. Precision, recall and lift in the highest-risk 5%, 10% and 20% translate scores into outreach-capacity evidence.

The final operating threshold was chosen on a separate calibration period as the score boundary for approximately 10% capacity, then frozen. This avoids choosing a threshold on the final temporal test. Campaign outcomes would require a randomized or credible quasi-experimental design; predictive lift alone cannot establish incremental marketing impact.

### 4. Theme three: explanation and governance

Explainability is useful only when its scope is explicit. Logistic coefficients and SHAP decompositions explain how the fitted model formed a score; they do not show that changing a feature will change behavior. GrowthPilot stores model, feature, target and split versions, artifact checksums and explanation payloads. Any recommendation is still constrained by current consent, purpose, role permissions, approval state, kill switch and budget limit.

### 5. Comparative synthesis

| Source | Objective / data / method | Findings used | Strength / limitation |
| --- | --- | --- | --- |
| Jerath, Fader & Hardie (2011) | Non-contractual customer death; two empirical datasets; PDO vs Pareto/NBD/BG-NBD | Dropout-time assumptions change customer metrics | Strong conceptual warning; not a supervised campaign-effect study |
| Batislam et al. (2007) | Grocery customer base; empirical Pareto/NBD and BG/NBD comparison | Active status and future purchasing require validation | Retail evidence; context does not guarantee transfer |
| Platzer & Reutterer (2016) | Non-contractual transactions; purchase regularity extension | Periodic behavior can improve customer-base modeling | Addresses cadence; still model-dependent latent status |
| Saito & Rehmsmeier (2015) | Imbalanced classification; ROC vs PR visualization | PR analysis is informative when positives are uneven | Metric guidance; not retail-specific |
| Lundberg & Lee (2017) | Unified additive feature-attribution framework | Local/global fitted-model explanations can be validated additively | Explanation is not causal attribution |

Evidence class: external-source synthesis. No GrowthPilot performance result is claimed in this table.

### 6. Marketing gap and contribution

The gap is not another isolated churn notebook. Small teams need a traceable path from raw records to a human decision: canonical data, versioned features, honest probability estimates, consent-aware prioritization and an approval gate. GrowthPilot contributes an integrated implementation and a reproducible capstone evaluation. It does not claim that one historical UK retailer represents every market, that future inactivity equals permanent churn, or that targeted outreach produces incremental revenue.

### 7. Literature conclusion

The literature justifies a conservative label and evaluation design. It also motivates explicit cadence features and the separation of prediction, explanation and causal effectiveness. These principles are encoded in the target memo, temporal split, model card and guarded marketing workflow.

## Part II — Data research

### 1. Objective and data needs

The data must support customer-level history before a cutoff and fully observed future outcomes after it. Required fields are a stable customer identifier, transaction/invoice identifier, timestamp, product identifier, quantity and price. Cancellation indicators, country and descriptions help quality checks. Advertising data is not required to train the first churn-proxy model; it belongs to later attribution and activation workflows.

### 2. Candidate assessment

| Dataset | Scope / access | Fit | Decision |
| --- | --- | --- | --- |
| UCI Online Retail II | 1,067,371 lines; 2009-12-01 to 2011-12-09; XLSX; CC BY 4.0; DOI 10.24432/C5CG6D | Two years, stable customer/invoice/time fields, multiple temporal cutoffs | Selected |
| UCI Online Retail | 541,909 lines; approximately one year; CC BY 4.0; DOI 10.24432/C5BW33 | Same retailer but shorter history | Rejected in favor of longer source |
| Online Shoppers Purchasing Intention | 12,330 sessions; CC BY 4.0; DOI 10.24432/C5F88Q | Session conversion, not longitudinal customer inactivity | Rejected |

Sources: UCI dataset records and repository dataset decision memo.

### 3. Selected source profile

| Dimension | Project-reproduced value |
| --- | --- |
| Raw size | 1,067,371 rows; 8 fields; 43 countries |
| Period | 2009-12-01 to 2011-12-09 |
| Customers / invoices | 5,942 identified customers; 53,628 invoices |
| Missingness | 243,007 rows missing customer ID; 4,382 missing description |
| Transaction anomalies | 19,494 cancellation rows; 22,950 nonpositive quantity; 6,207 nonpositive price |
| Duplicates | 34,335 exact duplicate rows |
| Eligible purchase evidence | 805,549 lines; 37,033 purchase events; 5,878 customers |

Evidence class: project-reproduced from external source. Values are generated by scripts/profile_dataset.py.

### 4. Quality, privacy and limitations

- Raw data is checksum-verified and ignored from Git; generated profiles record source URL, DOI, licence, size and SHA-256.

- Modeling excludes exact duplicates, unusable identity/date rows, cancellations and nonpositive purchase lines from eligible purchase events; raw evidence is not overwritten.

- Customer IDs are pseudonymous identifiers but still treated as linkable data. Processed customer-level files remain local and ignored; academic outputs contain only aggregates.

- The source is historical, single-retailer, UK-based and partly wholesale. Missing identifiers and survivor/censoring effects restrict representativeness.

### 5. Exploratory evidence and marketing insight

![Figure 1. Training-snapshot inactivity prevalence and recency distribution. Project-generated evidence.](../../artifacts/eda/training_label_recency.png)

*Figure 1. Training-snapshot inactivity prevalence and recency distribution. Project-generated evidence.*

![Figure 2. Training-snapshot frequency and spend behavior. Project-generated evidence.](../../artifacts/eda/training_frequency_spend.png)

*Figure 2. Training-snapshot frequency and spend behavior. Project-generated evidence.*

Median purchases per identified purchase customer are 3; the median observed interpurchase gap is 24.197 days and the 75th percentile is 61.194 days. These aggregates support a 90-day future window as a practical, purchase-cycle-informed inactivity horizon. They do not prove permanent loss. The skewed frequency/spend distributions also support log transformations and robust evaluation rather than raw-scale assumptions.

### 6. Data conclusion

Online Retail II is adequate for a reproducible temporal classification study and inadequate for claiming universal churn or campaign causality. Its licensing and provenance are explicit. Production use requires tenant-owned, consent-governed current data and new drift/quality validation.

## Part III — Technology review

### 1. Technology objective and marketing relevance

The technology must support ordinary customer operations and auditable intelligence in the same product. The priority is not maximum algorithmic complexity; it is reliable imports, canonical definitions, reproducible training/inference, tenant isolation, useful explanations and controlled actions.

### 2. Comparison

| Area | Selected technology | Why selected | Trade-off / control |
| --- | --- | --- | --- |
| API/domain | Python 3.12, FastAPI, Pydantic, SQLAlchemy | Typed validation, OpenAPI, shared ML ecosystem | Modular-monolith discipline and strict typing required |
| Database/tenancy | PostgreSQL RLS | Transactions, constraints, analytics and row-level tenant policy | RLS is defense-in-depth; application scope tests still required |
| Web | Next.js, React, strict TypeScript | Server-rendered operator UI and typed boundaries | Browser QA and accessibility require deployment-like validation |
| Jobs | Redis, Dramatiq, transactional outbox | Durable async imports/sync/scoring with retries | Operational monitoring and managed Redis needed |
| Modeling | scikit-learn + LightGBM candidates | Transparent pipelines plus nonlinear challenger | Validation chose regularized logistic regression, not assumed LightGBM |
| Tracking | MLflow | Run, parameter, metric and artifact provenance | Local registry is not a production registry service |
| Explanation | SHAP + logistic coefficients | Local/global score decomposition | Not causal; categorical encoding and correlated features complicate interpretation |
| Deployment | Containers + Terraform AWS reference | Portable local-to-cloud boundary | Paid cloud deployment and restore drills remain external |

Performance and cost conclusions are architectural assessments, not benchmark claims. Live provider latency/cost was not measured.

### 3. Use cases

- Customer 360: orders, value, RFM segment, predictions and consent in one tenant-scoped view.

- Capacity-aware retention review: sort customers by calibrated inactivity risk and commercial importance, then require approval.

- Operational analytics: versioned revenue/order/customer/inventory metrics with explicit null states when data is unavailable.

- Provider-neutral marketing ingestion: bounded raw payload provenance and canonical daily facts through fixed-origin adapters.

### 4. Limitations and opportunities

No live Meta, Google Ads, OIDC, LLM or cloud credentials were supplied; these boundaries are implemented and mock-tested but not live-validated. The local MLflow registry and single historical dataset do not establish production robustness. Next work after review should include credentialed sandbox validation, load/resilience tests, accessibility/browser review, managed backup/restore rehearsal and monitoring thresholds based on real operating data.

### 5. Technology conclusion

The stack is appropriate because it makes the capstone reproducible without separating the evidence pipeline from product controls. It remains a production-oriented local implementation, not a production deployment.

## References

Batislam, E. P., Denizel, M., & Filiztekin, A. (2007). Empirical validation and comparison of models for customer base analysis. International Journal of Research in Marketing, 24(3), 201–209. https://doi.org/10.1016/j.ijresmar.2006.12.005

Chen, D. (2012). Online Retail II [Dataset]. UCI Machine Learning Repository. https://doi.org/10.24432/C5CG6D

Jerath, K., Fader, P. S., & Hardie, B. G. S. (2011). New perspectives on customer “death” using a generalization of the Pareto/NBD model. Marketing Science, 30(5), 866–880. https://doi.org/10.1287/mksc.1110.0654

Lundberg, S. M., & Lee, S.-I. (2017). A unified approach to interpreting model predictions. Advances in Neural Information Processing Systems, 30. https://arxiv.org/abs/1705.07874

Platzer, M., & Reutterer, T. (2016). Ticking away the moments: Timing regularity helps to better predict customer activity. Marketing Science, 35(5), 779–799. https://doi.org/10.1287/mksc.2015.0963

Saito, T., & Rehmsmeier, M. (2015). The precision-recall plot is more informative than the ROC plot when evaluating binary classifiers on imbalanced datasets. PLOS ONE, 10(3), e0118432. https://doi.org/10.1371/journal.pone.0118432

Technology documentation: PostgreSQL row security; scikit-learn model evaluation and calibration; LightGBM Python API; SHAP documentation; MLflow tracking; FastAPI security; Next.js App Router. Accessed 8–9 September 2026; URLs are recorded in repository ADRs and research notes.
