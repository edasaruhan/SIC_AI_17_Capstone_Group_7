# Model İyileştirme ve Test Çalışması

Dondurulmuş, kalibre edilmiş lojistik müşteri kaybı vekil adayı ve dokunulmamış zamansal değerlendirme

**YAPAY ZEKA KULLANIM BEYANI:** Bu belge OpenAI Codex/ChatGPT desteğiyle hazırlanmış ve depo kanıtlarıyla kontrol edilmiştir. İnsan incelemesi gereklidir.

## Bölüm I — Model iyileştirme

### 1. İlk değerlendirme ve zayıflıklar

İlk keşif lojistik regresyonu doğrulama PR-AUC 0.805322 ile seçti. Zayıflıkları olasılık kalibrasyonu (Brier 0.213300; ECE 0.169377) ve düzenlileştirme duyarlılığıydı. LightGBM PR-AUC'de çok yakındı ve ham kalibrasyonu daha iyiydi; bu nedenle iyileştirme, birincil seçim kuralını değiştirmeden üç öğrenilmiş aileyi karşılaştırdı.

### 2. İyileştirme teknikleri

- Lojistik ızgara: C ∈ {0.01, 0.05, 0.2, 1.0, 5.0}; sıralama, kalibrasyon ve kapasite doğrudan ölçüldüğünden sınıf ağırlığı kapalı tutuldu.

- Rastgele orman ızgarası: 400 ağaç, asgari yaprak {5,10,20}, azami derinlik {8,16}.

- LightGBM: öğrenme oranı, yaprak, derinlik, asgari alt örnek, L2, satır ve sütun alt örneklemesinde 12 tohumlu deneme.

- Sigmoid kalibrasyon yalnız 2011-06-01 anlık görüntüsünde uyarlandı.

- Operasyon eşiği yaklaşık %10 kalibrasyon kapasitesinde 0.812509305136 olarak sabitlendi.

### 3. Ayarlamanın etkisi

| Aşama | PR-AUC | ROC-AUC | Brier | ECE | İlk %10 kesinlik / artış |
| --- | --- | --- | --- | --- | --- |
| İlk lojistik doğrulama | 0.805322 | 0.782819 | 0.213300 | 0.169377 | 0.871642 / 1.510154 |
| İyileştirilmiş lojistik C=.01 | 0.812223 | 0.787127 | 0.196710 | 0.106133 | 0.883582 / 1.530841 |
| Kalibrasyon uyumu, betimsel | 0.739014 | 0.773722 | 0.193632 | 0.040863 | 0.834586 / 1.671058 |



Kalibrasyon ölçütleri aynı kalibrasyon etiketlerini yeniden kullandığından betimseldir, tarafsız test tahmini değildir.

C değerinin 1.0'dan 0.01'e indirilmesi PR-AUC'yi 0.812223'e çıkarıp Brier'ı 0.196710'a düşürdü. Sonraki bölümde sigmoid kalibrasyon ECE'yi betimsel olarak 0.040863'e düşürdü. Seri hâle getirilmiş adayın sağlama toplamı 942d705d66a9469d57494626a99da83c91a9a895a3a2b2d7e977ff3ba56952ad'dir.

### 4. Çapraz doğrulama ve özellik seçimi

Rastgele k-katlı doğrulama, gelecek/geçmiş anlık görüntülerini ve tekrarlanan müşterileri karıştıracağı için kullanılmadı. Bunun yerine genişleyen kronolojik eğitim kesimleri ile ayrı doğrulama, kalibrasyon ve nihai test tarihleri kullanıldı. Test sonrası özellik seçimi yapılmadı: düzenlileştirilmiş lojistik hat katsayı büyüklüğünü sınırlar; testi gördükten sonra özellik kaldırmak dondurma kuralını ihlal eder.

### 5. Açıklanabilirlik doğrulaması

![Şekil 1. Kalibre log-olasılıkta küresel ortalama mutlak SHAP katkısı. Projede üretilen tanı.](../../artifacts/ml/explanations_global.png)

*Şekil 1. Kalibre log-olasılıkta küresel ortalama mutlak SHAP katkısı. Projede üretilen tanı.*

SHAP ayrıştırması dondurulmuş lojistik hat için kalibre log-olasılıkta hesaplandı. Azami toplamsallık hatası 8.881784197001252×10⁻¹⁶ olup sayısal tutarlılığı doğrular. Katkılar model puanını açıklar; nedensel etki değildir ve desteklenmeyen kişisel iddialara dönüştürülemez.

## Bölüm II — Nihai test

### 1. Test hazırlığı ve bütünlük

Nihai test, 2011-09-01 kesiminde tamamen gözlenen 90 günlük etiket penceresine sahip 2.772 müşteridir. Hazırlanmış dosyanın SHA-256 değeri 2830e4738acfee8c5561f5eb513874d0cacae32f3b3095c412db62dc2cf78ff6'dır. Erişimden önce aday bildirimi, ön işleme, kalibratör, sağlama toplamı ve eşik donduruldu. Test sonrası yeniden ayar yasaktır.

### 2. Model uygulaması

```python
bundle = joblib.load('artifacts/models/final_candidate.joblib')
assert sha256_file(model_path) == EXPECTED_MODEL_SHA256
scores = bundle['calibrated_model'].predict_proba(X_test)[:, 1]
predicted = scores >= 0.812509305136
# Hedef, özellik ve bölme sürümleri raporlamadan önce denetlenir.
```

### 3. Nihai test ölçütleri

| Ölçüt | Nihai test sonucu | %95 bootstrap aralığı |
| --- | --- | --- |
| Satır / yaygınlık | 2.772 / 0.392857 | Uygulanamaz |
| PR-AUC | 0.647525 | [0.618131, 0.678937] |
| ROC-AUC | 0.765878 | [0.748534, 0.782761] |
| Brier skoru | 0.199854 | [0.192598, 0.207125] |
| Log kaybı | 0.582761 | Bootstrap uygulanmadı |
| ECE (10 kutu) | 0.095054 | Bootstrap uygulanmadı |
| İlk %10 kesinlik / duyarlılık / artış | 0.748201 / 0.191001 / 1.904513 | Bootstrap uygulanmadı |



Kanıt sınıfı: projede yürütülen, dokunulmamış zamansal bekletme. Aralıklar bu kesim için parametrik olmayan satır bootstrap aralıklarıdır.

![Şekil 2. Nihai zamansal testte kesinlik–duyarlılık ve olasılık kalibrasyonu.](../../artifacts/ml/final_evaluation.png)

*Şekil 2. Nihai zamansal testte kesinlik–duyarlılık ve olasılık kalibrasyonu.*

### 4. Dondurulmuş eşik karışıklık matrisi

| Gerçek / tahmin | Aktif tahmini | Hareketsiz tahmini |
| --- | --- | --- |
| Gerçekte aktif | TN = 1.603 | FP = 80 |
| Gerçekte hareketsiz | FN = 867 | TP = 222 |



0.812509305136 eşiği 302 müşteriyi (%10,8947) seçti: kesinlik 0.735099, duyarlılık 0.203857, F1 0.319195.

### 5. Doğrulamadan teste karşılaştırma

| Bölüm | PR-AUC | ROC-AUC | Brier | Yaygınlık | Yorum |
| --- | --- | --- | --- | --- | --- |
| Doğrulama | 0.812223 | 0.787127 | 0.196710 | 0.577187 | Aile/ayar seçimi |
| Kalibrasyon | 0.739014 | 0.773722 | 0.193632 | 0.499436 | Sigmoid ve eşik; betimsel |
| Nihai test | 0.647525 | 0.765878 | 0.199854 | 0.392857 | Tek dokunulmamış zamansal bekletme |



PR-AUC 0.812223'ten 0.647525'e, yaygınlık 0.577187'den 0.392857'ye iner. ROC-AUC 0.765878 kalırken ilk %10 artış 1.904513'e çıkar. Fark, dondurulmuş sonucu değiştirme gerekçesi değil, zamansal/veri kayması ve belirsizlik kanıtıdır.

### 6. Dağıtımın gerçek durumu

Eser yerelde growthpilot-churn-inactivity sürüm 1 ve champion takma adıyla kayıtlı, kiracı kapsamlı istek üzerine ve kalıcı toplu puanlamaya bağlıdır. “Champion” yerel kayıt takma adıdır, üretim dağıtımı kanıtı değildir. İstek üzerine puanlama demo kapılıdır; canlı bulut, kiracı verisi sapması ve hizmet düzeyi doğrulanmamıştır. Hiçbir puan eylem yetkisi vermez.

### 7. Sonuç

Dondurulmuş model tarihsel testte, özellikle sınırlı erişim kapasitesinde yararlı sıralama sinyali verir; ancak katı eşikte çoğu hareketsiz müşteriyi kaçırır. İnsan kararını desteklemeli, yerine geçmemelidir. Üretim için güncel kiracı verisi, hukuka uygun kullanım, kalibrasyon/sapma izleme ve nedensel kampanya değerlendirmesi gerekir.

## Kaynakça ve kanıt

scikit-learn geliştiricileri. Olasılık kalibrasyonu ve model değerlendirme belgeleri. https://scikit-learn.org/stable/modules/calibration.html

Lundberg, S. M., & Lee, S.-I. (2017). A unified approach to interpreting model predictions. NeurIPS 30. https://arxiv.org/abs/1705.07874

Proje kanıtları: artifacts/ml/final_candidate.json, final_evaluation.json/png, explanations.json/png, model_registry.json; scripts/refine_model.py, evaluate_final.py, explain_model.py ve register_model.py.
