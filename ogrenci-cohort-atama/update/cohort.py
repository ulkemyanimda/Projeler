import pandas as pd

# Dosyaları oku
buyuk = pd.read_csv("yeni.csv")
kucuk = pd.read_csv("eski.csv")

# "tc" sütununu anahtar olarak kullanarak farkı bul
fark = buyuk[~buyuk["username"].isin(kucuk["username"])]
kes = buyuk[buyuk["username"].isin(kucuk["username"])]
# Sonucu yeni bir dosyaya kaydet
fark.to_csv("yuklemelik.csv", index=False)


print("İşlem tamamlandı. 'yuklemelik.csv' dosyası oluşturuldu.")