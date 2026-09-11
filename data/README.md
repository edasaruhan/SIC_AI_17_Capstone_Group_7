# Local data workspace

Bu dizin yeniden üretilebilir veri pipeline'ının yerel çalışma alanıdır. Veri katmanları
bilinçli olarak Git dışında tutulur:

- `raw/`: indirilen, değişmez kaynak snapshot'ı
- `interim/`: geçici doğrulama/dönüşüm çıktıları
- `processed/`: sürümlü train/validation/test tabloları
- `external/`: ayrıca onaylanmış harici girdiler

Kaynak veri repository'ye commit edilmez. İndirilen dosyanın kaynağı/lisansı ve checksum'ı
[`docs/DATASET_DECISION.md`](../docs/DATASET_DECISION.md) ile artifact metadata'sında
kaydedilir. Pipeline sırası için [`scripts/README.md`](../scripts/README.md).

Test fixture'ları gerçek müşteri veya akademik deney kanıtı değildir. Hassas veri bu
dizine konulmadan önce erişim, saklama, minimizasyon ve silme politikası onaylanmalıdır.
