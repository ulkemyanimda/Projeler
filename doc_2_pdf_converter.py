import os
import shutil
from pathlib import Path
import comtypes.client
from docx2pdf import convert
import pythoncom
import logging

def setup_logging():
    """Logging yapılandırması"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('conversion_log.txt', encoding='utf-8'),
            logging.StreamHandler()
        ]
    )
    return logging.getLogger(__name__)

def create_folders(base_path):
    """Gerekli klasörleri oluştur"""
    folders = {}
    
    # PDF klasörü
    pdf_folder = os.path.join(base_path, "pdf")
    if not os.path.exists(pdf_folder):
        os.makedirs(pdf_folder)
        print(f"PDF klasörü oluşturuldu: {pdf_folder}")
    folders['pdf'] = pdf_folder
    
    # OK klasörü (başarılı dosyalar için)
    ok_folder = os.path.join(base_path, "ok")
    if not os.path.exists(ok_folder):
        os.makedirs(ok_folder)
        print(f"OK klasörü oluşturuldu: {ok_folder}")
    folders['ok'] = ok_folder
    
    # Hata klasörü
    error_folder = os.path.join(base_path, "hatali")
    if not os.path.exists(error_folder):
        os.makedirs(error_folder)
        print(f"Hata klasörü oluşturuldu: {error_folder}")
    folders['error'] = error_folder
    
    return folders

def convert_doc_to_pdf_word(doc_path, pdf_path):
    """Microsoft Word kullanarak DOC/DOCX'i PDF'e dönüştür"""
    word = None
    try:
        # COM nesnesi başlat
        pythoncom.CoInitialize()
        
        # Dosya yollarını mutlak yol olarak hazırla
        doc_path = os.path.abspath(doc_path)
        pdf_path = os.path.abspath(pdf_path)
        
        # Dosyanın var olup olmadığını kontrol et
        if not os.path.exists(doc_path):
            print(f"Dosya bulunamadı: {doc_path}")
            return False
        
        # Word uygulamasını başlat
        word = comtypes.client.CreateObject('Word.Application')
        word.Visible = False
        word.DisplayAlerts = False  # Uyarıları kapat
        
        # Belgeyi aç - raw string kullan
        doc = word.Documents.Open(doc_path, ReadOnly=True)
        
        # PDF olarak kaydet
        doc.ExportAsFixedFormat(pdf_path, ExportFormat=17)  # ExportAsFixedFormat kullan
        
        # Belgeyi kapat
        doc.Close(SaveChanges=False)
        word.Quit()
        
        # COM nesnesi temizle
        pythoncom.CoUninitialize()
        
        # PDF dosyasının oluştuğunu kontrol et
        if os.path.exists(pdf_path):
            return True
        else:
            return False
        
    except Exception as e:
        print(f"Word ile dönüştürme hatası: {e}")
        try:
            if word:
                word.Quit()
        except:
            pass
        try:
            pythoncom.CoUninitialize()
        except:
            pass
        return False

def convert_docx_to_pdf_direct(docx_path, pdf_path):
    """docx2pdf kütüphanesi ile DOCX'i PDF'e dönüştür"""
    try:
        # Dosya yollarını mutlak yol olarak hazırla
        docx_path = os.path.abspath(docx_path)
        pdf_path = os.path.abspath(pdf_path)
        
        # Dosyanın var olup olmadığını kontrol et
        if not os.path.exists(docx_path):
            print(f"Dosya bulunamadı: {docx_path}")
            return False
        
        # Dönüştürme işlemi
        convert(docx_path, pdf_path)
        
        # PDF dosyasının oluştuğunu kontrol et
        if os.path.exists(pdf_path):
            return True
        else:
            return False
            
    except Exception as e:
        print(f"docx2pdf ile dönüştürme hatası: {e}")
        return False

def sanitize_filename(filename):
    """Dosya adını güvenli hale getir"""
    # Türkçe karakterleri değiştir
    char_map = {
        'ç': 'c', 'Ç': 'C',
        'ğ': 'g', 'Ğ': 'G',
        'ı': 'i', 'I': 'I',
        'ö': 'o', 'Ö': 'O',
        'ş': 's', 'Ş': 'S',
        'ü': 'u', 'Ü': 'U'
    }
    
    for turkish_char, english_char in char_map.items():
        filename = filename.replace(turkish_char, english_char)
    
    # Güvenli olmayan karakterleri temizle
    import re
    filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
    
    return filename

def convert_document_to_pdf(file_path, pdf_folder):
    """Belgeyi PDF'e dönüştür - birden fazla yöntem dene"""
    # Dosya adını güvenli hale getir
    file_name = os.path.splitext(os.path.basename(file_path))[0]
    safe_file_name = sanitize_filename(file_name)
    
    pdf_path = os.path.join(pdf_folder, f"{safe_file_name}.pdf")
    
    # Dosya uzantısını kontrol et
    file_extension = os.path.splitext(file_path)[1].lower()
    
    success = False
    
    print(f"Dosya yolu: {file_path}")
    print(f"PDF yolu: {pdf_path}")
    
    if file_extension == '.docx':
        # DOCX için önce docx2pdf dene
        print(f"DOCX dosyası dönüştürülüyor (docx2pdf): {file_path}")
        success = convert_docx_to_pdf_direct(file_path, pdf_path)
        
        # Başarısız olursa Word ile dene
        if not success:
            print(f"docx2pdf başarısız, Word ile deneniyor: {file_path}")
            success = convert_doc_to_pdf_word(file_path, pdf_path)
    
    elif file_extension == '.doc':
        # DOC için Word kullan
        print(f"DOC dosyası dönüştürülüyor (Word): {file_path}")
        success = convert_doc_to_pdf_word(file_path, pdf_path)
    
    return success

def move_to_folder(file_path, destination_folder, folder_name):
    """Dosyayı belirtilen klasöre taşı"""
    try:
        file_name = os.path.basename(file_path)
        destination = os.path.join(destination_folder, file_name)
        
        # Aynı isimde dosya varsa numara ekle
        counter = 1
        base_name, extension = os.path.splitext(file_name)
        while os.path.exists(destination):
            new_name = f"{base_name}_{counter}{extension}"
            destination = os.path.join(destination_folder, new_name)
            counter += 1
        
        shutil.move(file_path, destination)
        print(f"Dosya {folder_name} klasörüne taşındı: {destination}")
        return True
        
    except Exception as e:
        print(f"Dosya taşıma hatası: {e}")
        return False

def process_folder(folder_path):
    """Klasördeki tüm DOC/DOCX dosyalarını işle"""
    logger = setup_logging()
    
    if not os.path.exists(folder_path):
        print(f"Klasör bulunamadı: {folder_path}")
        return
    
    # Gerekli klasörleri oluştur
    folders = create_folders(folder_path)
    
    # Desteklenen dosya uzantıları
    supported_extensions = ['.doc', '.docx']
    
    # Dosyaları bul (işlem klasörlerini atla)
    files_to_process = []
    for root, dirs, files in os.walk(folder_path):
        # İşlem klasörlerini atla
        if any(folder_name in root for folder_name in ["hatali", "pdf", "ok"]):
            continue
            
        for file in files:
            file_path = os.path.join(root, file)
            file_extension = os.path.splitext(file)[1].lower()
            
            if file_extension in supported_extensions:
                files_to_process.append(file_path)
    
    print(f"Toplam {len(files_to_process)} dosya bulundu")
    
    # İstatistikler
    successful_conversions = 0
    failed_conversions = 0
    
    # Dosyaları işle
    for i, file_path in enumerate(files_to_process, 1):
        print(f"\n[{i}/{len(files_to_process)}] İşleniyor: {os.path.basename(file_path)}")
        
        try:
            # PDF'e dönüştür
            success = convert_document_to_pdf(file_path, folders['pdf'])
            
            if success:
                successful_conversions += 1
                print(f"✓ Başarılı: {os.path.basename(file_path)}")
                logger.info(f"Başarılı dönüştürme: {file_path}")
                
                # Başarılı dosyayı OK klasörüne taşı
                move_to_folder(file_path, folders['ok'], "OK")
            else:
                failed_conversions += 1
                print(f"✗ Başarısız: {os.path.basename(file_path)}")
                logger.error(f"Dönüştürme başarısız: {file_path}")
                
                # Hata klasörüne taşı
                move_to_folder(file_path, folders['error'], "HATALI")
                
        except Exception as e:
            failed_conversions += 1
            print(f"✗ Hata: {os.path.basename(file_path)} - {str(e)}")
            logger.error(f"Genel hata: {file_path} - {str(e)}")
            
            # Hata klasörüne taşı
            move_to_folder(file_path, folders['error'], "HATALI")
    
    # Sonuçları göster
    print(f"\n{'='*50}")
    print(f"İŞLEM TAMAMLANDI")
    print(f"{'='*50}")
    print(f"Toplam dosya: {len(files_to_process)}")
    print(f"Başarılı: {successful_conversions}")
    print(f"Başarısız: {failed_conversions}")
    print(f"Başarı oranı: {(successful_conversions/len(files_to_process)*100):.1f}%")
    
    print(f"\nKlasör düzenlemesi:")
    print(f"- PDF dosyalar: {folders['pdf']}")
    print(f"- Başarılı dosyalar: {folders['ok']}")
    if failed_conversions > 0:
        print(f"- Başarısız dosyalar: {folders['error']}")
    
    print(f"\nDetaylı log: conversion_log.txt")

def main():
    """Ana fonksiyon"""
    print("DOC/DOCX to PDF Converter")
    print("=" * 30)
    
    # Klasör yolunu al
    folder_path = input("Dönüştürülecek dosyaların bulunduğu klasör yolunu girin: ").strip()
    
    # Tırnak işaretlerini temizle
    folder_path = folder_path.strip('"\'')
    
    if not folder_path:
        print("Geçerli bir klasör yolu girmediniz!")
        return
    
    # İşlemi başlat
    process_folder(folder_path)

if __name__ == "__main__":
    main()