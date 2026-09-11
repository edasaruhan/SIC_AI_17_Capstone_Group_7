# Backend guide

`backend/`, GrowthPilot'ın FastAPI uygulamasını, PostgreSQL migration'larını ve testlerini
barındırır. Kod modüler monolit olarak düzenlenmiştir; tenant ve yetki sınırları tüm
domain'lerin ortak platform sözleşmesidir.

## Dizinler

| Yol | Sorumluluk |
|---|---|
| `app/identity/` | Kimlik doğrulama, tenant context, üyelik ve RBAC |
| `app/crm/` | Müşteri ve Customer 360 işlemleri |
| `app/catalog/` | Ürün ve stok katalog modeli |
| `app/commerce/` | Sipariş, iade ve envanter hareketleri |
| `app/imports/` | Güvenli CSV/XLSX staging ve commit akışı |
| `app/analytics/` | Merkezi KPI ve müşteri analitiği |
| `app/ml/` | Paylaşılan veri, feature ve evaluation mantığı |
| `app/intelligence/` | Registry, inference, açıklama ve karar kayıtları |
| `app/integrations/` | Provider-neutral entegrasyon sözleşmeleri |
| `app/marketing/` | Attribution, audience ve kampanya kontrolü |
| `app/generation/` | Grounded içerik üretim sınırı |
| `app/platform/` | DB, audit, job, storage, webhook, güvenlik ve worker altyapısı |
| `migrations/` | Alembic revision'ları ve PostgreSQL/RLS SQL'i |
| `tests/` | Birim, entegrasyon, tenancy ve güvenlik testleri |

## Katman kuralı

Router HTTP sözleşmesini, schema doğrulamayı, service iş kuralını, model ise kalıcı veri
yapısını taşır. Tenant seçimi istemci alanından yapılmaz; doğrulanmış üyelikten çözülür ve
transaction-local PostgreSQL context ile RLS'ye aktarılır.

## Komutlar

```sh
uv run uvicorn app.main:create_app --factory --host 127.0.0.1 --port 8000
sh scripts/quality.sh
uv run alembic current
```

Kurulum için [`docs/LOCAL_DEVELOPMENT.md`](../docs/LOCAL_DEVELOPMENT.md), domain modeli
için [`docs/04_DOMAIN_MODEL.md`](../docs/04_DOMAIN_MODEL.md) ve güvenlik için
[`docs/07_SECURITY_PRIVACY_RESPONSIBLE_AI.md`](../docs/07_SECURITY_PRIVACY_RESPONSIBLE_AI.md).
