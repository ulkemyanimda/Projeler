import fitz  # PyMuPDF
import pytesseract
from PIL import Image
import re
import os
from pathlib import Path

def extract_images_by_coordinates(pdf_path, output_dir="extracted_images", start_page=160):
    """
    Belirtilen koordinatlardaki 6 resmi çıkarır ve altlarındaki metinlerle kaydeder
    
    Args:
        pdf_path (str): PDF dosyasının yolu
        output_dir (str): Çıkarılan resimlerin kaydedileceği klasör
        start_page (int): İşleme başlanacak sayfa numarası
    """
    
    # 6 resim için koordinatlar (analiz sonuçlarından alındı)
    image_coordinates = [
        # Resim 1 (Sol üst) - "ben"
        {"rect": (68.53, 99.00, 204.71, 215.27), "text_area": (124.51, 213.50, 146.19, 231.25)},
        
        # Resim 2 (Sağ üst) - "sen" 
        {"rect": (223.41, 97.98, 360.58, 215.32), "text_area": (283.62, 213.50, 304.57, 231.25)},
        
        # Resim 3 (Sol orta) - "siz"
        {"rect": (68.53, 250.31, 204.70, 367.61), "text_area": (127.41, 518.94, 143.30, 536.68)},
        
        # Resim 4 (Sağ orta) - "biz"
        {"rect": (223.32, 250.33, 360.54, 367.65), "text_area": (285.79, 365.87, 302.40, 383.61)},
        
        # Resim 5 (Sol alt) - koordinat ile eşleştirme gerekli
        {"rect": (68.53, 403.43, 202.96, 520.67), "text_area": (68.53, 520.67, 202.96, 540.00)},
        
        # Resim 6 (Sağ alt) - "onlar"
        {"rect": (224.44, 403.45, 360.00, 520.77), "text_area": (279.64, 518.94, 308.54, 536.68)}
    ]
    
    # Çıktı klasörünü oluştur
    Path(output_dir).mkdir(exist_ok=True)
    
    # PDF'yi aç
    doc = fitz.open(pdf_path)
    
    print(f"Toplam sayfa sayısı: {len(doc)}")
    print(f"Sayfa {start_page} ve sonrasından işlem başlatılıyor...")
    
    for page_num in range(start_page - 1, len(doc)):
        page = doc[page_num]
        
        print(f"\nSayfa {page_num + 1} işleniyor...")
        
        # Her koordinat için resim çıkar
        for img_index, coord in enumerate(image_coordinates):
            # Resim alanını belirle
            img_rect = fitz.Rect(coord["rect"])
            text_rect = fitz.Rect(coord["text_area"])
            
            try:
                # Resmi çıkar (yüksek çözünürlük)
                mat = fitz.Matrix(3, 3)  # 3x zoom
                pix = page.get_pixmap(matrix=mat, clip=img_rect)
                
                # RGB formatına çevir
                if pix.n - pix.alpha < 4:
                    img_data = pix.tobytes("png")
                else:
                    pix_rgb = fitz.Pixmap(fitz.csRGB, pix)
                    img_data = pix_rgb.tobytes("png")
                    pix_rgb = None
                
                # Metin etiketini al
                label_text = page.get_textbox(text_rect).strip()
                
                # Etiket temizle
                if label_text:
                    # İlk kelimeyi al
                    label = label_text.split('\n')[0].split()[0] if label_text.split() else f"resim_{img_index + 1}"
                else:
                    label = f"resim_{img_index + 1}"
                
                # Dosya adını temizle
                label = clean_filename(label)
                
                # Resmi kaydet
                filename = f"{label}_{page_num+1}_{img_index+1}.png"
                output_path = os.path.join(output_dir, filename)
                
                with open(output_path, "wb") as f:
                    f.write(img_data)
                
                print(f"  ✓ Kaydedildi: {filename} (Etiket: {label})")
                
                pix = None
                
            except Exception as e:
                print(f"  ✗ Hata (resim {img_index + 1}): {str(e)}")
    
    doc.close()
    print("\nİşlem tamamlandı!")

def analyze_page_layout(pdf_path, page_number):
    """
    Belirli bir sayfayı analiz ederek koordinatları bulmanıza yardımcı olur
    """
    doc = fitz.open(pdf_path)
    page = doc[page_number - 1]
    
    print(f"Sayfa {page_number} analizi:")
    print(f"Sayfa boyutları: {page.rect}")
    
    # Sayfadaki resimleri listele
    image_list = page.get_images()
    print(f"\nBulunan resim sayısı: {len(image_list)}")
    
    for i, img in enumerate(image_list):
        img_rects = page.get_image_rects(img[0])
        if img_rects:
            for j, rect in enumerate(img_rects):
                print(f"Resim {i+1}.{j+1}: {rect}")
    
    # Sayfadaki metinleri listele
    blocks = page.get_text("dict")
    print(f"\nSayfadaki metin blokları:")
    for block in blocks["blocks"]:
        if "lines" in block:
            for line in block["lines"]:
                for span in line["spans"]:
                    text = span["text"].strip()
                    if text and len(text) > 2:
                        bbox = span["bbox"]
                        print(f"Metin: '{text}' - Konum: {bbox}")
    
    doc.close()

def clean_filename(filename):
    """
    Dosya adını temizle (özel karakterleri kaldır)
    """
    # Türkçe karakterleri koru, diğer özel karakterleri kaldır
    filename = re.sub(r'[<>:"/\\|?*]', '', filename)
    filename = filename.replace(' ', '_')
    return filename[:50]  # Maksimum 50 karakter

# Manuel koordinat belirleme için yardımcı fonksiyon
def find_coordinates_interactively(pdf_path, page_number):
    """
    Bir sayfayı analiz ederek koordinatları bulmanıza yardımcı olur
    """
    print("=== KOORDİNAT BULMA YARDIMCISI ===")
    print("Bu fonksiyon ile sayfadaki resim ve metin konumlarını görebilirsiniz.")
    print("Sonuçları kullanarak image_coordinates listesini güncelleyebilirsiniz.\n")
    
    analyze_page_layout(pdf_path, page_number)
    
    print("\n=== KOORDİNAT GÜNCELLEME REHBERİ ===")
    print("1. Yukarıdaki sonuçları kullanarak image_coordinates listesini güncelleyin")
    print("2. Her resim için 'rect' (resim alanı) ve 'text_area' (metin alanı) belirleyin")
    print("3. Koordinat formatı: (x0, y0, x1, y1)")
    print("   - x0, y0: Sol üst köşe")
    print("   - x1, y1: Sağ alt köşe")
    
    return True

# Kullanım örneği
if __name__ == "__main__":
    import io
    
    # PDF dosya yolunu buraya gir
    pdf_file = "your_pdf_file.pdf"  # PDF dosyanızın yolunu buraya yazın
    start_page = 160  # Başlangıç sayfası
    
    print("=== PDF RESİM ÇIKARICI ===\n")
    
    # Önce bir sayfayı analiz edin (koordinatları bulmak için)
    print("1. ADIM: Koordinat analizi")
    print("Önce bir örnek sayfayı analiz edelim...")
    
    # Örnek sayfa analizi (koordinatları bulmak için)
    try:
        find_coordinates_interactively(pdf_file, start_page)
    except Exception as e:
        print(f"Analiz hatası: {e}")
        print("PDF dosya yolunu kontrol edin veya farklı bir sayfa deneyin.")
    
    print(f"\n2. ADIM: Resim çıkarma")
    print("Koordinatları ayarladıktan sonra resim çıkarma işlemi:")
    print("extract_images_by_coordinates(pdf_file, 'extracted_images', start_page)")
    
    # Koordinatları ayarladıktan sonra bu satırı açın:
    extract_images_by_coordinates(pdf_file, "extracted_images", start_page)

# Gerekli kütüphaneleri yüklemek için:
# pip install PyMuPDF pillow pytesseract

# KULLANIM ADIMLARı:
# 1. PDF dosya yolunu 'pdf_file' değişkenine yazın
# 2. Kodu çalıştırın - önce koordinat analizi yapacak
# 3. Analiz sonuçlarına göre 'image_coordinates' listesini güncelleyin
# 4. Son satırdaki yorum işaretini kaldırıp tekrar çalıştırın