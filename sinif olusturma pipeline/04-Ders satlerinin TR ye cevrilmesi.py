#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import pandas as pd
import pandas as pd
import os
from tabulate import tabulate

path="./YeniSiniflar/"
def find_the_way(path,file_format):
    files_add = []
    # r=root, d=directories, f = files
    for r, d, f in os.walk(path):
        for file in f:
            if file_format in file:
                files_add.append(os.path.join(r, file))  
    return files_add
files_add=find_the_way(path,'.xlsx')
files_add


lines = [["Kod","Ulke","YAS",  "Gun","saat" ,"SEVIYE"]]
for i in files_add:
    df=pd.read_excel(i)
    code=i[15:-5]
    temp=df["Orijinal_Dosya"].unique()[0]
    temp=temp.split("@")
    ulke=temp[1]
    yas=temp[2]
    x=temp[3].split("-")[1]
    gun=x.split("_")[0]
    saat=x.split("_")[1][:2]
    seviye=temp[4]
    lines.append([code,ulke,yas,gun,saat,seviye])
results = pd.DataFrame (lines[1:], columns = lines[0])

results.to_excel("Veriler.xlsx",index=False)



# Saat farkları (TR saati ile fark)
saat_farklari = {
    "Bulgaristan": 0,
    "Çin": -8,
    "Hollanda": 1,
    "Iskandinavya": 1,
    "Amerika_Birleik_Devletleri": 7
}

# Excel veya CSV dosyasını oku
try:
    df = pd.read_excel("veriler.xlsx")  # dosya adı değiştirilebilir
except FileNotFoundError:
    print("HATA: 'veriler.xlsx' dosyası bulunamadı.")
    # Örnek bir DataFrame oluştur (kodun çalışmasını göstermek için)
    data = {
        'Ulke': ['Çin', 'Hollanda', 'Bulgaristan', 'Amerika_Birleik_Devletleri'],
        'saat': [15, 9, 12, 2],
        'Gun': ['Pazartesi', 'Salı', 'Çarşamba', 'Cuma']
    }
    df = pd.DataFrame(data)
    print("'veriler.xlsx' bulunamadığı için örnek DataFrame kullanılıyor.")


# Türkiye saatini hesaplayan fonksiyon
def tr_saat(row):
    ulke = row["Ulke"]
    saat = row["saat"]
    fark = saat_farklari.get(ulke, 0)
    yeni_saat = (saat + fark) % 24  # 24 saati geçerse modulo
    return yeni_saat

# Yeni sütun ekle
df["saat_tr"] = df.apply(tr_saat, axis=1)

# === İSTEDİĞİNİZ DEĞİŞİKLİK ===
# 'Gun' sütununu 'saat_tr' sütunuyla birleştir.
# Önce 'saat_tr' (sayı) sütununu .astype(str) ile metne dönüştürmeliyiz.
df["gun_saat_tr"] = df["Gun"] + df["saat_tr"].astype(str)
# ===============================

# Yeni dosya olarak kaydet
df.to_excel("ogrenciler.xlsx", index=False)

print("Yeni Excel dosyası oluşturuldu: ogrenciler.xlsx")
print("\nDataFrame'in son hali (ilk 5 satır):")
print(df.head())

