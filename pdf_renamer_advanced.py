import os
import re
import random
import string
from pathlib import Path
from PyPDF2 import PdfReader
import logging

# Logging konfigürasyonu
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('pdf_renamer.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)

def temizle_metin(metin):
    """Metinden gereksiz kelimeleri ve karakterleri temizler"""
    if not metin:
        return ""
    
    # "Adı", "Soyadı", "Ad", "Soyad" gibi kelimeleri sil
    metin = re.sub(r"\b(Adı|Soyadı|Ad|Soyad)\b", "", metin, flags=re.IGNORECASE)
    
    # Noktalama işaretlerini ve özel karakterleri sil
    metin = re.sub(r"[^\w\s]", "", metin)
    
    # Fazla boşlukları temizle
    metin = re.sub(r"\s+", " ", metin)
    
    # Başındaki ve sonundaki boşlukları sil
    metin = metin.strip()
    
    # Türkçe karakterleri düzelt
    metin = metin.replace("ı", "i").replace("ş", "s").replace("ğ", "g")
    metin = metin.replace("ü", "u").replace("ö", "o").replace("ç", "c")
    metin = metin.replace("İ", "I").replace("Ş", "S").replace("Ğ", "G")
    metin = metin.replace("Ü", "U").replace("Ö", "O").replace("Ç", "C")
    
    return metin

def guvenli_dosya_adi(ad):
    """Dosya adını güvenli hale getirir"""
    if not ad:
        return "bilinmeyen"
    
    # Dosya adı için geçersiz karakterleri temizle
    gecersiz_karakterler = r'[<>:"/\\|?*]'
    ad = re.sub(gecersiz_karakterler, "", ad)
    
    # Maksimum uzunluk kontrolü
    if len(ad) > 100:
        ad = ad[:100]
    
    # Boşsa varsayılan ad ver
    if not ad.strip():
        ad = "bilinmeyen"
    
    return ad.strip()

def random_sayi_olustur(uzunluk=4):
    """Rastgele sayı oluşturur"""
    return ''.join(random.choices(string.digits, k=uzunluk))

def benzersiz_dosya_adi_olustur(klasor_yolu, temel_ad):
    """Aynı adda dosya varsa sonuna rastgele sayı ekler"""
    temel_ad = guvenli_dosya_adi(temel_ad)
    dosya_adi = f"{temel_ad}.pdf"
    tam_yol = os.path.join(klasor_yolu, dosya_adi)
    
    # Dosya yoksa direkt döndür
    if not os.path.exists(tam_yol):
        return dosya_adi
    
    # Dosya varsa rastgele sayı ekle
    deneme_sayisi = 0
    while deneme_sayisi < 100:  # Sonsuz döngüyü önlemek için
        random_sayi = random_sayi_olustur()
        yeni_dosya_adi = f"{temel_ad}_{random_sayi}.pdf"
        yeni_tam_yol = os.path.join(klasor_yolu, yeni_dosya_adi)
        
        if not os.path.exists(yeni_tam_yol):
            return yeni_dosya_adi
        
        deneme_sayisi += 1
    
    # Eğer 100 deneme sonucu benzersiz ad bulunamadıysa
    timestamp = str(int(random.random() * 1000000))
    return f"{temel_ad}_{timestamp}.pdf"

def pdfden_adi_bul(pdf_path):
    """PDF dosyasından isim bilgisini çıkarır"""
    try:
        # Dosya var mı kontrol et
        if not os.path.exists(pdf_path):
            logging.error(f"Dosya bulunamadı: {pdf_path}")
            return None
        
        # Dosya boyutu kontrol et
        file_size = os.path.getsize(pdf_path)
        if file_size == 0:
            logging.warning(f"Dosya boş: {pdf_path}")
            return None
        
        # PDF okuma
        reader = PdfReader(pdf_path)
        
        # Sayfa sayısı kontrol et
        if len(reader.pages) == 0:
            logging.warning(f"PDF'de sayfa yok: {pdf_path}")
            return None
        
        # Metni çıkarma stratejileri
        metin_parcalari = []
        
        # 1. Strateji: "Adı" kelimesini içeren satırları bul
        for sayfa_no, sayfa in enumerate(reader.pages[:3]):  # İlk 3 sayfayı kontrol et
            try:
                metin = sayfa.extract_text()
                if not metin:
                    continue
                
                satirlar = metin.splitlines()
                for satir in satirlar:
                    if any(kelime in satir for kelime in ["Adı", "Ad", "İsim", "Name"]):
                        temiz_metin = temizle_metin(satir)
                        if temiz_metin and len(temiz_metin) > 2:
                            metin_parcalari.append(temiz_metin)
                            
            except Exception as e:
                logging.warning(f"Sayfa {sayfa_no + 1} okunamadı ({pdf_path}): {e}")
                continue
        
        # 2. Strateji: İlk sayfanın ilk birkaç satırını kontrol et
        if not metin_parcalari:
            try:
                ilk_sayfa = reader.pages[0]
                metin = ilk_sayfa.extract_text()
                if metin:
                    satirlar = metin.splitlines()[:10]  # İlk 10 satır
                    for satir in satirlar:
                        temiz_metin = temizle_metin(satir)
                        if temiz_metin and len(temiz_metin) > 2 and len(temiz_metin) < 50:
                            # Sadece harf ve boşluk içeren satırları al
                            if re.match(r'^[a-zA-ZçÇğĞıIİöÖşŞüÜ\s]+$', temiz_metin):
                                metin_parcalari.append(temiz_metin)
                                break
            except Exception as e:
                logging.warning(f"İlk sayfa stratejisi başarısız ({pdf_path}): {e}")
        
        # En iyi adayı seç
        if metin_parcalari:
            # En kısa ve en anlamlı olanı seç
            en_iyi = min(metin_parcalari, key=len)
            return en_iyi
        
        return None
        
    except Exception as e:
        logging.error(f"PDF okuma hatası ({pdf_path}): {e}")
        return None

def klasordeki_pdflere_isim_ver(klasor_yolu):
    """Klasördeki PDF dosyalarını yeniden adlandırır"""
    
    # Klasör kontrolü
    if not os.path.exists(klasor_yolu):
        logging.error(f"Klasör bulunamadı: {klasor_yolu}")
        return
    
    if not os.path.isdir(klasor_yolu):
        logging.error(f"Belirtilen yol bir klasör değil: {klasor_yolu}")
        return
    
    # PDF dosyalarını bul
    pdf_dosyalari = []
    try:
        for dosya in os.listdir(klasor_yolu):
            if dosya.lower().endswith('.pdf'):
                pdf_dosyalari.append(dosya)
    except PermissionError:
        logging.error(f"Klasöre erişim izni yok: {klasor_yolu}")
        return
    
    if not pdf_dosyalari:
        logging.info(f"Klasörde PDF dosyası bulunamadı: {klasor_yolu}")
        return
    
    logging.info(f"Toplam {len(pdf_dosyalari)} PDF dosyası bulundu")
    
    # İstatistikler
    basarili = 0
    basarisiz = 0
    atlanan = 0
    
    for dosya in pdf_dosyalari:
        try:
            eski_yol = os.path.join(klasor_yolu, dosya)
            logging.info(f"İşleniyor: {dosya}")
            
            # PDF'den isim çıkar
            yeni_ad = pdfden_adi_bul(eski_yol)
            
            if not yeni_ad:
                logging.warning(f"İsim bulunamadı, atlandı: {dosya}")
                atlanan += 1
                continue
            
            # Benzersiz dosya adı oluştur
            yeni_dosya_adi = benzersiz_dosya_adi_olustur(klasor_yolu, yeni_ad)
            yeni_yol = os.path.join(klasor_yolu, yeni_dosya_adi)
            
            # Dosyayı yeniden adlandır
            os.rename(eski_yol, yeni_yol)
            logging.info(f"✓ Başarılı: {dosya} -> {yeni_dosya_adi}")
            basarili += 1
            
        except PermissionError:
            logging.error(f"Dosya erişim izni yok: {dosya}")
            basarisiz += 1
        except FileExistsError:
            logging.error(f"Dosya zaten var: {dosya}")
            basarisiz += 1
        except Exception as e:
            logging.error(f"Beklenmeyen hata ({dosya}): {e}")
            basarisiz += 1
    
    # Sonuçları yazdır
    logging.info(f"\n=== İŞLEM TAMAMLANDI ===")
    logging.info(f"Başarılı: {basarili}")
    logging.info(f"Başarısız: {basarisiz}")
    logging.info(f"Atlanan: {atlanan}")
    logging.info(f"Toplam: {len(pdf_dosyalari)}")

def main():
    """Ana fonksiyon"""
    # Klasör yolunu belirle
    klasor = input("PDF klasörünün yolunu girin (Enter: mevcut klasör): ").strip()
    if not klasor:
        klasor = "."
    
    # Klasörü Path objesi olarak işle
    klasor_path = Path(klasor)
    if not klasor_path.exists():
        print(f"Hata: Klasör bulunamadı: {klasor}")
        return
    
    # Onay al
    print(f"\nKlasör: {klasor_path.absolute()}")
    onay = input("İşleme devam etmek istiyor musunuz? (e/h): ").strip().lower()
    if onay not in ['e', 'evet', 'y', 'yes']:
        print("İşlem iptal edildi.")
        return
    
    # İşlemi başlat
    klasordeki_pdflere_isim_ver(str(klasor_path))

if __name__ == "__main__":
    main()