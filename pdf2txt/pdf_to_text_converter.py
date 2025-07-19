import os
import fitz  # PyMuPDF
from pathlib import Path
import time
import json
import shutil

class PDFToTextConverter:
    def __init__(self, folder_path="pdf_files", output_folder="text_output", create_combined_file=True):
        """
        PDFToTextConverter sınıfı. PDF dosyalarını okuyup text dosyalarına dönüştürür.
        
        Args:
            folder_path (str): İşlenecek PDF'lerin bulunduğu klasör.
            output_folder (str): Text dosyalarının kaydedileceği klasör.
            create_combined_file (bool): Toplu dosya oluşturulsun mu?
        """
        self.folder_path = folder_path
        self.output_folder = output_folder
        self.create_combined_file = create_combined_file
        self.combined_file_path = os.path.join(output_folder, "tum_pdfler_birlesik.txt")
        self.combined_content = []
        
        # Alt klasörler
        self.success_folder = os.path.join(folder_path, "processed")
        self.failed_folder = os.path.join(folder_path, "failed")
        self.progress_folder = os.path.join(folder_path, "progress")
        
        # İşlem takibi
        self.failed_files = []
        self.processed_files = set()
        
        # Önceden işlenmiş dosyaları yükle
        self.load_processed_files()
        
    def load_processed_files(self):
        """Önceden işlenmiş dosyaları yükler"""
        try:
            if os.path.exists(self.output_folder):
                # Text klasöründe bulunan .txt dosyalarına karşılık gelen PDF'leri bul
                text_files = list(Path(self.output_folder).glob("*.txt"))
                for txt_file in text_files:
                    # .txt uzantısını .pdf ile değiştir
                    pdf_name = txt_file.stem + ".pdf"
                    self.processed_files.add(pdf_name)
                
                if self.processed_files:
                    print(f"BİLGİ: {len(self.processed_files)} dosya daha önce işlenmiş, bunlar atlanacak.")
        except Exception as e:
            print(f"HATA: Önceden işlenmiş dosyalar yüklenirken hata: {e}")

    def create_folders(self):
        """Gerekli klasörleri oluşturur"""
        try:
            os.makedirs(self.output_folder, exist_ok=True)
            os.makedirs(self.success_folder, exist_ok=True)
            os.makedirs(self.failed_folder, exist_ok=True)
            os.makedirs(self.progress_folder, exist_ok=True)
            print(f"BİLGİ: Klasörler oluşturuldu/kontrol edildi.")
        except Exception as e:
            print(f"HATA: Klasörler oluşturulurken hata: {e}")

    def save_progress(self, current_file, total_files, processed_count):
        """İlerleme bilgisini kaydet"""
        try:
            progress_file = os.path.join(self.progress_folder, "progress.json")
            progress_data = {
                "current_file": current_file,
                "total_files": total_files,
                "processed_count": processed_count,
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                "processed_files": list(self.processed_files)
            }
            with open(progress_file, 'w', encoding='utf-8') as f:
                json.dump(progress_data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"HATA: İlerleme kaydedilirken hata: {e}")

    def move_file(self, source_path, is_success):
        """Dosyayı başarı durumuna göre uygun klasöre taşır"""
        try:
            filename = os.path.basename(source_path)
            destination_folder = self.success_folder if is_success else self.failed_folder
            destination = os.path.join(destination_folder, filename)
            
            if os.path.exists(destination):
                os.remove(destination)
            
            shutil.move(source_path, destination)
            status = "başarılı" if is_success else "başarısız"
            print(f"BİLGİ: '{filename}' dosyası '{os.path.basename(destination_folder)}' klasörüne taşındı.")
        except Exception as e:
            print(f"HATA: '{os.path.basename(source_path)}' dosyası taşınırken hata: {e}")

    def extract_pdf_text(self, pdf_path):
        """PDF'den metin çıkarır"""
        try:
            doc = fitz.open(pdf_path)
            text = ""
            
            # Her sayfayı işle
            for page_num, page in enumerate(doc, 1):
                page_text = page.get_text()
                if page_text.strip():  # Boş sayfaları atla
                    text += f"\n--- SAYFA {page_num} ---\n"
                    text += page_text
                    text += "\n"
            
            doc.close()
            
            if len(text.strip()) > 50:
                return text.strip()
            else:
                print(f"UYARI: '{os.path.basename(pdf_path)}' dosyasından çok az metin çıkarıldı.")
                return None
                
        except Exception as e:
            print(f"HATA: {os.path.basename(pdf_path)} dosyası okunurken hata: {e}")
            return None

    def save_text_to_file(self, text_content, pdf_filename):
        """Metni text dosyasına kaydet ve toplu dosya için hazırla"""
        try:
            # Tekil dosya oluştur
            text_filename = os.path.splitext(pdf_filename)[0] + ".txt"
            text_file_path = os.path.join(self.output_folder, text_filename)
            
            # Başlık bilgisi hazırla
            header = f"PDF Dosyası: {pdf_filename}\n"
            header += f"İşlenme Tarihi: {time.strftime('%Y-%m-%d %H:%M:%S')}\n"
            header += "=" * 50 + "\n\n"
            
            full_content = header + text_content
            
            # Tekil text dosyasına kaydet
            with open(text_file_path, 'w', encoding='utf-8') as f:
                f.write(full_content)
            
            # Toplu dosya için içeriği sakla
            if self.create_combined_file:
                combined_entry = f"\n\n{'='*80}\n"
                combined_entry += f"DOSYA: {pdf_filename}\n"
                combined_entry += f"İŞLENME TARİHİ: {time.strftime('%Y-%m-%d %H:%M:%S')}\n"
                combined_entry += f"{'='*80}\n\n"
                combined_entry += text_content
                combined_entry += f"\n\n{'='*80}\n"
                combined_entry += f"DOSYA SONU: {pdf_filename}\n"
                combined_entry += f"{'='*80}\n"
                
                self.combined_content.append(combined_entry)
            
            print(f"BİLGİ: '{text_filename}' dosyası oluşturuldu.")
            return True
            
        except Exception as e:
            print(f"HATA: Text dosyası kaydedilirken hata: {e}")
            return False

    def process_pdf(self, pdf_path):
        """Tek bir PDF'yi işler"""
        filename = os.path.basename(pdf_path)
        
        if filename in self.processed_files:
            print(f"ATLANDI: '{filename}' daha önce işlenmiş.")
            return True
        
        print(f"\nİşleniyor: {filename}")

        # PDF'den metin çıkar
        text_content = self.extract_pdf_text(pdf_path)
        if not text_content:
            self.failed_files.append((filename, "PDF Metin Çıkarma Hatası"))
            self.move_file(pdf_path, False)
            return False

        # Text dosyasına kaydet
        if self.save_text_to_file(text_content, filename):
            print(f"BAŞARILI: '{filename}' text dosyasına dönüştürüldü.")
            self.processed_files.add(filename)
            self.move_file(pdf_path, True)
            return True
        else:
            self.failed_files.append((filename, "Text Dosyası Kaydetme Hatası"))
            self.move_file(pdf_path, False)
            return False

    def save_combined_file(self):
        """Tüm PDF'lerin içeriğini tek bir dosyada birleştir"""
        if not self.create_combined_file or not self.combined_content:
            return
        
        try:
            with open(self.combined_file_path, 'w', encoding='utf-8') as f:
                # Dosya başlığı
                f.write("TÜM PDF DOSYALARI - BİRLEŞİK İÇERİK\n")
                f.write(f"Oluşturulma Tarihi: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"Toplam PDF Sayısı: {len(self.combined_content)}\n")
                f.write("="*100 + "\n")
                f.write("İÇİNDEKİLER:\n")
                
                # İçindekiler tablosu
                for i, content in enumerate(self.combined_content, 1):
                    # Dosya adını içerikten çıkar
                    lines = content.split('\n')
                    for line in lines:
                        if line.startswith("DOSYA: "):
                            filename = line.replace("DOSYA: ", "")
                            f.write(f"{i:3}. {filename}\n")
                            break
                
                f.write("="*100 + "\n")
                
                # Tüm içerikleri birleştir
                for content in self.combined_content:
                    f.write(content)
            
            print(f"\nBİLGİ: Birleşik dosya oluşturuldu: '{os.path.basename(self.combined_file_path)}'")
            print(f"Toplam {len(self.combined_content)} PDF'in içeriği birleştirildi.")
            
        except Exception as e:
            print(f"HATA: Birleşik dosya oluşturulurken hata: {e}")

    def process_all_pdfs(self):
        """Tüm PDF'leri işler"""
        self.create_folders()
        
        # PDF dosyalarını bul
        pdf_files = list(Path(self.folder_path).glob("*.pdf"))
        if not pdf_files:
            print(f"UYARI: '{self.folder_path}' klasöründe işlenecek PDF dosyası bulunamadı.")
            return

        # İşlenmemiş dosyaları filtrele
        unprocessed_files = [f for f in pdf_files if f.name not in self.processed_files]
        if not unprocessed_files:
            print("BİLGİ: Tüm PDF dosyaları daha önce işlenmiş.")
            return

        print(f"Toplam {len(pdf_files)} PDF dosyası bulundu.")
        print(f"Bunlardan {len(unprocessed_files)} tanesi işlenecek.")
        print("İşlem başlatılıyor...\n")
        
        total_to_process = len(unprocessed_files)
        successful_count = 0
        
        for i, pdf_file in enumerate(unprocessed_files, 1):
            print(f"\n--- İşlem {i}/{total_to_process} ---")
            
            try:
                if self.process_pdf(str(pdf_file)):
                    successful_count += 1
                
                self.save_progress(pdf_file.name, len(pdf_files), len(self.processed_files))
                
            except KeyboardInterrupt:
                print("\n\nİŞLEM KULLANICI TARAFINDAN DURDURULDU!")
                break
            except Exception as e:
                print(f"HATA: '{pdf_file.name}' işlenirken beklenmeyen hata: {e}")
                self.failed_files.append((pdf_file.name, f"Beklenmeyen Hata: {e}"))
            
            # Kısa bir bekleme (isteğe bağlı)
            if i < total_to_process:
                time.sleep(0.1)
        """Tüm PDF'leri işler"""
        self.create_folders()
        
        # PDF dosyalarını bul
        pdf_files = list(Path(self.folder_path).glob("*.pdf"))
        if not pdf_files:
            print(f"UYARI: '{self.folder_path}' klasöründe işlenecek PDF dosyası bulunamadı.")
            return

        # İşlenmemiş dosyaları filtrele
        unprocessed_files = [f for f in pdf_files if f.name not in self.processed_files]
        if not unprocessed_files:
            print("BİLGİ: Tüm PDF dosyaları daha önce işlenmiş.")
            return

        print(f"Toplam {len(pdf_files)} PDF dosyası bulundu.")
        print(f"Bunlardan {len(unprocessed_files)} tanesi işlenecek.")
        print("İşlem başlatılıyor...\n")
        
        total_to_process = len(unprocessed_files)
        successful_count = 0
        
        for i, pdf_file in enumerate(unprocessed_files, 1):
            print(f"\n--- İşlem {i}/{total_to_process} ---")
            
            try:
                if self.process_pdf(str(pdf_file)):
                    successful_count += 1
                
                self.save_progress(pdf_file.name, len(pdf_files), len(self.processed_files))
                
            except KeyboardInterrupt:
                print("\n\nİŞLEM KULLANICI TARAFINDAN DURDURULDU!")
                break
            except Exception as e:
                print(f"HATA: '{pdf_file.name}' işlenirken beklenmeyen hata: {e}")
                self.failed_files.append((pdf_file.name, f"Beklenmeyen Hata: {e}"))
            
            # Kısa bir bekleme (isteğe bağlı)
            if i < total_to_process:
                time.sleep(0.1)
        
        # Özet raporu
        print("\n" + "="*60)
        print("İŞLEM TAMAMLANDI")
        print("="*60)
        print(f"ÖZET: {successful_count} PDF başarıyla text dosyasına dönüştürüldü.")
        print(f"Başarısız: {len(self.failed_files)} PDF.")
        print(f"Text dosyaları '{self.output_folder}' klasöründe kaydedildi.")
        
        # Birleşik dosyayı oluştur
        if successful_count > 0:
            self.save_combined_file()
        
        if self.failed_files:
            print("\n--- Başarısız Olan Dosyalar ve Nedenleri ---")
            for filename, reason in self.failed_files:
                print(f"- {filename}: {reason}")
        
        print(f"\nİşlenmiş PDF'ler: '{self.success_folder}' klasörüne taşındı.")
        print(f"Başarısız PDF'ler: '{self.failed_folder}' klasörüne taşındı.")

def main():
    print("PDF to Text Converter")
    print("="*50)
    
    # Klasör ayarları
    pdf_folder = "pdf_files"  # PDF'lerin bulunduğu klasör
    text_output_folder = "text_output"  # Text dosyalarının kaydedileceği klasör
    
    print(f"PDF Klasörü: {pdf_folder}")
    print(f"Text Çıktı Klasörü: {text_output_folder}")
    
    try:
        converter = PDFToTextConverter(
            folder_path=pdf_folder,
            output_folder=text_output_folder,
            create_combined_file=True  # Birleşik dosya oluştur
        )
        converter.process_all_pdfs()
    except Exception as e:
        print(f"HATA: Program çalıştırılırken hata oluştu: {e}")

if __name__ == "__main__":
    main()
