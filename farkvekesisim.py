import pandas as pd

# Dosyaları oku
buyuk = pd.read_excel("all.xlsx")
kucuk = pd.read_excel("kurs.xlsx")

# "tc" sütununu anahtar olarak kullanarak farkı bul
fark = buyuk[~buyuk["username"].isin(kucuk["username"])]
kes = buyuk[buyuk["username"].isin(kucuk["username"])]
# Sonucu yeni bir dosyaya kaydet
fark.to_excel("fark.xlsx", index=False)
kes.to_excel("kes.xlsx", index=False)

print("İşlem tamamlandı. 'fark.xlsx' dosyası oluşturuldu.")
