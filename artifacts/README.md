# Reproducible evidence artifacts

Bu dizin raporlarda kullanılan küçük, commit edilmiş ve makine tarafından okunabilir
proje kanıtlarını içerir. Büyük/özel veri tabloları ve model binary'leri burada tutulmaz.

| Dizin | İçerik |
|---|---|
| `reports/` | Veri kaynağı profili ve veri hazırlama özeti |
| `eda/` | Training-only EDA özetleri ve grafikler |
| `ml/` | Aday karşılaştırması, frozen test, açıklamalar ve registry metadata |

`final_evaluation.json` dokunulmamış zamansal test sonucunun, `final_candidate.json`
seçilmiş model/threshold kararının, `model_registry.json` ise serving bütünlük kaydının
esas makine-okunabilir kaynaklarıdır.

Bu dosyalar gerçek production sonucu, nedensel kampanya etkisi veya gelir iddiası olarak
yorumlanmamalıdır. Yeniden üretim script'leri [`scripts/`](../scripts/README.md), yöntem ve
sınırlamalar [`docs/MODEL_EVALUATION.md`](../docs/MODEL_EVALUATION.md) altındadır.
