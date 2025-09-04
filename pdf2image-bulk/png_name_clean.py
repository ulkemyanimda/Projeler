import os
import re

# PNG dosyalarının olduğu klasörün yolunu buraya yaz
klasor_yolu = "extracted_images"

for dosya in os.listdir(klasor_yolu):
    if dosya.lower().endswith(".png"):  # sadece png dosyaları
        eski_yol = os.path.join(klasor_yolu, dosya)

        # Harfleri sil → sadece rakam ve alt çizgi kalsın
        yeni_isim = re.sub(r"[^0-9_]", "", os.path.splitext(dosya)[0])

        # Baştaki ve sondaki alt çizgileri sil
        yeni_isim = yeni_isim.strip("_")

        # Boş kalma ihtimaline karşı kontrol
        if not yeni_isim:
            yeni_isim = "dosya"

        yeni_isim = yeni_isim + ".png"
        yeni_yol = os.path.join(klasor_yolu, yeni_isim)

        if not os.path.exists(yeni_yol):
            os.rename(eski_yol, yeni_yol)
            print(f"{dosya} → {yeni_isim}")
        else:
            print(f"⚠️ {yeni_isim} zaten var, atlandı.")
