# GrowthPilot AI Akademik Kaynak Paketi

Bu dizin bitirme projesinin **Türkçe metin kaynaklarını ve onlardan üretilmiş belgeleri**
içerir. Teslim için numaralandırılmış eş kopyalar [`ödevler/`](../ödevler/README.md)
altındadır. Eğitmenin yedi özgün kaynak/şablon dosyası
[`references/instructor/`](../references/README.md) altında değiştirilmeden korunur.

## Dosya yolu ve kullanım amacı

| No | Konu | Okunabilir kaynak | Belge ve PDF |
| --- | --- | --- | --- |
| 01 | Literatür, veri ve teknoloji | [Markdown](submissions/01_Literature_Data_Technology_Submission.md) | [DOCX](submissions/01_Literature_Data_Technology_Submission.docx) · [PDF](submissions/01_Literature_Data_Technology_Submission.pdf) |
| 02 | Kavram notu ve uygulama planı | [Markdown](submissions/02_Concept_Note_and_Implementation_Plan.md) | [DOCX](submissions/02_Concept_Note_and_Implementation_Plan.docx) · [PDF](submissions/02_Concept_Note_and_Implementation_Plan.pdf) |
| 03 | Veri hazırlama ve model keşfi | [Markdown](submissions/03_Data_Preparation_Feature_Engineering_Model_Exploration.md) | [DOCX](submissions/03_Data_Preparation_Feature_Engineering_Model_Exploration.docx) · [PDF](submissions/03_Data_Preparation_Feature_Engineering_Model_Exploration.pdf) |
| 04 | Model iyileştirme ve test | [Markdown](submissions/04_Model_Refinement_and_Test_Submission.md) | [DOCX](submissions/04_Model_Refinement_and_Test_Submission.docx) · [PDF](submissions/04_Model_Refinement_and_Test_Submission.pdf) |
| 05 | Haftalık ilerleme raporu | [Markdown](submissions/05_Weekly_Progress_Report_2026-09-09.md) | [DOCX](submissions/05_Weekly_Progress_Report_2026-09-09.docx) · [PDF](submissions/05_Weekly_Progress_Report_2026-09-09.pdf) |
| 06 | Final sunumu | Düzenlenebilir [PPTX](presentation/GrowthPilot_AI_Final_Presentation.pptx) | [Sekiz slayt PDF](presentation/GrowthPilot_AI_Final_Presentation.pdf) |
| 07 | Model dağıtımı | [Markdown](submissions/07_Deployment_Submission.md) | [DOCX](submissions/07_Deployment_Submission.docx) · [13 sayfa PDF](submissions/07_Deployment_Submission.pdf) |

Raporların Markdown dosyaları anlatımın kaynak metnidir. Şekiller
[`figures/`](figures/) altında bulunur. Sayısal ML sonuçlarının kaynak dosyaları ise
[`artifacts/ml/`](../artifacts/ml/) içindedir. Dış kaynak iddiaları kaynakçayla;
proje tarafından yeniden üretilen sonuçlar, planlar ve canlıda henüz doğrulanmayan
özellikler ayrı etiketlerle sunulur. Yapay zekâ desteği teslim metinlerinde açıklanır.

## Yazılı raporları yeniden üretme

01–05 numaralı yazılı belgeler ve `ödevler/` eş kopyaları depo kökünden şu komutla
yeniden üretilir:

```sh
uv run python scripts/generate_academic_deliverables.py
```

Bu işlem PDF dışa aktarımı için `soffice` gerektirir; PDF üretilemezse hata verir.
07 numaralı dağıtım ödevi ayrı bir üretici kullanır, çünkü özgün
[`Deployment Submission.docx`](../references/instructor/Deployment%20Submission.docx)
şablonundan türetilmiştir:

```sh
uv run python scripts/generate_deployment_submission.py
```

Bu komut iki diyagramı, akademik DOCX'i ve düzenlenmiş DOCX eş kopyasını üretir.
PDF, DOCX sayfaları render edilip görsel olarak kontrol edildikten sonra dışa
aktarılmıştır. Özgün şablon değiştirilmemiştir; A4 sayfa sistemi, Times New Roman
tipografisi ve altı ana bölüm sırası korunmuştur.

Final sunumunun düzenlenebilir dosyası PPTX'tir. Sunumun ilk tasarım çalışma alanı
bu depoda bulunmadığı için burada sıfırdan üretilebilir bir sunum betiği olduğu
iddia edilmez. İçeriği, PDF eş kopyası ve görsel denetim sonucu
[nihai ödev denetiminde](../docs/ASSIGNMENT_FINAL_AUDIT.md) kayıtlıdır.

Teslim gereksinimleri ile kanıt bağlantıları için
[eğitmen inceleme rehberine](../docs/INSTRUCTOR_REVIEW_GUIDE.md) bakın.
