import pandas as pd
import unicodedata
import os

def normalize_text(text):
    """
    Metni normalize eder: küçük harfe çevirir ve Türkçe karakterleri düzenler
    """
    if pd.isna(text):
        return ""
    
    # Küçük harfe çevir
    text = str(text).lower()
    
    # Türkçe karakterleri normalize et
    replacements = {
        'ç': 'c', 'ğ': 'g', 'ı': 'i', 'ö': 'o', 'ş': 's', 'ü': 'u',
        'Ç': 'c', 'Ğ': 'g', 'İ': 'i', 'Ö': 'o', 'Ş': 's', 'Ü': 'u'
    }
    
    for turkish_char, latin_char in replacements.items():
        text = text.replace(turkish_char, latin_char)
    
    # Ekstra boşlukları temizle
    text = ' '.join(text.split())
    
    return text

def process_names():
    """
    Ana işlem fonksiyonu
    """
    try:
        # liste.txt dosyasını oku
        if not os.path.exists('liste.txt'):
            print("Hata: liste.txt dosyası bulunamadı!")
            return
        
        with open('liste.txt', 'r', encoding='utf-8') as f:
            search_names = [line.strip() for line in f.readlines() if line.strip()]
        
        print(f"{len(search_names)} isim okundu liste.txt dosyasından")
        
        # cv_degerlendirme.xlsx dosyasını oku
        if not os.path.exists('cv_degerlendirme.xlsx'):
            print("Hata: cv_degerlendirme.xlsx dosyası bulunamadı!")
            return
        
        df = pd.read_excel('cv_degerlendirme.xlsx')
        print(f"Excel dosyası okundu. {len(df)} satır bulundu.")
        
        # Sütun isimlerini kontrol et
        required_columns = ['TC Kimlik No', 'Ad Soyad', 'Görev Yaptığı İl İlçe', 
                           'Branş', 'Şu Anda Görev Yaptığı Okul', 'E-posta Adresi', 
                           'Telefon Numarası']
        
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            print(f"Uyarı: Şu sütunlar bulunamadı: {missing_columns}")
            print(f"Mevcut sütunlar: {list(df.columns)}")
        
        # Sonuç listesi
        results = []
        
        # Her isim için kontrol yap
        for search_name in search_names:
            normalized_search = normalize_text(search_name)
            found = False
            
            # Excel'deki her satırı kontrol et
            for index, row in df.iterrows():
                excel_name = normalize_text(row.get('Ad Soyad', ''))
                
                if normalized_search == excel_name:
                    # Eşleşme bulundu, bilgileri al
                    result_row = {}
                    for col in required_columns:
                        if col in df.columns:
                            result_row[col] = row[col]
                        else:
                            result_row[col] = ''  # Sütun yoksa boş bırak
                    
                    results.append(result_row)
                    found = True
                    print(f"✓ Bulundu: {search_name} -> {row.get('Ad Soyad', '')}")
                    break
            
            if not found:
                # İsim bulunamadı, boş satır ekle
                result_row = {}
                for col in required_columns:
                    if col == 'Ad Soyad':
                        result_row[col] = search_name  # Aranan ismi yaz
                    else:
                        result_row[col] = ''  # Diğer sütunları boş bırak
                
                results.append(result_row)
                print(f"✗ Bulunamadı: {search_name}")
        
        # Sonuçları yeni Excel dosyasına kaydet
        if results:
            result_df = pd.DataFrame(results)
            output_file = 'sonuc.xlsx'
            result_df.to_excel(output_file, index=False)
            print(f"\n🎉 İşlem tamamlandı! Sonuçlar '{output_file}' dosyasına kaydedildi.")
            print(f"Toplam {len(results)} kayıt işlendi.")
            
            # İstatistikler
            found_count = sum(1 for row in results if any(row[col] for col in required_columns if col != 'Ad Soyad'))
            not_found_count = len(results) - found_count
            print(f"Bulunan: {found_count}, Bulunamayan: {not_found_count}")
        else:
            print("Hiç sonuç bulunamadı!")
    
    except Exception as e:
        print(f"Hata oluştu: {str(e)}")

if __name__ == "__main__":
    print("İsim kontrol ve Excel işleme başlıyor...")
    print("=" * 50)
    process_names()
