import pandas as pd
import pandas as pd
import os

# Kullanıcı dosyası
kullanici_dosyasi = "Kullanıcılar.xlsx"
kullanicilar_df = pd.read_excel(kullanici_dosyasi)

# Tercih sütununu ekleyelim, başlangıçta boş
kullanicilar_df['Tercih'] = ""

# Öğrenci dosyaları
ogrenci_dosyalari = ["1.xlsx", "2.xlsx", "3.xlsx"]

for dosya in ogrenci_dosyalari:
    if os.path.exists(dosya):
        ogrenci_df = pd.read_excel(dosya)
        
        # Boş değerleri string olarak değiştir (NaN sorun olmasın)
        ogrenci_df = ogrenci_df.fillna("")
        
        # Kullanıcılar ile eşleşme kontrolü
        for idx, kullanici in kullanicilar_df.iterrows():
            match = ogrenci_df[
                (ogrenci_df['Öğrencinin adı'].str.strip() == str(kullanici['firstname']).strip()) &
                (ogrenci_df['Öğrencinin soyadı'].str.strip() == str(kullanici['lastname']).strip()) &
                (ogrenci_df['E-posta adresi'].str.strip() == str(kullanici['email']).strip())
            ]
            if not match.empty:
                # Tercih değerini al ve kullanıcı dataframe'ine yaz
                kullanicilar_df.at[idx, 'Tercih'] = match.iloc[0]['Tercih']

# Yeni dosya olarak kaydet (istersen üzerine yazabilirsin)
kullanicilar_df.to_excel("Kullanıcılar.xlsx", index=False)

print("İşlem tamamlandı, 'kullanicilar_guncel.xlsx' oluşturuldu.")













# Excel dosyasını oku
df = pd.read_excel("Kullanıcılar.xlsx")  # kendi dosya yolunu buraya yaz

# Ders saatleri sözlüğü
schedule_options = {
    "Amerika Birleşik Devletleri": [
        "Cumartesi 09:00 - 10:30",
        "Pazar 09:00 - 10:30",
        "Cumartesi 12:00 - 13:30",
        "Pazar 12:00 - 13:30"
    ],
    "Bulgaristan": [
        "Cumartesi 10:00 - 11:30",
        "Pazar 10:00 - 11:30",
        "Cumartesi 17:00 - 18:30",
        "Pazar 17:00 - 18:30",
        "Salı 19:00 - 20:30",
        "Çarşamba 19:00 - 20:30",
        "Perşembe 19:00 - 20:30"
    ],
    "Çin": [
        "Cumartesi 17:00 - 18:30",
        "Pazar 17:00 - 18:30"
    ],
    "Hollanda": [
        "Cumartesi 09:00 - 10:30",
        "Pazar 09:00 - 10:30",
        "Cumartesi 12:00 - 13:30",
        "Pazar 12:00 - 13:30",
        "Cumartesi 17:00 - 18:30",
        "Pazar 17:00 - 18:30",
        "Salı 18:00 - 19:30",
        "Çarşamba 18:00 - 19:30",
        "Perşembe 18:00 - 19:30"
    ],
    "İsveç": [
        "Cumartesi 09:00 - 10:30",
        "Pazar 09:00 - 10:30",
        "Cumartesi 12:00 - 13:30",
        "Pazar 12:00 - 13:30",
        "Cumartesi 17:00 - 18:30",
        "Pazar 17:00 - 18:30",
        "Salı 18:00 - 19:30",
        "Çarşamba 18:00 - 19:30",
        "Perşembe 18:00 - 19:30"
    ],
    "Finlandiya": [
        "Cumartesi 09:00 - 10:30",
        "Pazar 09:00 - 10:30",
        "Cumartesi 12:00 - 13:30",
        "Pazar 12:00 - 13:30",
        "Cumartesi 17:00 - 18:30",
        "Pazar 17:00 - 18:30",
        "Salı 18:00 - 19:30",
        "Çarşamba 18:00 - 19:30",
        "Perşembe 18:00 - 19:30"
    ],
    "Norveç": [
        "Cumartesi 09:00 - 10:30",
        "Pazar 09:00 - 10:30",
        "Cumartesi 12:00 - 13:30",
        "Pazar 12:00 - 13:30",
        "Cumartesi 17:00 - 18:30",
        "Pazar 17:00 - 18:30",
        "Salı 18:00 - 19:30",
        "Çarşamba 18:00 - 19:30",
        "Perşembe 18:00 - 19:30"
    ],
    "Danimarka": [
        "Cumartesi 09:00 - 10:30",
        "Pazar 09:00 - 10:30",
        "Cumartesi 12:00 - 13:30",
        "Pazar 12:00 - 13:30",
        "Cumartesi 17:00 - 18:30",
        "Pazar 17:00 - 18:30",
        "Salı 18:00 - 19:30",
        "Çarşamba 18:00 - 19:30",
        "Perşembe 18:00 - 19:30"
    ],
    "İtalya": [
        "Cumartesi 09:00 - 10:30",
        "Pazar 09:00 - 10:30",
        "Cumartesi 12:00 - 13:30",
        "Pazar 12:00 - 13:30",
        "Cumartesi 17:00 - 18:30",
        "Pazar 17:00 - 18:30",
        "Salı 18:00 - 19:30",
        "Çarşamba 18:00 - 19:30",
        "Perşembe 18:00 - 19:30"
    ],
    "İspanya": [
        "Cumartesi 09:00 - 10:30",
        "Pazar 09:00 - 10:30",
        "Cumartesi 12:00 - 13:30",
        "Pazar 12:00 - 13:30",
        "Cumartesi 17:00 - 18:30",
        "Pazar 17:00 - 18:30",
        "Salı 18:00 - 19:30",
        "Çarşamba 18:00 - 19:30",
        "Perşembe 18:00 - 19:30"
    ],
    "İzlanda": [
        "Cumartesi 09:00 - 10:30",
        "Pazar 09:00 - 10:30",
        "Cumartesi 12:00 - 13:30",
        "Pazar 12:00 - 13:30",
        "Cumartesi 17:00 - 18:30",
        "Pazar 17:00 - 18:30",
        "Salı 18:00 - 19:30",
        "Çarşamba 18:00 - 19:30",
        "Perşembe 18:00 - 19:30"
    ],
    "Diğer": ["Lütfen ülke seçin"],
    "Öğretmen": ["Kendi programını belirleyecek"]
}

# Yeni sütun ekleme fonksiyonu
def get_lesson(row):
    country = row['profile_field_ulke']
    choice = row['profile_field_derssaat']
    lessons = schedule_options.get(country, ["Saat bilgisi bulunamadı"])
    try:
        index = int(choice) - 1  # tercihler 1'den başlıyor, index 0'dan
        return lessons[index]
    except (ValueError, IndexError):
        return "Geçersiz tercih"

# Yeni sütunu ekle
df['ders_saati'] = df.apply(get_lesson, axis=1)

# Excel dosyasına kaydet
df.to_excel("Kullanıcılar.xlsx", index=False)
print("Excel dosyası güncellendi ve 'ders_saati' sütunu eklendi.")



import pandas as pd

# Excel dosyasını oku
df = pd.read_excel("Kullanıcılar.xlsx")

# 1) Tarihten yılı çıkartma
# Tarih sütununu yıl bilgisine çevirmek için temizleme + dönüştürme

# 1) Gün isimlerini sil (örn. "Pazartesi, ")
df["profile_field_DT"] = df["profile_field_DT"].str.replace(r"^[^,]+, ", "", regex=True)

# 2) Türkçe ay isimlerini İngilizce'ye çevir
ay_map = {
    "Ocak": "January",
    "Şubat": "February",
    "Mart": "March",
    "Nisan": "April",
    "Mayıs": "May",
    "Haziran": "June",
    "Temmuz": "July",
    "Ağustos": "August",
    "Eylül": "September",
    "Ekim": "October",
    "Kasım": "November",
    "Aralık": "December"
}
for tr, en in ay_map.items():
    df["profile_field_DT"] = df["profile_field_DT"].str.replace(tr, en)

# 3) Tarihi parse et ve yıl bilgisini al
df["year"] = pd.to_datetime(
    df["profile_field_DT"],
    format="%d %B %Y, %I:%M %p",
    errors="coerce"
).dt.year


# 2) Yıla göre rutbe sütunu
def get_rutbe(year):
    if year in [2021, 2020, 2019, 2018]:
        return "Freshman"
    elif year in [2017, 2016, 2015]:
        return "Sophomore"
    elif year in [2014, 2013, 2012]:
        return "Junior"
    elif year in [2011, 2010, 2009, 2008, 2007, 2006]:
        return "Senior"
    else:
        return None

df["rutbe"] = df["year"].apply(get_rutbe)

# 3) Ulke düzenleme
ulke_map = {
    "Amerika Birleşik Devletleri": "Amerika Birleşik Devletleri",
    "Bulgaristan": "Avrupa",
    "Çin": "Çin",
    "Hollanda": "Avrupa",
    "İsveç": "Avrupa",
    "Finlandiya": "Avrupa",
    "Norveç": "Avrupa",
    "Karadağ": "Avrupa",
    "Danimarka": "Avrupa",
    "İtalya": "Avrupa",
    "İspanya": "Avrupa",
    "İzlanda": "Avrupa"
}

df["Ulke"] = df["profile_field_ulke"].map(ulke_map)

# 4) Tercih - ders_saati sütunlarını birleştirme
df["ders"] = df["Tercih"].fillna(df["ders_saati"])

# Yeni dosyaya kaydet
df.to_excel("Kullanıcılar.xlsx", index=False)

print("✅ Düzenlemeler tamamlandı. 'duzenlenmis_dosya.xlsx' dosyasına kaydedildi.")

import pandas as pd
import os
import re

# Kaynak Excel dosyasının yolu
input_file = "Kullanıcılar.xlsx"

# Çıkış klasörü
output_dir = "Siniflar"
os.makedirs(output_dir, exist_ok=True)

# Excel dosyasını oku
df = pd.read_excel(input_file)

# Gruplama yapılacak sütunlar
group_cols = ["Ulke", "rutbe", "ders", "profile_field_dilseviyesi"]

# Gruplara ayır
grouped = df.groupby(group_cols)

def temizle_dosya_adi(text):
    """Dosya adı için uygunsuz karakterleri temizler"""
    if pd.isna(text):
        return "Bilinmiyor"
    text = str(text).strip()
    text = re.sub(r"[^\w\s-]", "", text)  # özel karakterleri kaldır
    text = re.sub(r"\s+", "_", text)      # boşlukları _ yap
    return text

# Her grup için ayrı dosya oluştur
for keys, group in grouped:
    ulke, rutbe, ders, dil = keys
    
    # Dosya ismini oluştur
    dosya_adi = f"{len(group)}@"\
    f"{temizle_dosya_adi(ulke)}@{temizle_dosya_adi(rutbe)}@" \
                f"{temizle_dosya_adi(ulke)}-{temizle_dosya_adi(ders)}@{temizle_dosya_adi(dil)}.xlsx" 
                
    
    dosya_yolu = os.path.join(output_dir, dosya_adi)
    
    # Excel'e kaydet
    group.to_excel(dosya_yolu, index=False)

print("✅ Tüm sınıf dosyaları başarıyla oluşturuldu!")
