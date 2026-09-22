# Eğitmen İçin Proje İnceleme Rehberi

Bu rehber, GrowthPilot AI bitirme projesindeki bir iddiayı ilgili teslim dosyasına,
uygulama koduna ve yeniden incelenebilir kanıta bağlamak için hazırlanmıştır. Proje
**yerelde uygulanmış ve test edilmiştir; canlı AWS dağıtımı veya gerçek müşteri
performansı gösterilmiş değildir.** Teslim dosyalarının doğrudan bağlantıları
[ana README](../README.md#akademik-teslimler) ve [ödev paketi](../ödevler/README.md)
içindedir.

## Kısa inceleme yolu

1. [Sekiz slaytlık final sunumunu](../ödevler/06_Final_Sunumu/Odev_06_GrowthPilot_Final_Sunumu.pdf)
   açın. Ürün kapsamı, veri, model sonucu ve canlıya geçiş sınırı burada özetlenir.
2. [Model iyileştirme ve test raporunu](../ödevler/04_Model_Iyilestirme_ve_Test/Odev_04_Model_Iyilestirme_ve_Test.pdf)
   okuyun. Dondurulmuş zamansal test, kalibrasyon ve hata matrisi ayrıntıları buradadır.
3. [Model dağıtımı raporunu](../ödevler/07_Deployment/Odev_07_Model_Dagitimi_Deployment.pdf)
   inceleyin. API, güvenlik, izleme, gerçek kod düzeltmeleri ve henüz yapılmayan canlı
   doğrulamalar ayrı ayrı anlatılır.
4. İddiaların kaynağı için [nihai ödev denetimine](ASSIGNMENT_FINAL_AUDIT.md) ve
   [üretime hazırlık raporuna](PRODUCTION_READINESS_REPORT.md) bakın. Bunlar bir
   öğretim üyesi notu veya teslim alındı belgesi değildir; proje içi denetim kayıtlarıdır.

## İddia ile kanıt arasındaki yol

| İncelenecek konu | Açıklama | Birincil proje kanıtı |
| --- | --- | --- |
| Görev ve kapsam | [Eğitmen gereksinimleri eşlemesi](02_CAPSTONE_REQUIREMENTS.md), [ürün kapsamı](01_PRODUCT_SCOPE.md) | Değiştirilmemiş özgün dosyalar: [`references/instructor/`](../references/README.md) |
| Veri ve hedef | [Veri kümesi kararı](DATASET_DECISION.md), [90 günlük hedef](TARGET_DEFINITION.md), [özellik sözleşmesi](FEATURE_CONTRACT.md) | [`backend/app/ml/`](../backend/app/ml/), [`artifacts/eda/`](../artifacts/eda/) |
| Model seçimi ve nihai test | [Model değerlendirmesi](MODEL_EVALUATION.md) | [`final_evaluation.json`](../artifacts/ml/final_evaluation.json), [`final_candidate.json`](../artifacts/ml/final_candidate.json), [`model_registry.json`](../artifacts/ml/model_registry.json) |
| Açıklama ve insan kararı | [Açıklanabilirlik ve karar sınırı](EXPLAINABILITY_AND_DECISIONS.md) | [`explanations.json`](../artifacts/ml/explanations.json), [`backend/app/intelligence/`](../backend/app/intelligence/) |
| Organizasyon yalıtımı | [Güvenlik ilkeleri](07_SECURITY_PRIVACY_RESPONSIBLE_AI.md), [mimari kararlar](03_ARCHITECTURE_DECISIONS.md) | [`backend/app/identity/`](../backend/app/identity/), [`backend/tests/test_tenancy.py`](../backend/tests/test_tenancy.py), [`backend/tests/test_security_boundaries.py`](../backend/tests/test_security_boundaries.py) |
| API ve arka plan işi | [Model kayıt ve çıkarım rehberi](MODEL_REGISTRY_AND_INFERENCE.md), [veri alımı ve işler](IMPORTS_AND_JOBS.md) | [`backend/app/intelligence/router.py`](../backend/app/intelligence/router.py), [`backend/app/platform/worker.py`](../backend/app/platform/worker.py), [`backend/tests/test_deployment_contract.py`](../backend/tests/test_deployment_contract.py) |
| Dağıtım sınırı | [Dağıtım ödevi](../academic/submissions/07_Deployment_Submission.md), [üretime hazırlık raporu](PRODUCTION_READINESS_REPORT.md) | [`infra/containers/backend.Dockerfile`](../infra/containers/backend.Dockerfile), [`infra/terraform/aws/`](../infra/terraform/aws/), [`docs/tasks/TASK-DEPLOY-001.md`](tasks/TASK-DEPLOY-001.md) |

JSON kanıtları ve çalışma zamanındaki model dosyası farklı şeylerdir. İzlenen JSON
dosyaları sonuçları ve model soyunu belgeler. Dondurulmuş `joblib` modeli yerel
`.local/models/` altında Git dışında tutulur; SHA-256 değeri manifestte kayıtlıdır.
Konteyner oluşturma sözleşmesi bu dosyayı güvenilen bir kaynaktan BuildKit gizli girdisi
olarak bekler. Bu depoda yayımlanmış veya çalıştırılmış bir konteyner imajı yoktur.

## Sayıların nasıl okunacağı

`future-inactivity-v1` hedefi, uygun müşterinin sonraki 90 günde yeni uygun satın alma
yapmamasıdır. Bu bir **gelecekte işlem yapmama göstergesidir**; sözleşmesel müşteri kaybı,
kampanya etkisi veya gelir artışı ölçümü değildir. Tek tarihsel perakendeci verisiyle
yapılan dokunulmamış zamansal test 2.772 satır içerir. Sonuçlar:

| Ölçüt | Proje tarafından yeniden üretilen test sonucu |
| --- | ---: |
| PR-AUC | 0,647525 |
| ROC-AUC | 0,765878 |
| Brier skoru | 0,199854 |
| İlk yüzde 10 için kesinlik / artış | 0,748201 / 1,904513 |

Kaynak [`final_evaluation.json`](../artifacts/ml/final_evaluation.json) ve
[yöntem açıklaması](MODEL_EVALUATION.md) içindedir. Nihai test açıldıktan sonra model
ayarlarının yeniden seçilmesine izin verilmez. Operasyonel çıkarımda `country` alanı
her satırda `__missing__` olduğu hâlde eğitim verisinde ülke değişkenliği vardır.
Bu eğitim-sunum uyumsuzluğu giderilmeden model canlı kullanıma alınmamalıdır.

## Yerelde yeniden kontrol

Kurulum koşulları ve güvenli sıralama için önce [yerel geliştirme rehberini](LOCAL_DEVELOPMENT.md)
okuyun. Geliştirme ve test PostgreSQL veritabanları ile yerel Redis hazırsa depo
kökünden backend kalite kapısı çalıştırılabilir:

```sh
sh scripts/quality.sh
```

Son yerel çalıştırmada 127 Python dosyasının biçimi, 75 kaynak dosyasının tipleri ve
86 backend testi geçti. Bu sonuç GitHub Actions çalışması veya bulut dağıtımı sonucu
olarak sunulmuyor. Altyapı tanımının yalnız statik kontrolü için:

```sh
terraform fmt -check -recursive infra/terraform/aws
terraform -chdir=infra/terraform/aws validate
```

Komutlar AWS hesabında kaynak oluşturmaz. `terraform apply`, canlı reklam harcaması ve
gerçek sağlayıcı çağrıları bu inceleme yolunun parçası değildir.

## Sık sorulabilecek ayrımlar

- **Ürün yalnızca churn modeli mi?** Hayır. CRM, sipariş, stok, veri alımı, analitik,
  pazarlama onayları ve entegrasyon sınırları da vardır. Churn, ilk akademik ML problemidir.
- **Skor otomatik kampanya başlatıyor mu?** Hayır. Tahmin karar desteğidir;
  `action_authorized=false` döner. İnsan onayı, güncel rıza, bütçe ve durdurma anahtarı
  dış eylemden önce ayrıca denetlenir.
- **AWS üzerinde canlı mı?** Hayır. Terraform doğrulanmış bir referans tanımdır;
  hesapta `apply`, DNS/TLS kurulumu veya ücretli servis başlatma kanıtı yoktur.
- **Harici Meta/Google/LLM sonuçları gerçek mi?** Depodaki yerel sözleşme testleri
  gerçektir; sağlayıcı kimlik bilgileriyle canlı doğrulama ve reklam harcaması yoktur.
- **Tüm teslimler öğretim üyesi tarafından kabul edildi mi?** Hayır. İçerik ve biçim
  denetimi tamamlanmıştır; teslim kanalı, geçmiş tarihli haftalık raporun kabulü,
  notlandırma ve varsa ek rubrik dış süreçlerdir.

Tam belge dizini için [dokümantasyon indeksine](README.md), düzenlenebilir teslim
dosyaları için [ödev paketine](../ödevler/README.md) dönün.
