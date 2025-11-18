import pandas as pd
import os
import re

print("İşlem başlıyor...")

# --- SCRIPT 1: Öğrenci Tercihlerini Ana Dosyaya Ekleme ---
print("1. Adım: Öğrenci tercihleri '1.xlsx', '2.xlsx', '3.xlsx' dosyalarından okunuyor...")

kullanici_dosyasi = "Kullanıcılar.xlsx"
if not os.path.exists(kullanici_dosyasi):
    print(f"HATA: Ana dosya '{kullanici_dosyasi}' bulunamadı. Script durduruldu.")
    exit()
    
kullanicilar_df = pd.read_excel(kullanici_dosyasi)

# Tercih sütununu ekleyelim (eğer yoksa), başlangıçta boş
if 'Tercih' not in kullanicilar_df.columns:
    kullanicilar_df['Tercih'] = ""

ogrenci_dosyalari = ["1.xlsx", "2.xlsx", "3.xlsx"]
bulunan_tercih_sayisi = 0

for dosya in ogrenci_dosyalari:
    if os.path.exists(dosya):
        print(f"  -> '{dosya}' işleniyor...")
        ogrenci_df = pd.read_excel(dosya)
        
        # Boş değerleri string olarak değiştir (NaN sorun olmasın)
        ogrenci_df = ogrenci_df.fillna("")
        
        # Kullanıcılar ile eşleşme kontrolü
        for idx, kullanici in kullanicilar_df.iterrows():
            # Eşleşme için tüm alanları string'e çevirip boşlukları temizle
            match = ogrenci_df[
                (ogrenci_df['Öğrencinin adı'].astype(str).str.strip() == str(kullanici['firstname']).strip()) &
                (ogrenci_df['Öğrencinin soyadı'].astype(str).str.strip() == str(kullanici['lastname']).strip()) &
                (ogrenci_df['E-posta adresi'].astype(str).str.strip() == str(kullanici['email']).strip())
            ]
            if not match.empty:
                # Tercih değerini al ve kullanıcı dataframe'ine yaz
                kullanicilar_df.at[idx, 'Tercih'] = match.iloc[0]['Tercih']
                bulunan_tercih_sayisi += 1
    else:
        print(f"  -> UYARI: '{dosya}' bulunamadı, atlanıyor.")

# Ana dosyayı güncelle
kullanicilar_df.to_excel("Kullanıcılar.xlsx", index=False)
print(f"✅ 1. Adım tamamlandı: {bulunan_tercih_sayisi} tercih bulundu ve 'Kullanıcılar.xlsx' güncellendi.")
print("-" * 30)


# --- SCRIPT 2: 'ders_saati' Sütununu Ekleme ---
print("2. Adım: 'ders_saati' sütunu kopyalanıyor...")

# Dosyayı tekrar oku (bir önceki adımda kaydedildi)
df = pd.read_excel("Kullanıcılar.xlsx")
df['ders_saati'] = df["profile_field_derssaat"]
df.to_excel("Kullanıcılar.xlsx", index=False)

print("✅ 2. Adım tamamlandı: 'ders_saati' sütunu eklendi ve dosya güncellendi.")
print("-" * 30)


# --- SCRIPT 3: Veri Temizleme ve Yeni Sütunlar (Rutbe, Ulke, Ders) ---
print("3. Adım: Veri temizleme ve 'rutbe', 'Ulke', 'ders' sütunları oluşturuluyor...")

df = pd.read_excel("Kullanıcılar.xlsx")

# 1) Tarihten yılı çıkartma
# Tarih sütununu string'e çevirerek hataları önle
df["profile_field_DT_clean"] = df["profile_field_DT"].astype(str)
# 1a) Gün isimlerini sil (örn. "Pazartesi, ")
df["profile_field_DT_clean"] = df["profile_field_DT_clean"].str.replace(r"^[^,]+, ", "", regex=True)

# 1b) Türkçe ay isimlerini İngilizce'ye çevir
ay_map = {
    "Ocak": "January", "Şubat": "February", "Mart": "March", "Nisan": "April",
    "Mayıs": "May", "Haziran": "June", "Temmuz": "July", "Ağustos": "August",
    "Eylül": "September", "Ekim": "October", "Kasım": "November", "Aralık": "December"
}
for tr, en in ay_map.items():
    df["profile_field_DT_clean"] = df["profile_field_DT_clean"].str.replace(tr, en)

# 1c) Tarihi parse et ve yıl bilgisini al
df["year"] = pd.to_datetime(
    df["profile_field_DT_clean"],
    format="%d %B %Y, %I:%M %p",
    errors="coerce"  # Hata verirse NaN ata (programı durdurma)
).dt.year


# 2) Yıla göre rutbe sütunu
def get_rutbe(year):
    if pd.isna(year):
        return None
    if year in [2021, 2020, 2019, 2018]: return "Freshman"
    elif year in [2017, 2016, 2015]: return "Sophomore"
    elif year in [2014, 2013, 2012]: return "Junior"
    elif year in [2011, 2010, 2009, 2008, 2007, 2006]: return "Senior"
    else: return None # Eşleşmezse None (NaN) olacak

df["rutbe"] = df["year"].apply(get_rutbe)

# 3) Ulke düzenleme
ulke_map = {
    "Amerika Birleşik Devletleri": "Amerika Birleşik Devletleri", "Bulgaristan": "Avrupa",
    "Çin": "Çin", "Hollanda": "Avrupa", "İsveç": "Avrupa", "Finlandiya": "Avrupa",
    "Norveç": "Avrupa", "Karadağ": "Avrupa", "Danimarka": "Avrupa", "İtalya": "Avrupa",
    "İspanya": "Avrupa", "İzlanda": "Avrupa"
}
# .map() fonksiyonu, sözlükte olmayan ülkeler için otomatik olarak NaN atar.
df["Ulke"] = df["profile_field_ulke"].map(ulke_map) 

# 4) Tercih - ders_saati sütunlarını birleştirme
# Eğer ikisi de boşsa (NaN) sonuç NaN olur.
df["ders"] = df["Tercih"].fillna(df["ders_saati"])

# Temizlik için oluşturulan ara sütunu sil
if "profile_field_DT_clean" in df.columns:
    df = df.drop(columns=["profile_field_DT_clean"])

df.to_excel("Kullanıcılar.xlsx", index=False)
print("✅ 3. Adım tamamlandı: 'rutbe', 'Ulke' ve 'ders' sütunları oluşturuldu, dosya güncellendi.")
print("-" * 30)


# --- SCRIPT 4: Sınıflara Ayırma (DÜZELTİLMİŞ) ---
print("4. Adım: Öğrenciler sınıflara ayrılıyor...")

input_file = "Kullanıcılar.xlsx"
output_dir = "Siniflar"
os.makedirs(output_dir, exist_ok=True)

df = pd.read_excel(input_file)

# Gruplama yapılacak sütunlar
group_cols = ["Ulke", "rutbe", "ders", "profile_field_dilseviyesi"]

# --- DÜZELTME 1: dropna=False ---
# Bu parametre, NaN (Boş) değerli satırları (örn. rutbesi, ülkesi olmayan)
# gruplama dışında bırakmamanızı sağlar.
# Eksik öğrencilerinizin tamamı bu sayede dahil edilecek.
grouped = df.groupby(group_cols, dropna=False)

def temizle_dosya_adi(text):
    """Dosya adı için YALNIZCA geçersiz karakterleri temizler"""
    if pd.isna(text):
        return "Bilinmiyor"  # NaN değerler bu gruba girer
    text = str(text).strip()
    
    # --- DÜZELTME 2: Daha Az Agresif Temizleme ---
    # Sadece Windows/Linux'ta gerçekten geçersiz olan karakterleri kaldır.
    # Parantez (), artı +, virgül , gibi karakterler kalabilir.
    # Bu, "Ders (A1)" ve "Ders (A2)" gibi grupların "Ders_A1" olarak çakışmasını önler.
    text = re.sub(r'[\\/*?:"<>|]', "", text)  
    
    text = re.sub(r"\s+", "_", text)  # Boşlukları _ yap
    return text

toplam_ogrenci = 0
# Her grup için ayrı dosya oluştur
for keys, group in grouped:
    ulke, rutbe, ders, dil = keys
    grup_sayisi = len(group)
    toplam_ogrenci += grup_sayisi
    
    # Dosya ismini oluştur
    dosya_adi = f"{grup_sayisi}@{temizle_dosya_adi(ulke)}@{temizle_dosya_adi(rutbe)}@" \
                f"{temizle_dosya_adi(ulke)}-{temizle_dosya_adi(ders)}@{temizle_dosya_adi(dil)}.xlsx"
    
    dosya_yolu = os.path.join(output_dir, dosya_adi)
    
    # Excel'e kaydet
    group.to_excel(dosya_yolu, index=False)

print(f"✅ 4. Adım tamamlandı: Toplam {toplam_ogrenci} öğrenci, {len(grouped)} adet sınıf dosyasına ayrıldı.")
print(f"Tüm işlemler bitti! Dosyalarınızı '{output_dir}' klasöründe bulabilirsiniz.")