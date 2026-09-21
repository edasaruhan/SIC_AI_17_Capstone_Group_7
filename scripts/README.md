# Automation scripts

Bu dizin kurulum, veri/ML kanıtı, kalite ve akademik teslim üretimini tekrar edilebilir
komutlara dönüştürür. Script'ler repository kökünden çalıştırılmalıdır.

## Yerel altyapı ve kalite

| Script | İşlev |
|---|---|
| `local_setup.py` | İzole PostgreSQL kümesi, database/roller ve güvenli yerel `.env` |
| `migrate_test.py` | Ayrı test database'ini migration head'e getirir |
| `local_redis.py` | Parola korumalı loopback Redis örneğini başlatır |
| `dispatch_outbox.py` | Tenant'a sabitlenmiş outbox dispatcher çalıştırır |
| `ci_setup.py` | Disposable CI servislerini hazırlar |
| `quality.sh` | Ruff, format, strict mypy ve pytest kalite kapısı |

## Veri ve ML sırası

1. `download_dataset.py`
2. `profile_dataset.py`
3. `prepare_ml_data.py`
4. `generate_eda.py`
5. `train_models.py`
6. `refine_model.py`
7. `evaluate_final.py`
8. `explain_model.py`
9. `register_model.py`

Final test değerlendirmesi korunmuş holdout üzerinde bir kez çalıştırılmıştır; sonuçları
iyileştirmek amacıyla tekrar tuning yapılmamalıdır. Yöntem:
[`docs/MODEL_EVALUATION.md`](../docs/MODEL_EVALUATION.md).

## Akademik çıktı

`generate_academic_deliverables.py`, commit edilmiş artifact'lardan beş yazılı raporu
üretir, LibreOffice ile PDF'e dönüştürür ve DOCX/PDF kopyalarını `ödevler/` ile eşitler:

```sh
uv run python scripts/generate_academic_deliverables.py
```

Eğitmen orijinalleri okunur ancak hiçbir zaman değiştirilmez.

`generate_deployment_submission.py`, `references/instructor/Deployment Submission.docx`
şablonunun A4 ve Times New Roman düzeninden model dağıtımı raporunu türetir, iki mimari
şekli üretir ve DOCX'i `ödevler/07_Deployment/` ile eşitler. Script production dağıtımı
yapılmış gibi kanıt üretmez:

```sh
uv run python scripts/generate_deployment_submission.py
```
