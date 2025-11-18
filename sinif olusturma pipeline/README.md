# 🎓 Sınıf Oluşturma Pipeline Sistemi

Bu depo, yurtdışı öğrencilerin sınıflandırılması ve çıktıların (Excel/CSV) hazırlanması için adım adım çalışan bir Python pipeline'ıdır.

---

## 📋 İçindekiler

1. [Sistem Özeti](#sistem-özeti)
2. [Kurulum](#kurulum)
3. [Pipeline Adımları](#pipeline-adımları)
4. [Dosya Açıklamaları](#dosya-açıklamaları)
5. [Çıktı Dosyaları](#çıktı-dosyaları)
6. [İletişim & Sorun Giderme](#iletisim--sorun-giderme)

---

## 🎯 Sistem Özeti

Pipeline şu işleri otomatikleştirir:

- Sahte öğrenci verisi üretme
- İlk sınıf gruplandırması
- Küçük sınıfları birleştirme
- Çok büyük sınıfları bölme ve kodlama
- Ders saatlerini Türkiye saatine çevirme
- CSV dışarı aktarma (Moodle vb. için)

Öğretmen atama işlevi bu repoda bir Python scripti yerine küçük bir web uygulaması (HTML/JS/CSS) olarak sağlanmaktadır. Repoda bulunan `05-ogretmenlere ders atamasinin yapilmasi.txt` dosyası, uygulamanın GitHub Pages adresine işaret eden bir bağlantı içerir; uygulama şu adreste bulunur:

`https://ulkemyanimda.github.io/araclar/ogretmenderseslestirme/index.html`

Kullanım seçenekleri:
- Uygulamayı doğrudan bağlantıdan açarak online kullanabilirsiniz.
- Ya da repodaki `05-ogretmenlere ders atamasinin yapilmasi.txt` içeriğini `.html` dosyası olarak kaydedip yerel tarayıcıda (çift tıklayarak) açabilirsiniz.

README'nin ilgili adımlarında bu web uygulamasına atıf yapılmıştır; eğer uygulamayı farklı bir lokasyona taşırsanız veya kendi sunucunuzda barındıracaksanız linkleri güncelleyin.

---

## 💾 Kurulum

### Gereksinimler

- Python 3.7+
- `pandas`, `openpyxl`, `tabulate`

### Kütüphanelerin Yüklenmesi

```powershell
pip install pandas openpyxl tabulate
```

---

## 🔄 Pipeline Adımları

Sıralı olarak çalıştırılacak ana adımlar:

### 1) Sahte Veri Oluşturma
`00-fake_data_creator.py`

Çalıştırma:
```powershell
python "00-fake_data_creator.py"
```

Çıktı: `Kullanıcılar.xlsx` (ör. isim, e-posta, ülke, ders saati, seviye)

---

### 2) İlk Sınıf Oluşturma
`01-Sinif-olusturma-pipeline.py`

Çalıştırma:
```powershell
python "01-Sinif-olusturma-pipeline.py"
```

Çıktı: `Siniflar/` içindeki Excel dosyaları

---

### 3) Yetersiz Mevcutlu Sınıfları Birleştirme
`02-yerlestirilemeyen ogrencileri uygun siniflara atar.py`

Çalıştırma:
```powershell
python "02-yerlestirilemeyen ogrencileri uygun siniflara atar.py"
```

Çıktı: Güncellenmiş `Siniflar/` ve `*_raporu_*.txt`

---

### 4) Sınıf Bölme ve Kodlama
`03-ogrencileri siniflara boler-sinif kodlarini olusturur.py`

Çalıştırma:
```powershell
python "03-ogrencileri siniflara boler-sinif kodlarini olusturur.py"
```

Çıktı: `YeniSiniflar/` ve `sinif_bolme_raporu_*.txt`

---

### 5) Ders Saatlerini Türkiye Saatine Çevirme
`04-Ders satlerinin TR ye cevrilmesi.py`

Çalıştırma:
```powershell
python "04-Ders satlerinin TR ye cevrilmesi.py"
```

Çıktı: `ogrenciler.xlsx`, `Veriler.xlsx`

---


### 6) Öğretmen Ataması (Web Uygulaması)
`05-ogretmenlere ders atamasinin yapilmasi.txt` (web uygulama bağlantısı)

Bu adım için repoda bir Python scripti bulunmamaktadır; öğretmen-öğrenci eşleştirmesi, repodaki web uygulaması ile yapılır. Uygulamayı açtıktan sonra kaynak olarak `YeniSiniflar/` ve `ogrenciler.xlsx` dosyalarını kullanarak atama yapabilirsiniz. Uygulama, öğretmen müsaitliklerini ve ders saatlerini okuyup uygun eşleştirmeyi sağlar.

Kullanım:
1. Tarayıcıdan `https://ulkemyanimda.github.io/araclar/ogretmenderseslestirme/index.html` adresini açın
2. Varsa `ogrenciler.xlsx` veya `YeniSiniflar/` çıktılarınızı uygulamaya yükleyin (uygulama destekliyorsa)
3. Atama sonuçlarını dışa aktarın veya kopyalayın

---

### 7) CSV Dışarı Aktarma
`06-ders ve ogrenci csv dosyalari.py`

Not: Bu adım `YeniSiniflar/` ve `ogrenciler.xlsx` gibi kaynakları kullanır; web uygulaması ile üretilen atama çıktılarınızı burada girdi olarak kullanabilirsiniz. Script içindeki giriş dosyalarını kontrol edin.

Çalıştırma:
```powershell
python "06-ders ve ogrenci csv dosyalari.py"
```

Çıktı: `dersler.csv`, `ogrenciler.csv`

---

## 📁 Dosya Açıklamaları

| Dosya | Amaç | Giriş | Çıktı |
|-------|------|-------|-------|
| `00-fake_data_creator.py` | Sahte öğrenci verisi oluşturma | (opsiyonel) `adsoyad.xlsx` | `Kullanıcılar.xlsx` |
| `01-Sinif-olusturma-pipeline.py` | İlk gruplandırma | `Kullanıcılar.xlsx` | `Siniflar/*.xlsx` |
| `02-yerlestirilemeyen ogrencileri uygun siniflara atar.py` | Küçük sınıfları birleştir | `Siniflar/*.xlsx` | `Siniflar/*.xlsx` + rapor |
| `03-ogrencileri siniflara boler-sinif kodlarini olusturur.py` | Bölme ve kodlama | `Siniflar/*.xlsx` | `YeniSiniflar/*.xlsx` + rapor |
| `04-Ders satlerinin TR ye cevrilmesi.py` | Ders saatlerini TR'ye çevirme | `YeniSiniflar/*.xlsx` | `ogrenciler.xlsx`, `Veriler.xlsx` |
| `06-ders ve ogrenci csv dosyalari.py` | CSV dışarı aktarma | `YeniSiniflar/*.xlsx`, `ogrenciler.xlsx` | `dersler.csv`, `ogrenciler.csv` |
| `05-ogretmenlere ders atamasinin yapilmasi.txt` | Öğretmen-öğrenci eşleştirmesi (web uygulama bağlantısı) | (tarayıcı) `ogrenciler.xlsx`, `YeniSiniflar/` | Atama sonuçlarını dışa aktarılabilir formatta sunar |

---

## 📊 Örnek Klasör Yapısı ve Çıktılar

```
sinif olusturma pipeline/
├── Siniflar/
├── YeniSiniflar/
├── Kullanıcılar.xlsx
├── ogrenciler.xlsx
├── dersler.csv
├── ogrenciler.csv
├── Veriler.xlsx
└── *_raporu_*.txt
```

### Sınıf Dosyası Örneği (`25-AV-01-04-00.xlsx`)
- `25`: Dönem
- `AV`: Bölge (Avrupa)
- `01`: Yaş grubu
- `04`: Seviye
- `00`: Sınıf sıra numarası

---

## 🚀 Hızlı Başlangıç

```powershell
# 1. Sahte veri oluştur
python "00-fake_data_creator.py"

# 2. İlk sınıfları oluştur
python "01-Sinif-olusturma-pipeline.py"

# 3. Küçük sınıfları birleştir
python "02-yerlestirilemeyen ogrencileri uygun siniflara atar.py"

# 4. Sınıfları böl ve kodla
python "03-ogrencileri siniflara boler-sinif kodlarini olusturur.py"

# 5. Saatleri Türkiye'ye çevir
python "04-Ders satlerinin TR ye cevrilmesi.py"

# 6. CSV dışarı aktar
python "06-ders ve ogrenci csv dosyalari.py"
```

---

## ⚙️ Hızlı Konfigürasyon Notları

- Standart sınıf büyüklüğü: `15` (esneklik `±2`)
- Minimum sınıf mevcut: `5`
- Saat farkları script içinde `saat_farklari` dict olarak tanımlıdır; eksik ülkeleri ekleyin.

---

## 🔍 Sorun Giderme

- `adsoyad.xlsx` yoksa `00` script rastgele isim üretebilir.
- `Siniflar/` veya `YeniSiniflar/` beklenen formatta değilse adlandırmayı kontrol edin.
- `06` scripti çalıştırmadan önce `YeniSiniflar/` ve `ogrenciler.xlsx` dosyalarının mevcut olduğundan emin olun.

---

**Son Güncelleme**: Kasım 2025

**Versiyon**: 1.1
