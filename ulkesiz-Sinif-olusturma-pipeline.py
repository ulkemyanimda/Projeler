import pandas as pd
import os
import re

# Kullanıcı dosyası
kullanici_dosyasi = "yeni.xlsx"
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
        
        # yeni ile eşleşme kontrolü
        for idx, kullanici in kullanicilar_df.iterrows():
            match = ogrenci_df[
                (ogrenci_df['Öğrencinin adı'].str.strip() == str(kullanici['firstname']).strip()) &
                (ogrenci_df['Öğrencinin soyadı'].str.strip() == str(kullanici['lastname']).strip()) &
                (ogrenci_df['E-posta adresi'].str.strip() == str(kullanici['email']).strip())
            ]
            if not match.empty:
                # Tercih değerini al ve kullanıcı dataframe'ine yaz
                kullanicilar_df.at[idx, 'Tercih'] = match.iloc[0]['Tercih']

# Yeni dosya olarak kaydet
kullanicilar_df.to_excel("yeni.xlsx", index=False)
print("İşlem tamamlandı, tercihler eklendi.")


# Excel dosyasını oku
df = pd.read_excel("yeni.xlsx")

# 1) Tarihten yılı çıkartma
# Gün isimlerini sil (örn. "Pazartesi, ")
df["profile_field_DT"] = df["profile_field_DT"].str.replace(r"^[^,]+, ", "", regex=True)

# Türkçe ay isimlerini İngilizce'ye çevir
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

# Tarihi parse et ve yıl bilgisini al
df["year"] = pd.to_datetime(
    df["profile_field_DT"],
    format="%d %B %Y, %I:%M %p",
    errors="coerce"
).dt.year


# 2) Yıla göre rutbe sütunu
def get_rutbe(year):
    if year in [2021, 2020, 2019]:
        return "Freshman"
    elif year in [2018, 2017, 2016, 2015]:
        return "Sophomore"
    elif year in [2014, 2013, 2012]:
        return "Junior"
    elif year in [2011, 2010, 2009, 2008, 2007, 2006]:
        return "Senior"
    else:
        return None

df["rutbe"] = df["year"].apply(get_rutbe)

# 3) Ders saati sütunu - artık profile_field_derssaat direkt ders saatini içeriyor
# Tercih varsa onu kullan, yoksa profile_field_derssaat'i kullan
df["ders"] = df["Tercih"].fillna(df["profile_field_derssaat"])

# Boş değerleri temizle
df["ders"] = df["ders"].replace("-- Lütfen seçiniz --", "")
df["ders"] = df["ders"].replace("", pd.NA)

# Yeni dosyaya kaydet
df.to_excel("yeni.xlsx", index=False)
print("✅ Düzenlemeler tamamlandı.")


# Sınıflara ayırma işlemi
# Kaynak Excel dosyasının yolu
input_file = "yeni.xlsx"

# Çıkış klasörü
output_dir = "Siniflar"
os.makedirs(output_dir, exist_ok=True)

# Excel dosyasını oku
df = pd.read_excel(input_file)

# Gruplama yapılacak sütunlar - sadece rutbe, ders saati ve dil seviyesi
group_cols = ["rutbe", "ders", "profile_field_dilseviyesi"]

# Gruplara ayır
grouped = df.groupby(group_cols, dropna=False)

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
    rutbe, ders, dil = keys
    
    # Dosya ismini oluştur
    dosya_adi = (f"{len(group)}@"
                f"{temizle_dosya_adi(rutbe)}@"
                f"{temizle_dosya_adi(ders)}@{temizle_dosya_adi(dil)}.xlsx")
    
    dosya_yolu = os.path.join(output_dir, dosya_adi)
    
    # Excel'e kaydet
    group.to_excel(dosya_yolu, index=False)

print("✅ Tüm sınıf dosyaları başarıyla oluşturuldu!")