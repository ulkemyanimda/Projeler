import pandas as pd
import os
import shutil
import zipfile
from pathlib import Path
import unicodedata
import re

def temizle_dosya_adi(metin):
    """
    Türkçe karakterleri çevirir, özel karakterleri ve boşlukları kaldırır
    """
    # Türkçe karakterleri İngilizce karşılıklarına çevir
    turkce_harfler = {
        'ç': 'c', 'Ç': 'C',
        'ğ': 'g', 'Ğ': 'G',
        'ı': 'i', 'İ': 'I',
        'ö': 'o', 'Ö': 'O',
        'ş': 's', 'Ş': 'S',
        'ü': 'u', 'Ü': 'U'
    }
    
    for tr, en in turkce_harfler.items():
        metin = metin.replace(tr, en)
    
    # Boşlukları kaldır
    metin = metin.replace(' ', '')
    
    # Sadece harf ve rakamları tut (özel karakterleri kaldır)
    metin = re.sub(r'[^a-zA-Z0-9]', '', metin)
    
    return metin

def html_olustur(baslik, src):
    """
    iframe içeren HTML içeriği oluşturur
    """
    html_icerik = f'''<!DOCTYPE html>
<html lang="tr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{baslik}</title>
    <style>
        body {{
            margin: 0;
            padding: 0;
            overflow: hidden;
        }}
        iframe {{
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            border: none;
        }}
    </style>
</head>
<body>
    <iframe frameborder="0" title="{baslik}" src="{src}" allowfullscreen="true" scrolling="no"></iframe>
</body>
</html>'''
    return html_icerik

def scorm_paketi_olustur(baslik, src, example_klasor, output_klasor):
    """
    Bir SCORM paketi oluşturur
    """
    # Temiz dosya adı oluştur
    dosya_adi = temizle_dosya_adi(baslik)
    
    # Geçici klasör oluştur
    temp_klasor = os.path.join(output_klasor, f"temp_{dosya_adi}")
    
    # Example klasörünü kopyala
    if os.path.exists(temp_klasor):
        shutil.rmtree(temp_klasor)
    shutil.copytree(example_klasor, temp_klasor)
    
    # index.html oluştur ve kaydet
    html_icerik = html_olustur(baslik, src)
    index_path = os.path.join(temp_klasor, "index.html")
    with open(index_path, 'w', encoding='utf-8') as f:
        f.write(html_icerik)
    
    # ZIP dosyası oluştur
    zip_path = os.path.join(output_klasor, f"{dosya_adi}.zip")
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(temp_klasor):
            for file in files:
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, temp_klasor)
                zipf.write(file_path, arcname)
    
    # Geçici klasörü sil
    shutil.rmtree(temp_klasor)
    
    print(f"✓ SCORM paketi oluşturuldu: {dosya_adi}.zip")
    return zip_path

def main():
    # Dosya yolları
    excel_dosya = "1.xlsx"
    example_klasor = "example"
    output_klasor = "scorm_paketleri"
    
    # Output klasörü oluştur
    if not os.path.exists(output_klasor):
        os.makedirs(output_klasor)
    
    # Example klasörünün varlığını kontrol et
    if not os.path.exists(example_klasor):
        print(f"HATA: '{example_klasor}' klasörü bulunamadı!")
        return
    
    # Excel dosyasını oku
    try:
        df = pd.read_excel(excel_dosya)
    except FileNotFoundError:
        print(f"HATA: '{excel_dosya}' dosyası bulunamadı!")
        return
    except Exception as e:
        print(f"HATA: Excel dosyası okunurken hata oluştu: {e}")
        return
    
    # Sütun isimlerini kontrol et
    if 'baslik' not in df.columns or 'adres' not in df.columns:
        print("HATA: Excel dosyasında 'baslik' ve 'adres' sütunları bulunamadı!")
        print(f"Bulunan sütunlar: {df.columns.tolist()}")
        return
    
    # Her satır için SCORM paketi oluştur
    basarili = 0
    basarisiz = 0
    
    print(f"\n{len(df)} adet SCORM paketi oluşturuluyor...\n")
    
    for index, row in df.iterrows():
        baslik = str(row['baslik']).strip()
        adres = str(row['adres']).strip()
        
        if pd.isna(baslik) or pd.isna(adres) or baslik == '' or adres == '':
            print(f"⚠ Satır {index + 1} atlandı (boş veri)")
            basarisiz += 1
            continue
        
        try:
            scorm_paketi_olustur(baslik, adres, example_klasor, output_klasor)
            basarili += 1
        except Exception as e:
            print(f"✗ Satır {index + 1} için hata: {e}")
            basarisiz += 1
    
    print(f"\n{'='*50}")
    print(f"İşlem tamamlandı!")
    print(f"Başarılı: {basarili}")
    print(f"Başarısız: {basarisiz}")
    print(f"Toplam: {len(df)}")
    print(f"SCORM paketleri '{output_klasor}' klasörüne kaydedildi.")
    print(f"{'='*50}")

if __name__ == "__main__":
    main()
