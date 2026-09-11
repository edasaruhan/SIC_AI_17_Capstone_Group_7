"""Translate the final academic PPTX text while preserving its OOXML design."""

# ruff: noqa: E501, S314

from __future__ import annotations

import os
import tempfile
import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
PPTX = ROOT / "academic" / "presentation" / "GrowthPilot_AI_Final_Presentation.pptx"

NS_A = "http://schemas.openxmlformats.org/drawingml/2006/main"
NS_C = "http://schemas.openxmlformats.org/drawingml/2006/chart"

TRANSLATIONS = {
    "Customer operations, explainable inactivity risk, and governed marketing action": "Müşteri operasyonları, açıklanabilir hareketsizlik riski ve denetimli pazarlama eylemi",
    "Samsung Innovation Campus · Group 7 · Şahin Başcı": "Samsung Innovation Campus · Grup 7 · Şahin Başcı",
    "Final local evidence package · 9 September 2026": "Nihai yerel kanıt paketi · 9 Eylül 2026",
    "AI-assisted drafting disclosed · Human review required": "Yapay zekâ desteği açıklanmıştır · İnsan incelemesi gereklidir",
    "THE OPERATING PROBLEM": "OPERASYON SORUNU",
    "Marketing decisions fail when the evidence trail is fragmented": "Kanıt izi parçalandığında pazarlama kararları başarısız olur",
    "Customer context": "Müşteri bağlamı",
    "CRM notes and consent are detached from orders and value.": "CRM notları ve rıza, sipariş ve değerden kopuktur.",
    "Commercial truth": "Ticari gerçek",
    "Inventory, returns and revenue definitions drift across files.": "Stok, iade ve gelir tanımları dosyalar arasında değişir.",
    "Paid media": "Ücretli medya",
    "Provider metrics arrive without consistent provenance or identity.": "Sağlayıcı ölçütleri tutarlı kaynak ve kimlik olmadan gelir.",
    "The bottleneck is not a lack of dashboards.": "Darboğaz, gösterge paneli eksikliği değildir.",
    "It is the absence of a traceable path from data to a reviewed decision.": "Sorun, veriden incelenmiş karara uzanan izlenebilir yolun olmamasıdır.",
    "GrowthPilot makes provenance, tenant scope, consent and approval part of that path.": "GrowthPilot kaynak, kiracı kapsamı, rıza ve onayı bu yolun parçası yapar.",
    "Project problem framing; no commercial outcome is claimed.": "Proje problem çerçevesi; ticari sonuç iddia edilmez.",
    "THE PRODUCT": "ÜRÜN",
    "One governed workflow connects source data to human action": "Tek yönetişimli akış, kaynak veriyi insan eylemine bağlar",
    "1 · INGEST": "1 · AL",
    "Validated imports": "Doğrulanmış içe aktarımlar",
    "and provider adapters": "ve sağlayıcı bağdaştırıcıları",
    "2 · STORE": "2 · SAKLA",
    "Canonical records": "Standart kayıtlar",
    "with PostgreSQL RLS": "ve PostgreSQL RLS",
    "3 · ANALYZE": "3 · ANALİZ ET",
    "Versioned KPIs, RFM": "Sürümlü KPI, RFM",
    "and inactivity scores": "ve hareketsizlik puanı",
    "4 · REVIEW": "4 · İNCELE",
    "Explanation, consent": "Açıklama, rıza",
    "and audience snapshot": "ve kitle anlık görüntüsü",
    "5 · ACT": "5 · UYGULA",
    "Approval required": "Onay zorunlu",
    "kill switch remains on": "acil durdurma açık",
    "Controls that never drop away": "Her zaman geçerli denetimler",
    "Tenant scope  ·  server-side RBAC  ·  checksums  ·  consent  ·  approval  ·  audit": "Kiracı kapsamı · sunucu RBAC · sağlama toplamı · rıza · onay · denetim",
    "Implemented locally; live provider execution remains disabled.": "Yerelde uygulandı; canlı sağlayıcı yürütmesi kapalıdır.",
    "DATA AND TARGET": "VERİ VE HEDEF",
    "The experiment uses time as a guardrail, not a random split": "Deney, rastgele bölme yerine zamanı koruma sınırı yapar",
    "transaction lines": "işlem satırı",
    "identified customers": "tanımlı müşteri",
    "90 days": "90 gün",
    "future inactivity window": "gelecek hareketsizlik penceresi",
    "TRAIN": "EĞİTİM",
    "7 cutoffs": "7 kesim",
    "20,677 rows": "20.677 satır",
    "VALIDATE": "DOĞRULAMA",
    "3,349 rows": "3.349 satır",
    "CALIBRATE": "KALİBRASYON",
    "2,659 rows": "2.659 satır",
    "TEST": "TEST",
    "2,772 rows": "2.772 satır",
    "Features use events strictly before each cutoff; every label window is fully observed.": "Özellikler yalnız kesim öncesi olayları kullanır; her etiket penceresi tam gözlenir.",
    "Future inactivity is an operational proxy — not contractual churn and not campaign causality.": "Gelecek hareketsizliği operasyonel vekildir; gerçek kayıp veya kampanya nedenselliği değildir.",
    "UCI Online Retail II profile and temporal split artifacts.": "UCI Online Retail II profili ve zamansal veri bölümü eserleri.",
    "MODEL EXPLORATION": "MODEL KEŞFİ",
    "Evidence selected a simpler model than the concept predicted": "Kanıt, kavramda öngörülenden daha yalın modeli seçti",
    "Validation PR-AUC": "Doğrulama PR-AUC",
    "Selected for refinement": "İyileştirme için seçildi",
    "Regularized": "Düzenlileştirilmiş",
    "logistic regression": "lojistik regresyon",
    "C = 0.01 improved validation PR-AUC to 0.812223. Sigmoid calibration and the ~10% threshold were then frozen before test access.": "C = 0.01 doğrulama PR-AUC'yi 0.812223'e çıkardı. Sigmoid kalibrasyon ve yaklaşık %10 eşik testten önce donduruldu.",
    "LightGBM was not chosen merely because the original concept expected it.": "LightGBM yalnız ilk kavramda öngörüldüğü için seçilmedi.",
    "Project-executed validation only · artifacts/ml/model_exploration.json.": "Yalnız projede yürütülen doğrulama · artifacts/ml/model_exploration.json.",
    "UNTOUCHED FINAL EVALUATION": "DOKUNULMAMIŞ NİHAİ DEĞERLENDİRME",
    "The frozen test shows useful ranking and visible temporal shift": "Dondurulmuş test yararlı sıralama ve belirgin zamansal kayma gösterir",
    "Top-10% lift": "İlk %10 artış",
    "Frozen threshold": "Dondurulmuş eşik",
    "customers selected": "müşteri seçildi",
    "10.8947% of test": "testin %10,8947'si",
    "Precision 0.735099": "Kesinlik 0.735099",
    "Recall 0.203857": "Duyarlılık 0.203857",
    "2,772-row 2011-09-01 holdout · 95% PR-AUC CI [0.618131, 0.678937].": "2.772 satırlı 2011-09-01 bekletmesi · %95 PR-AUC GA [0.618131, 0.678937].",
    "EXPLAINABILITY AND RESPONSIBLE AI": "AÇIKLANABİLİRLİK VE SORUMLU YAPAY ZEKÂ",
    "A score can inform review, but it never authorizes an action": "Puan incelemeyi besler, ancak eyleme asla yetki vermez",
    "Validated explanation": "Doğrulanmış açıklama",
    "Maximum SHAP additivity error": "Azami SHAP toplamsallık hatası",
    "8.88 × 10⁻¹⁶ in calibrated log-odds": "Kalibre log-olasılıkta 8,88 × 10⁻¹⁶",
    "Current consent": "Güncel rıza",
    "Eligible audience snapshot": "Uygun kitle anlık görüntüsü",
    "Authorized reviewer": "Yetkili inceleyen",
    "Explicit approval": "Açık onay",
    "Kill switch + budget cap": "Acil durdurma + bütçe sınırı",
    "SHAP explains fitted score formation — not why a customer behaves or what will change them.": "SHAP, puanın oluşumunu açıklar; müşteri davranışının nedenini veya neyin değiştireceğini değil.",
    "Project explanation artifact and implemented consent/approval controls.": "Proje açıklama eseri ve uygulanmış rıza/onay denetimleri.",
    "PROJECT LEAD DECISION": "PROJE LİDERİ KARARI",
    "Local evidence is ready; production proof remains external": "Yerel kanıt hazır; üretim kanıtı dış doğrulamada bekliyor",
    "Completed locally": "Yerelde tamamlandı",
    "✓  Tenant-safe CRM / commerce / imports": "✓  Kiracı güvenli CRM / ticaret / içe aktarma",
    "✓  Versioned analytics and model registry": "✓  Sürümlü analitik ve model kaydı",
    "✓  Audiences, approvals and audit trail": "✓  Kitleler, onaylar ve denetim izi",
    "✓  Written assignments + final presentation": "✓  Yazılı ödevler + final sunumu",
    "External validation still required": "Dış doğrulama hâlâ gerekli",
    "○  Live Meta / Google / LLM / OIDC sandboxes": "○  Canlı Meta / Google / LLM / OIDC test ortamları",
    "○  Browser accessibility and load validation": "○  Tarayıcı erişilebilirlik ve yük doğrulaması",
    "○  Managed backup / restore rehearsal": "○  Yönetilen yedekleme / geri yükleme provası",
    "○  Randomized pilot for incremental impact": "○  Ek etki için rastgeleleştirilmiş pilot",
    "Decision requested: audit the local package. Publication, deployment and live spend remain separately gated.": "İstenen karar: yerel paketi denetleyin. Yayın, dağıtım ve canlı harcama ayrı onaya bağlıdır.",
    "No push · no paid deployment · no live advertising spend.": "Ücretli dağıtım veya canlı reklam harcaması yapılmadı.",
    "Random forest": "Rastgele orman",
    "Recency": "Yakınlık",
    "Dummy": "Kukla",
    "Logistic": "Lojistik",
}


def main() -> None:
    with zipfile.ZipFile(PPTX, "r") as source:
        members = [(info, source.read(info.filename)) for info in source.infolist()]
    changed: set[str] = set()
    existing: set[str] = set()
    with tempfile.NamedTemporaryFile(dir=PPTX.parent, suffix=".pptx", delete=False) as tmp:
        tmp_path = Path(tmp.name)
    try:
        with zipfile.ZipFile(tmp_path, "w") as target:
            for info, data in members:
                if info.filename.startswith("ppt/slides/") and info.filename.endswith(".xml"):
                    root = ET.fromstring(data)
                    for tag in (f"{{{NS_A}}}t", f"{{{NS_C}}}v"):
                        for node in root.iter(tag):
                            if node.text:
                                existing.add(node.text)
                            if node.text in TRANSLATIONS:
                                changed.add(node.text)
                                node.text = TRANSLATIONS[node.text]
                    data = ET.tostring(root, encoding="utf-8", xml_declaration=True)
                target.writestr(info, data)
        missing = {
            source
            for source, translated in TRANSLATIONS.items()
            if source not in changed and translated not in existing
        }
        if missing:
            raise RuntimeError(f"Sunumda bulunmayan çeviri anahtarları: {sorted(missing)}")
        os.replace(tmp_path, PPTX)
    finally:
        tmp_path.unlink(missing_ok=True)
    print(f"Türkçeleştirilen sunum metni: {len(changed)}")


if __name__ == "__main__":
    main()
