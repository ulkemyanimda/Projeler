import pandas as pd
import re
import unicodedata

# Türkçe karakterleri ve özel karakterleri temizleyen fonksiyon
def temizle_dosya_adi(baslik):
    # Türkçe karakterleri ASCII'ye çevir
    normalized = unicodedata.normalize('NFKD', baslik)
    ascii_str = normalized.encode('ascii', 'ignore').decode('ascii')
    # Sadece harf ve rakam kalsın
    ascii_str = re.sub(r'[^A-Za-z0-9]', '', ascii_str)
    return ascii_str

# Excel dosyasını oku
df = pd.read_excel("1.xlsx")

html_output = ""

# Her satır için HTML kart oluştur
for _, row in df.iterrows():
    baslik = str(row["baslik"]).strip()
    adres = str(row["adres"]).strip()
    dosya_adi = temizle_dosya_adi(baslik)

    html_output += f"""
<div class="icon">
    <iframe frameborder="0" title="{baslik}" src="{adres}" allowfullscreen="true" scrolling="no"></iframe>
    <span>{baslik}</span>
    <a class="download-btn" href="zips/{dosya_adi}.zip" download>Scorm indir</a>
</div>

"""

# Sonucu dosyaya kaydet
with open("output.html", "w", encoding="utf-8") as f:
    f.write(html_output)

print("✅ HTML kartlar 'output.html' dosyasına kaydedildi.")
