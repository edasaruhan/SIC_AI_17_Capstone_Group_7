# Literatür, Veri ve Teknoloji Çalışması

Denetimli bir perakende müşteri kaybı karar sistemi için kanıta dayalı araştırma temeli

**YAPAY ZEKA KULLANIM BEYANI:** Bu belge OpenAI Codex/ChatGPT desteğiyle hazırlanmış ve depo kanıtlarıyla kontrol edilmiştir. İnsan incelemesi gereklidir.

## Yönetici özeti

GrowthPilot AI, küçük perakende ekiplerindeki dağınık müşteri, sipariş, ürün, stok ve reklam verilerini birleştirerek geç, açıklanması güç ve denetlenemeyen müşteriyi elde tutma kararlarını iyileştirmeyi amaçlar. İlk denetimli öğrenme problemi, sözleşmesiz perakendede 90 günlük gelecekte satın alma hareketsizliğidir. Bu bir tahmindir; kalıcı müşteri kaybını veya bir müdahalenin nedensel etkisini kanıtlamaz.

Araştırma dört yöntemi destekler: sonucu operasyonel tanımlamak, kronolojik gözlem/sonuç pencereleri kullanmak, karmaşık modellerden önce şeffaf temel yöntemleri karşılaştırmak ve yalnız doğruluk yerine olasılık kalitesi ile kapasite kısıtlı sıralamayı ölçmek. UCI Online Retail II iki yıllık geçmişi nedeniyle seçilmiştir. Teknoloji yığını veri kaynağını, kiracı yalıtımını, model sürümlemeyi, rızayı ve insan onayını denetlenebilir tek akışta tutar.

## Bölüm I — Literatür taraması

### 1. Problem ve araştırma sorusu

Sözleşmeli hizmetlerde iptal müşteri kaybını gösterebilir. Sözleşmesiz perakendede sessizlik belirsizdir: müşteri iki satın alma arasında, mevsimsel olarak pasif veya kalıcı biçimde kaybedilmiş olabilir. Araştırma sorusu şudur: Kesim tarihinden önceki işlem davranışı, sabit 90 günlük gelecek penceresinde uygun satın alma yapmayacak müşterileri; kalibrasyon, açıklanabilirlik ve yönetişimli pazarlama kullanımını koruyarak ne kadar doğru ve yararlı belirleyebilir?

### 2. Müşteri durumu örtüktür

Jerath, Fader ve Hardie (2011), müşteri “ölümü” modellerinin kayıp zamanına ilişkin farklı varsayımlar içerdiğini gösterir. Pareto/NBD kaybı takvim zamanında, BG/NBD ise işlem zamanında ele alır. Dolayısıyla müşteri durumu gözlenebilir bir olgudan çok model varsayımlarına bağlıdır. Batislam, Denizel ve Filiztekin (2007) de market işlemlerinde Pareto/NBD ve BG/NBD'yi karşılaştırıp aktif durum ile gelecekte satın almayı ayrı hedefler olarak inceler.

Platzer ve Reutterer (2016), satın alma düzenliliğini sözleşmesiz müşteri tabanı modellerine ekler. Belleksiz bir kural dönemsel satın alan kişiyi yanlışlıkla pasif sayabilir. GrowthPilot bu nedenle yakınlık, sıklık, müşteri yaşı ve satın almalar arası süre özelliklerini kullanır; hedefi “gerçek kayıp” değil, “gelecekte hareketsizlik” olarak adlandırır.

### 3. Değerlendirme pazarlama kararıyla uyumlu olmalıdır

Her müşteriyle iletişim kurulamayacağından değerlendirme hem ayırt ediciliği hem operasyon politikasını kapsar. Yaygınlık zamanla değiştiği için PR-AUC birincil, ROC-AUC ikincil sıralama ölçütüdür. Brier, log kaybı ve ECE olasılık kalitesini; en riskli %5, %10 ve %20'de kesinlik, duyarlılık ve artış erişim kapasitesini ölçer.

Operasyon eşiği ayrı kalibrasyon döneminde yaklaşık %10 kapasiteye göre seçilip dondurulmuştur. Böylece nihai testte eşik seçimi yapılmamıştır. Kampanya etkisi için rastgeleleştirilmiş veya güvenilir yarı deneysel tasarım gerekir; tahmine dayalı artış nedensel etki değildir.

### 4. Açıklanabilirlik ve yönetişim

Lojistik katsayılar ve SHAP ayrıştırmaları modelin puanı nasıl oluşturduğunu açıklar; bir özelliği değiştirmenin davranışı değiştireceğini göstermez. GrowthPilot model, özellik, hedef ve veri bölümü sürümlerini, sağlama toplamlarını ve açıklamaları saklar. Öneriler güncel rıza, amaç, rol, onay, acil durdurma anahtarı ve bütçe sınırıyla kısıtlanır.

### 5. Karşılaştırmalı sentez

| Kaynak | Amaç / yöntem | Kullanılan bulgu | Sınırlılık |
| --- | --- | --- | --- |
| Jerath, Fader ve Hardie (2011) | Sözleşmesiz müşteri kaybı; PDO, Pareto/NBD, BG/NBD | Kayıp zamanı varsayımları ölçütleri değiştirir | Denetimli kampanya etkisi çalışması değildir |
| Batislam ve diğerleri (2007) | Market verisinde Pareto/NBD ve BG/NBD | Aktif durum ve gelecekte satın alma doğrulanmalıdır | Bağlam aktarılabilirliği garanti etmez |
| Platzer ve Reutterer (2016) | Satın alma düzenliliği uzantısı | Dönemsellik modellemeyi geliştirebilir | Örtük durum modele bağlıdır |
| Saito ve Rehmsmeier (2015) | Dengesiz sınıflandırmada ROC ve PR | Dengesiz pozitif sınıfta PR bilgilendiricidir | Perakendeye özgü değildir |
| Lundberg ve Lee (2017) | Toplamsal özellik katkısı | Model açıklamaları toplamsal doğrulanabilir | Açıklama nedensellik değildir |



Kanıt sınıfı: dış kaynak sentezi. GrowthPilot performans sonucu ileri sürülmemektedir.

### 6. Pazarlama boşluğu ve katkı

İhtiyaç başka bir bağımsız müşteri kaybı not defteri değil; ham kayıttan insan kararına uzanan izlenebilir bir yoldur: standart veri, sürümlü özellikler, dürüst olasılıklar, rızaya duyarlı önceliklendirme ve onay kapısı. GrowthPilot bütünleşik uygulama ile yeniden üretilebilir değerlendirme sunar; tek tarihsel Birleşik Krallık perakendecisinin tüm pazarları temsil ettiğini, hareketsizliğin kalıcı kayıp olduğunu veya hedefli iletişimin gelir yarattığını iddia etmez.

### 7. Literatür sonucu

Literatür ihtiyatlı etiket/değerlendirme tasarımını, satın alma ritmi özelliklerini ve tahmin, açıklama ile nedensel etkinliğin ayrılmasını destekler. Bunlar hedef notu, zamansal bölme, model kartı ve korumalı pazarlama akışına işlenmiştir.

## Bölüm II — Veri araştırması

### 1. Amaç ve gereksinimler

Veri, kesim öncesi müşteri geçmişini ve sonrasında tam gözlenen sonucu desteklemelidir. Gerekli alanlar müşteri, işlem/fatura ve ürün kimliği; zaman, miktar ve fiyattır. İptal, ülke ve açıklama kalite kontrolüne yardım eder. Reklam verisi ilk modeli eğitmek için değil, sonraki atıf ve etkinleştirme akışları için gerekir.

### 2. Aday değerlendirmesi

| Veri kümesi | Kapsam / erişim | Uygunluk | Karar |
| --- | --- | --- | --- |
| UCI Online Retail II | 1.067.371 satır; 2009-12-01–2011-12-09; XLSX; CC BY 4.0; DOI 10.24432/C5CG6D | İki yıl ve birden çok zamansal kesim | Seçildi |
| UCI Online Retail | 541.909 satır; yaklaşık bir yıl; CC BY 4.0; DOI 10.24432/C5BW33 | Aynı perakendeci, daha kısa geçmiş | Elendi |
| Online Shoppers Purchasing Intention | 12.330 oturum; CC BY 4.0; DOI 10.24432/C5F88Q | Oturum dönüşümü; müşteri hareketsizliği değil | Elendi |



Kaynaklar: UCI kayıtları ve depo veri kümesi karar notu.

### 3. Seçilen kaynak profili

| Boyut | Projede yeniden üretilen değer |
| --- | --- |
| Ham boyut | 1.067.371 satır; 8 alan; 43 ülke |
| Dönem | 2009-12-01–2011-12-09 |
| Müşteriler / faturalar | 5.942 tanımlı müşteri; 53.628 fatura |
| Eksiklik | Müşteri kimliği eksik 243.007; açıklama eksik 4.382 satır |
| Aykırılıklar | 19.494 iptal; 22.950 pozitif olmayan miktar; 6.207 pozitif olmayan fiyat |
| Yinelenenler | Birebir aynı 34.335 satır |
| Uygun satın alma | 805.549 satır; 37.033 olay; 5.878 müşteri |



Kanıt sınıfı: dış kaynaktan projede yeniden üretilmiştir. Değerleri scripts/profile_dataset.py üretir.

### 4. Kalite, gizlilik ve sınırlılıklar

- Ham veri sağlama toplamıyla doğrulanır ve Git dışında tutulur; kaynak URL, DOI, lisans, boyut ve SHA-256 kaydedilir.

- Modelleme birebir yinelenenleri, kullanılamayan kimlik/tarihleri, iptalleri ve pozitif olmayan satın alma satırlarını uygun olaylardan çıkarır; ham kanıtı değiştirmez.

- Takma adlı müşteri kimlikleri ilişkilendirilebilir veri sayılır. Müşteri düzeyi dosyalar yerelde ve Git dışında; akademik çıktılar topludur.

- Kaynak tarihsel, tek perakendecili, Birleşik Krallık merkezli ve kısmen toptandır. Eksik kimlik ve sansürleme temsil gücünü sınırlar.

### 5. Keşifsel kanıt ve pazarlama içgörüsü

![Şekil 1. Eğitim anlık görüntülerinde hareketsizlik yaygınlığı ve yakınlık. Projede üretilen kanıt.](../../artifacts/eda/training_label_recency.png)

*Şekil 1. Eğitim anlık görüntülerinde hareketsizlik yaygınlığı ve yakınlık. Projede üretilen kanıt.*

![Şekil 2. Eğitim anlık görüntülerinde sıklık ve harcama. Projede üretilen kanıt.](../../artifacts/eda/training_frequency_spend.png)

*Şekil 2. Eğitim anlık görüntülerinde sıklık ve harcama. Projede üretilen kanıt.*

Tanımlı satın alma müşterisi başına medyan satın alma sayısı 3; satın almalar arası sürenin medyanı 24,197 gün, %75'lik dilimi 61,194 gündür. Bunlar 90 günlük pencereyi uygulanabilir bir hareketsizlik ufku olarak destekler, kalıcı kaybı kanıtlamaz. Çarpık dağılımlar log dönüşümü ve sağlam değerlendirmeyi destekler.

### 6. Veri sonucu

Online Retail II yeniden üretilebilir zamansal sınıflandırma için yeterli, evrensel kayıp veya kampanya nedenselliği için yetersizdir. Üretim kullanımı kiracıya ait, rıza yönetimli güncel veri ve yeni sapma/kalite doğrulaması gerektirir.

## Bölüm III — Teknoloji incelemesi

### 1. Amaç ve pazarlama ilgisi

Teknoloji müşteri operasyonlarını ve denetlenebilir zekâyı aynı üründe desteklemelidir. Öncelik algoritmik karmaşıklık değil; güvenilir içe aktarma, standart tanımlar, yeniden üretilebilir eğitim/çıkarım, kiracı yalıtımı, açıklama ve denetimli eylemdir.

### 2. Karşılaştırma

| Alan | Seçilen teknoloji | Neden | Ödünleşim / kontrol |
| --- | --- | --- | --- |
| API/alan | Python 3.12, FastAPI, Pydantic, SQLAlchemy | Tür kontrollü doğrulama, OpenAPI, ML ekosistemi | Modüler tek parça ve katı tür disiplini |
| Veri/kiracılık | PostgreSQL RLS | İşlem, kısıt, analitik, satır politikası | Uygulama kapsam testleri yine gerekir |
| Web | Next.js, React, katı TypeScript | Sunucu işleme ve tür kontrollü sınırlar | Otomasyon geçer; manuel tarayıcı/yardımcı teknoloji incelemesi bekler |
| İşler | Redis, Dramatiq, işlemsel outbox | Kalıcı ve yeniden denemeli işler | İzleme ve yönetilen Redis gerekir |
| Modelleme | scikit-learn + LightGBM | Şeffaf hat ve doğrusal olmayan aday | Doğrulama lojistik regresyonu seçti |
| İzleme | MLflow | Çalıştırma, parametre, ölçüt ve eser kaynağı | Yerel kayıt üretim hizmeti değildir |
| Açıklama | SHAP + katsayılar | Yerel/küresel puan ayrıştırması | Nedensel değildir |
| Dağıtım | Kapsayıcılar + Terraform AWS | Taşınabilir sınır | Ücretli bulut ve geri yükleme testleri bekler |



Performans ve maliyet değerlendirmeleri kıyaslama iddiası değildir; canlı sağlayıcı gecikmesi/maliyeti ölçülmemiştir.

### 3. Sektör örnekleri ve kullanım alanları

| Harici örnek | Uygulama ve yayımlanan vaka sonucu | GrowthPilot için ders |
| --- | --- | --- |
| Salesforce / Grammarly | Account Engagement ve Einstein puanlaması satışa hazır adayları önceliklendirir. Salesforce müşteri hikâyesinde Grammarly, MQL dönüşümünde %30 artış ve satış döngüsünün 60–90 günden 30 güne kısaldığını bildirmiştir | Puan açıklamayla iş akışında olmalıdır; sonuç, sağlayıcının yayımladığı tek müşteri vakasıdır ve GrowthPilot kanıtı değildir |
| Google Ads / Aritaum | Aritaum'un Kore'deki 30 günlük deneyinde aynı ürün akışıyla Smart Shopping'in dönüşüm değeri optimizasyonu standart eCPC kampanyasıyla karşılaştırılmıştır. Think with Google vakası 2,2 kat ROAS ve %400 daha fazla dönüşüm bildirmiştir | Optimizasyon ölçüm ve sağlayıcı verisine bağlıdır; yayımlanan vaka bağımsız doğrulama veya GrowthPilot sonucu değildir |



Rakamlar sağlayıcıların yayımladığı dış kaynak müşteri/vaka anlatılarıdır; bağımsız olarak yeniden üretilmiş sonuçlar, genellenebilir etki tahminleri veya GrowthPilot iş sonucu değildir.

#### GrowthPilot uygulaması

- Müşteri 360: sipariş, değer, RFM, tahmin ve rıza tek kiracı görünümünde.

- Kapasiteye duyarlı elde tutma: risk ve ticari öneme göre sıralama, ardından zorunlu onay.

- Operasyonel analitik: sürümlü ölçütler ve veri yoksa açık boş durumlar.

- Sağlayıcıdan bağımsız alım: sabit kökenli bağdaştırıcılarla ham yük kaynağı ve standart günlük gerçekler.

### 4. Sınırlılıklar ve fırsatlar

Canlı Meta, Google Ads, OIDC, LLM veya bulut kimlik bilgileri yoktur; sınırlar uygulanıp taklitle test edilmiş, canlı doğrulanmamıştır. Yerel MLflow ve tek tarihsel veri kümesi üretim sağlamlığını kanıtlamaz. Sonraki işler kimlik bilgili test ortamı, yük/dayanıklılık, manuel tarayıcı/yardımcı teknoloji, yedekleme/geri yükleme ve gerçek veriye dayalı izleme doğrulamasıdır.

### 5. Teknoloji sonucu

Yığın, kanıt işlem hattını ürün denetimlerinden ayırmadan yeniden üretilebilirlik sağlar. Bu üretime yönelik yerel uygulamadır, üretim dağıtımı değildir.

## Kaynakça

Batislam, E. P., Denizel, M., & Filiztekin, A. (2007). Empirical validation and comparison of models for customer base analysis. International Journal of Research in Marketing, 24(3), 201–209. https://doi.org/10.1016/j.ijresmar.2006.12.005

Chen, D. (2012). Online Retail II [Veri kümesi]. UCI Machine Learning Repository. https://doi.org/10.24432/C5CG6D

Jerath, K., Fader, P. S., & Hardie, B. G. S. (2011). New perspectives on customer “death” using a generalization of the Pareto/NBD model. Marketing Science, 30(5), 866–880. https://doi.org/10.1287/mksc.1110.0654

Lundberg, S. M., & Lee, S.-I. (2017). A unified approach to interpreting model predictions. Advances in Neural Information Processing Systems, 30. https://arxiv.org/abs/1705.07874

Platzer, M., & Reutterer, T. (2016). Ticking away the moments: Timing regularity helps to better predict customer activity. Marketing Science, 35(5), 779–799. https://doi.org/10.1287/mksc.2015.0963

Saito, T., & Rehmsmeier, M. (2015). The precision-recall plot is more informative than the ROC plot when evaluating binary classifiers on imbalanced datasets. PLOS ONE, 10(3), e0118432. https://doi.org/10.1371/journal.pone.0118432

Salesforce. (t.y.). Einstein Lead Scoring. Salesforce Help. https://help.salesforce.com/s/articleView?id=einstein_sales_lead_insights.htm&language=en_US. Erişim: 11 Eylül 2026.

Salesforce. (t.y.). Grammarly increases plan upgrades by 80% with sales and marketing AI. https://www.salesforce.com/customer-stories/grammarly-lead-scoring-ai/. Erişim: 13 Eylül 2026.

Google Ads Help. (t.y.). About Smart Bidding. https://support.google.com/google-ads/answer/7065882?hl=en. Erişim: 11 Eylül 2026.

Think with Google. (t.y.). Experiment: How Aritaum lifted conversions with Smart Shopping campaigns. https://www.thinkwithgoogle.com/_qs/documents/11638/Experiment_-_How_Aritaum_lifted_conversions_with_Smart_Shopping_campaigns.pdf. Erişim: 13 Eylül 2026.

Teknoloji belgeleri: PostgreSQL satır güvenliği; scikit-learn değerlendirme/kalibrasyon; LightGBM Python API; SHAP; MLflow; FastAPI güvenliği; Next.js App Router. URL'ler depo ADR'lerinde ve araştırma notlarında kayıtlıdır.
