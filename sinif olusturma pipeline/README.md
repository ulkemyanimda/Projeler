# Pipeline İşlemleri

Bu klasör, öğrencilerin sınıflara yerleştirilmesi ve ders atanması için kullanılan Python betikleri içerir. Pipeline, öğrenci verilerini işlemek, sınıflar oluşturmak, optimize etmek ve son olarak LMS sistemine aktarmak için tasarlanmıştır.

## 📋 Dosyalar ve Açıklamaları

### 1. **01-Sinif-olusturma-pipeline.py**
**Amaç:** Temel sınıf oluşturma işlemlerini gerçekleştiren ana pipeline script'i

**İşlevler:**
- Kullanıcı bilgilerini (`Kullanıcılar.xlsx`) okur
- Öğrenci tercihlerini (`1.xlsx`, `2.xlsx`, `3.xlsx`) bağlar
- Ülkeye göre ders saatleri atanır
- Öğrencilerin kayıt yılına göre sınıf düzeyi (Freshman, Sophomore, vb.) belirler
- Ülkeleri bölgesel kategorilere ayırır (Avrupa, Çin, ABD vb.)
- Öğrencileri tercihlerine göre Excel dosyalarına yerleştirir

**Çıktı:** `Siniflar/` klasöründe gruplandırılmış Excel dosyaları

**Dosya Adı Format:** `{öğrenci_sayısı}@{bolge}@{yas}@{ülke}-{ders_saati}@{seviye}.xlsx`

---

### 2. **02-yerlestirilemeyen ogrencileri uygun siniflara atar.py**
**Amaç:** Çok az öğrenciye sahip sınıfları birleştirme (Sınıf Birleştirici)

**İşlevler:**
- 5 öğrenciden az olan sınıfları tespit eder
- Uyumlu sınıfları bulur ve birleştirir:
  - Aynı bölge ve ders saati gereklidir
  - Benzer yaş grupları birleştirilebilir (Freshman + Sophomore, vb.)
  - Benzer Türkçe seviyeleri birleştirilebilir
- Birleştirme işlemini raporlar
- Eski dosyaları siler ve yeni dosyalar oluşturur

**Çalışma Sırası:** `calistir()` metodunu çağırır, işlem hakkında detaylı raporlar üretir

**Çıktı:** 
- Birleştirilmiş `Siniflar/` dosyaları
- `birleştirme_raporu_{tarih}.txt` rapor dosyası

---

### 3. **03-ogrencileri siniflara boler-sinif kodlarini olusturur.py**
**Amaç:** Sınıfları optimal boyuta bölme ve yeni sınıf kodları oluşturma (Sınıf Bölme)

**İşlevler:**
- Her sınıfı 15±2 öğrenci boyutuna böler (esneklik: 13-17 arası uygun)
- Minimum sınıf büyüklüğü: 5 öğrenci
- Her sınıfa benzersiz kod atanır

**Sınıf Kodu Formatı:** `{dönem}-{bölge}-{yaş}-{seviye}-{sıra}`
- **Dönem:** 25 (varsayılan, kullanıcı tarafından değiştirilebilir)
- **Bölge:** US (ABD), IX (İskandinavya), BG (Bulgaristan), vb.
- **Yaş:** 01 (Freshman), 02 (Sophomore), 03 (Junior), 04 (Senior)
- **Seviye:** 01-04 (Türkçe dil seviyeleri)
- **Sıra:** 00, 01, 02... (aynı özellikteki sınıflar için sıra numarası)

**Örnek Kod:** `25-AV-01-04-00`

**Çıktı:** 
- `YeniSiniflar/` klasöründe yeniden kodlanmış Excel dosyaları
- Her kayıtta `Orijinal_Dosya` sütunu eklenir
- `sinif_bolme_raporu_{tarih}.txt` rapor dosyası

---

### 4. **04-Ders satlerinin TR ye cevrilmesi.py**
**Amaç:** Ders saatlerini Türkiye Standart Saatine (TST) dönüştürme

**İşlevler:**
- `Veriler.xlsx` dosyasını okur (sınıf kodları ve bilgileri)
- Her ülke için saat farklarını tanımlar:
  - Bulgaristan: +0 saat
  - Çin: -8 saat (TST'den)
  - Hollanda: +1 saat
  - İskandinavya: +1 saat
  - ABD: +7 saat
- Yerel ders saatlerini TST'ye çevirir
- Gün ve saati birleştirerek yeni sütun oluşturur

**Çıktı:** `veriler_tr.xlsx` (Türkiye saatleriyle güncellenmiş)

---

### 5. **05-ogretmenlere ders atamasinin yapilmasi.txt**
**Tür:** Bilgiler/Talimatlar dosyası

**İçerik:** 
- Öğretmenlere ders atanması için dış bağlantı
- URL: https://ulkemyanimda.github.io/araclar/ogretmenderseslestirme/index.html
- El ile gerçekleştirilen işlem için referans

---

### 6. **06-ders ve ogrenci csv dosyalari.py**
**Amaç:** LMS/Moodle entegrasyonu için CSV dosyaları oluşturma

**İşlevler:**
- `YeniSiniflar/` klasöründen Excel dosyalarını okur
- İki ayrı CSV dosyası oluşturur:

**a) `dersler.csv` (Kurslar)**
- Sütunlar: `shortname`, `fullname`, `category`
- Her sınıf bir derse dönüşür
- Şortname: sınıf kodu (örn: `25-AV-01-04-00.xlsx`)

**b) `ogrenciler.csv` (Kursiyerler Kaydı)**
- Sütunlar: `username`, `course1`, `role1`
- Her öğrenci için uygun derse kayıt yapılır
- Rol: `student`

**Çıktı:** 
- `dersler.csv` - Moodle'a aktarılacak kurs listesi
- `ogrenciler.csv` - Moodle'a aktarılacak öğrenci kaydı

---

## 🔄 Pipeline İş Akışı

```
1. Kullanıcılar.xlsx + Tercih Dosyaları (1.xlsx, 2.xlsx, 3.xlsx)
                ↓
        01-Sinif-olusturma-pipeline.py
                ↓
        Siniflar/ (İlk gruplandırma)
                ↓
        02-yerlestirilemeyen ogrencileri atar.py
                ↓
        Siniflar/ (Birleştirilmiş)
                ↓
        03-ogrencileri siniflara boler.py
                ↓
        YeniSiniflar/ (Kodlanmış ve bölünmüş)
                ↓
        04-Ders satlerinin TR ye cevrisi.py
                ↓
        veriler_tr.xlsx (TST'ye çevrilmiş saatler)
                ↓
        06-ders ve ogrenci csv.py
                ↓
        dersler.csv + ogrenciler.csv (LMS'e aktarım)
```

---

## 📊 Veri Yapıları

### Giriş Dosyaları Gerekli Sütunlar:
- **Kullanıcılar.xlsx:** `firstname`, `lastname`, `email`, `profile_field_ulke`, `profile_field_derssaat`, `profile_field_DT`, `profile_field_dilseviyesi`, `username`
- **Tercih Dosyaları:** `Öğrencinin adı`, `Öğrencinin soyadı`, `E-posta adresi`, `Tercih`

### Ülke Kategorileri:
- **Amerika:** ABD
- **Çin:** Çin
- **Avrupa:** Bulgaristan, Hollanda, İsveç, Finlandiya, Norveç, Danimarka, İtalya, İspanya, İzlanda, Karadağ

### Yaş Grupları:
- **Freshman (01):** 2020-2021 kayıt yılı
- **Sophomore (02):** 2015-2017 kayıt yılı
- **Junior (03):** 2012-2014 kayıt yılı
- **Senior (04):** 2006-2011 kayıt yılı

### Türkçe Dil Seviyeleri:
1. Türkçeyi hiç bilmez
2. Türkçeyi anlayabilir fakat konuşamaz
3. Türkçeyi anlayabilir konuşabilir fakat yazamaz
4. Türkçeyi anlayabilir konuşabilir yazabilir

---

## ⚙️ Konfigürasyon

### Standart Sınıf Büyüklüğü:
- **Hedef:** 15 öğrenci
- **Esneklik:** ±2 (13-17 arası kabul edilebilir)
- **Minimum:** 5 öğrenci
- **Maksimum:** 17 öğrenci

### Birleştirme Kriterleri:
- Aynı bölge
- Aynı ders saati
- Uyumlu yaş grubu
- Uyumlu Türkçe seviyesi

---

## 🚀 Kullanım

1. **Giriş verilerini hazırlayın:** `Kullanıcılar.xlsx` ve tercih dosyalarını kaydedin
2. **Sırayla çalıştırın:**
   ```bash
   python 01-Sinif-olusturma-pipeline.py
   python 02-yerlestirilemeyen ogrencileri uygun siniflara atar.py
   python 03-ogrencileri siniflara boler-sinif kodlarini olusturur.py
   python 04-Ders satlerinin TR ye cevrilmesi.py
   python 06-ders ve ogrenci csv dosyalari.py
   ```

3. **Çıktı dosyalarını kontrol edin:**
   - `YeniSiniflar/` - Kodlanmış sınıflar
   - `dersler.csv` - LMS kursları
   - `ogrenciler.csv` - LMS öğrenci kayıtları
   - Rapor dosyaları - Ayrıntılı işlem özeti

---

## 📝 Rapor Dosyaları

Her işlem adımı ayrıntılı rapor üretir:
- `birleştirme_raporu_YYYYMMDD_HHMMSS.txt` - Sınıf birleştirme detayları
- `sinif_bolme_raporu_YYYYMMDD_HHMMSS.txt` - Sınıf bölme detayları
- `Veriler.xlsx` - İstatistiksel özet

---

## 🛠️ Gerekli Python Kütüphaneleri

```
pandas
openpyxl
tabulate
```

Kurulum:
```bash
pip install pandas openpyxl tabulate
```

---

## ✅ Uyumlu Sistem

- **Python Version:** 3.7+
- **İşletim Sistemi:** Windows, macOS, Linux
- **LMS:** Moodle (CSV formatı ile uyumlu)

---

## 📧 Notlar

- Her adımda otomatik raporlar oluşturulur
- Eski dosyalar işlemden sonra silinir (yedek alınız)
- Saat dönüşümleri otomatik olarak 24 saatlik format kullanır
- Kodlar benzersiz ve systematik şekilde atanır

---

**Versiyon:** 1.0  
**Son Güncelleme:** 2025  
**Dil:** Türkçe
