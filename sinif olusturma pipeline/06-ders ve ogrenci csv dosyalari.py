#!/usr/bin/env python
# coding: utf-8

# In[3]:


import pandas as pd

# Excel dosyasını oku
dosya_adi = "atama_sonuclari.xlsx"

# Her iki sayfayı oku
atama_sonuclari = pd.read_excel(dosya_adi, sheet_name="Atama Sonuçları")
atanamayan_siniflar = pd.read_excel(dosya_adi, sheet_name="Atanamayan Sınıflar")

# Atama Sonuçları için dictionary oluştur
atama_dict = {}
for index, row in atama_sonuclari.iterrows():
    key = row['Ogrenci_KODU']
    value = f"{row['Ogrenci_KODU']} - {row['Ogrenci_YAS']} - {row['Ogrenci_SEVIYE']} - {row['Istenen_Saat']} - {row['Atanan_Ogretmen']} - {row['Ogretmen_Bransi']}"
    atama_dict[key] = value

# Atanamayan Sınıflar için dictionary oluştur
atanamayan_dict = {}
for index, row in atanamayan_siniflar.iterrows():
    key = row['Ogrenci_KODU']
    value = f"{row['Ogrenci_KODU']} - {row['Ogrenci_YAS']} - {row['Ogrenci_SEVIYE']} - {row['Istenen_Saat']} - {row['Sebep']}"
    atama_dict[key] = value

# Sonuçları yazdır
print("=" * 80)
print("ATAMA SONUÇLARI")
print("=" * 80)
for key, value in atama_dict.items():
    print(f"Key: {key}")
    print(f"Value: {value}")
    print("-" * 80)

print("\n" + "=" * 80)
print("ATANAMAYAN SINIFLAR")
print("=" * 80)
for key, value in atanamayan_dict.items():
    print(f"Key: {key}")
    print(f"Value: {value}")
    print("-" * 80)


# In[4]:


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




ders = [["shortname","fullname",	"category"]]
ogrenci=[["username",	"course1",	"role1"]]
for i in files_add:
    df=pd.read_excel(i)
    code=i[15:-5]
    temp=atama_dict[code]
    ders.append([code,temp,5])
    for j in  df["username"].values:
        ogrenci.append([j,code,"student"])
df = pd.DataFrame (ders[1:], columns = ders[0])
of = pd.DataFrame (ogrenci[1:], columns = ogrenci[0])
df.to_csv("dersler.csv", index=False)      
of.to_csv("ogrenciler.csv", index=False)


    


# In[ ]:




