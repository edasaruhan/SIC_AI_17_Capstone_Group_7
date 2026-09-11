# GrowthPilot documentation index

Bu dizin ürün, mimari, veri/ML, güvenlik, teslim ve operasyon kararlarının kalıcı kayıt
merkezidir. İlk kez inceleyenler aşağıdaki sırayı izleyebilir.

## Hızlı okuma yolu

1. [`00_PROJECT_CHARTER.md`](00_PROJECT_CHARTER.md) — amaç, roller ve başarı tanımı
2. [`01_PRODUCT_SCOPE.md`](01_PRODUCT_SCOPE.md) — Release 1 kapsamı ve kapsam dışı alanlar
3. [`03_ARCHITECTURE_DECISIONS.md`](03_ARCHITECTURE_DECISIONS.md) — onaylı sistem yapısı
4. [`05_DATA_AND_ML_PLAN.md`](05_DATA_AND_ML_PLAN.md) — veri ve ML yöntemi
5. [`07_SECURITY_PRIVACY_RESPONSIBLE_AI.md`](07_SECURITY_PRIVACY_RESPONSIBLE_AI.md) — güvenlik sınırları
6. [`PRODUCTION_READINESS_REPORT.md`](PRODUCTION_READINESS_REPORT.md) — son yerel kanıt ve dış kapılar

## Ürün ve yönetişim

| Belge | Amaç |
|---|---|
| [`00_PROJECT_CHARTER.md`](00_PROJECT_CHARTER.md) | Misyon, paydaşlar ve çalışma ilkeleri |
| [`01_PRODUCT_SCOPE.md`](01_PRODUCT_SCOPE.md) | Ürün kapsamı, kullanıcılar ve Release 1 sınırı |
| [`02_CAPSTONE_REQUIREMENTS.md`](02_CAPSTONE_REQUIREMENTS.md) | Eğitmen gereksinimlerinin proje karşılığı |
| [`08_DELIVERY_PLAN.md`](08_DELIVERY_PLAN.md) | Teslim yaklaşımı ve faz yapısı |
| [`09_RISK_REGISTER.md`](09_RISK_REGISTER.md) | İzlenen ürün/teknik/akademik riskler |
| [`10_TASK_LOG.md`](10_TASK_LOG.md) | Tamamlanan çalışmaların toplu kaydı |
| [`11_ACADEMIC_DELIVERABLES_MAP.md`](11_ACADEMIC_DELIVERABLES_MAP.md) | Ödev, kaynak ve kanıt eşlemesi |
| [`ASSIGNMENT_FINAL_AUDIT.md`](ASSIGNMENT_FINAL_AUDIT.md) | Nihai ödev içerik, biçim, render ve kanıt denetimi |

## Mimari ve domain

| Belge | Amaç |
|---|---|
| [`03_ARCHITECTURE_DECISIONS.md`](03_ARCHITECTURE_DECISIONS.md) | Sistem bileşenleri ve kabul edilmiş kararlar |
| [`04_DOMAIN_MODEL.md`](04_DOMAIN_MODEL.md) | Tenant, müşteri, sipariş, stok ve pazarlama modeli |
| [`adr/README.md`](adr/README.md) | Altı kabul edilmiş ADR'nin dizini |
| [`ANALYTICS_CONTRACT.md`](ANALYTICS_CONTRACT.md) | Merkezi KPI ve analitik tanımları |
| [`IMPORTS_AND_JOBS.md`](IMPORTS_AND_JOBS.md) | Upload, staging, outbox ve worker sözleşmesi |
| [`INTEGRATIONS_MARKETING_SAFETY.md`](INTEGRATIONS_MARKETING_SAFETY.md) | Sağlayıcı ve kampanya güvenlik sınırları |

## Veri ve makine öğrenmesi

| Belge | Amaç |
|---|---|
| [`DATASET_DECISION.md`](DATASET_DECISION.md) | Veri kümesi kararı, kaynak ve sınırlamalar |
| [`RESEARCH_FOUNDATION.md`](RESEARCH_FOUNDATION.md) | Akademik/teknik dış kaynak sentezi |
| [`TARGET_DEFINITION.md`](TARGET_DEFINITION.md) | Churn proxy, uygunluk ve zamansal split |
| [`FEATURE_CONTRACT.md`](FEATURE_CONTRACT.md) | Özellik sürümü ve leakage sınırları |
| [`MODEL_EVALUATION.md`](MODEL_EVALUATION.md) | Adaylar, kalibrasyon ve final test sonuçları |
| [`MODEL_REGISTRY_AND_INFERENCE.md`](MODEL_REGISTRY_AND_INFERENCE.md) | Model bütünlüğü ve güvenli scoring |
| [`EXPLAINABILITY_AND_DECISIONS.md`](EXPLAINABILITY_AND_DECISIONS.md) | SHAP/açıklama ve karar kaydı yaklaşımı |
| [`12_BENCHMARK_NOTES.md`](12_BENCHMARK_NOTES.md) | Benchmark yorumlama notları |

## Operasyon, demo ve değerlendirme

| Belge | Amaç |
|---|---|
| [`LOCAL_DEVELOPMENT.md`](LOCAL_DEVELOPMENT.md) | Yerel kurulum ve kalite komutları |
| [`DEMO_GUIDE.md`](DEMO_GUIDE.md) | Güvenli uçtan uca demo akışı |
| [`06_MARKETING_MEASUREMENT.md`](06_MARKETING_MEASUREMENT.md) | Attribution ve etki ölçümü sınırları |
| [`OPERATIONS_SECURITY_RECOVERY.md`](OPERATIONS_SECURITY_RECOVERY.md) | Gözlemlenebilirlik, incident ve recovery |
| [`PRODUCTION_READINESS_REPORT.md`](PRODUCTION_READINESS_REPORT.md) | Geçen yerel kapılar ve production blocker'ları |
| [`tasks/README.md`](tasks/README.md) | PHASE-01–PHASE-24 kayıtlarının başlangıç noktası |

## Kaynak önceliği

- Ödevin tam ifadesi için `references/instructor/` altındaki orijinal dosya esastır.
- Proje kararı için kabul edilmiş ADR ve açık Project Lead kararı esastır.
- Sonuç/metrik için `artifacts/` altındaki yeniden üretilebilir kanıt esastır.
- `ödevler/` teslim kopyasıdır; üretim kaynağı `academic/` ve `scripts/` altındadır.

Kök başlangıç sayfasına dönmek için [`README.md`](../README.md).
