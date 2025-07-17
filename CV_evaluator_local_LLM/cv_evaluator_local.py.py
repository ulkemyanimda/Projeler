import os
import pandas as pd
import fitz  # PyMuPDF
from pathlib import Path
import json
import re
import shutil
import requests
import time

class CVEvaluator:
    def __init__(self, api_base_url="[http://127.0.0.1:1234](http://127.0.0.1:1234)", model_name="gemma-3-4b-it", folder_path="cv_dosyalari", excel_file="cv_degerlendirme.xlsx", timeout=120):
        """
        CVEvaluator sınıfı. Yerel API serverını kullanarak CV'leri işler.
        
        Args:
            api_base_url (str): Yerel API serverının adresi
            model_name (str): Kullanılacak model adı
            folder_path (str): İşlenecek PDF'lerin bulunduğu klasör.
            excel_file (str): Sonuçların kaydedileceği Excel dosyasının adı.
            timeout (int): API isteği için saniye cinsinden zaman aşımı süresi.
        """
        self.api_base_url = api_base_url.rstrip('/')
        self.model_name = model_name
        self.folder_path = folder_path
        self.excel_file = excel_file
        self.timeout = timeout
        
        self.chat_url = f"{self.api_base_url}/v1/chat/completions"
        self.models_url = f"{self.api_base_url}/v1/models"
        
        self.test_api_connection()
        
        self.success_folder = os.path.join(folder_path, "okey")
        self.failed_folder = os.path.join(folder_path, "notokey")
        self.progress_folder = os.path.join(folder_path, "progress")
        
        self.excel_headers = [
            "Dosya Adı", "Ad Soyad", "TC Kimlik No", "Telefon Numarası", "E-posta Adresi",
            "Branş", "Şu Anda Görev Yaptığı Okul", "Görev Yaptığı İl İlçe",
            "TÖMER Belgesi", "Yurtdışı Görev", "Doktora/Yüksek Lisans", "Doktora/Yüksek Lisans Konusu",
            "Genel Değerlendirme"
        ]
        
        self.column_mapping = {
            "dosya_adi": "Dosya Adı", "ad_soyad": "Ad Soyad", "tc_kimlik_no": "TC Kimlik No",
            "telefon_numarasi": "Telefon Numarası", "eposta_adresi": "E-posta Adresi",
            "brans": "Branş", "su_anda_gorev_yaptigi_okul": "Şu Anda Görev Yaptığı Okul",
            "gorev_yaptigi_il_ilce": "Görev Yaptığı İl İlçe",
            "tomer_belgesi": "TÖMER Belgesi", "yurtdisi_gorev": "Yurtdışı Görev",
            "doktora_yuksek_lisans": "Doktora/Yüksek Lisans",
            "doktora_yuksek_lisans_konusu": "Doktora/Yüksek Lisans Konusu",
            "genel_degerlendirme": "Genel Değerlendirme"
        }
        
        self.failed_files = []
        self.processed_files = set()
        
        self.initialize_excel()

    def test_api_connection(self):
        """API bağlantısını test eder"""
        try:
            print(f"BİLGİ: API bağlantısı test ediliyor: {self.api_base_url}")
            response = requests.get(self.models_url, timeout=10)
            if response.status_code == 200:
                models_data = response.json()
                print("BİLGİ: API bağlantısı başarılı!")
                if 'data' in models_data:
                    available_models = [model['id'] for model in models_data['data']]
                    print(f"BİLGİ: Mevcut modeller: {available_models}")
                    if self.model_name in available_models:
                        print(f"BİLGİ: Seçilen model '{self.model_name}' kullanılabilir.")
                    else:
                        print(f"UYARI: Seçilen model '{self.model_name}' listede yok, yine de denenecek.")
            else:
                print(f"HATA: API bağlantısı başarısız. Status code: {response.status_code}")
                raise Exception(f"API bağlantı hatası: {response.status_code}")
        except requests.exceptions.RequestException as e:
            print(f"HATA: API bağlantısı test edilirken hata: {e}")
            print("BİLGİ: Lütfen yerel API serverınızın çalıştığından emin olun.")
            raise

    def initialize_excel(self):
        """Excel dosyasını başlat ve önceden işlenmiş dosyaları yükle"""
        try:
            if os.path.exists(self.excel_file):
                df = pd.read_excel(self.excel_file)
                if not df.empty and "Dosya Adı" in df.columns:
                    self.processed_files = set(df["Dosya Adı"].tolist())
                    print(f"BİLGİ: {len(self.processed_files)} dosya daha önce işlenmiş, bunlar atlanacak.")
                else:
                    df = pd.DataFrame(columns=self.excel_headers)
                    df.to_excel(self.excel_file, index=False)
            else:
                df = pd.DataFrame(columns=self.excel_headers)
                df.to_excel(self.excel_file, index=False)
                print(f"BİLGİ: Yeni Excel dosyası oluşturuldu: {self.excel_file}")
        except Exception as e:
            print(f"HATA: Excel dosyası başlatılırken hata: {e}")
            df = pd.DataFrame(columns=self.excel_headers)
            df.to_excel(self.excel_file, index=False)

    def append_to_excel(self, cv_data):
        """Yeni CV verisini Excel dosyasına ekler"""
        try:
            df = pd.read_excel(self.excel_file)
            new_row = {self.column_mapping.get(key, key): value for key, value in cv_data.items()}
            
            # DataFrame'e satır eklemenin modern yolu
            df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
            
            df.to_excel(self.excel_file, index=False)
            print(f"BİLGİ: '{cv_data.get('dosya_adi', 'Bilinmeyen')}' Excel dosyasına eklendi.")
        except Exception as e:
            print(f"HATA: Excel dosyasına ekleme hatası: {e}")

    def create_folders(self):
        """Gerekli klasörleri oluşturur"""
        try:
            os.makedirs(self.success_folder, exist_ok=True)
            os.makedirs(self.failed_folder, exist_ok=True)
            os.makedirs(self.progress_folder, exist_ok=True)
            print(f"BİLGİ: Klasörler oluşturuldu/kontrol edildi.")
        except Exception as e:
            print(f"HATA (Klasör): Klasörler oluşturulurken hata: {e}")

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
            print(f"BİLGİ: '{filename}' dosyası '{os.path.basename(destination_folder)}' klasörüne taşındı.")
        except Exception as e:
            print(f"HATA (Dosya Taşıma): '{os.path.basename(source_path)}' dosyası taşınırken hata: {e}")

    def extract_pdf_text(self, pdf_path):
        """PDF'den metin çıkarır"""
        try:
            doc = fitz.open(pdf_path)
            text = "".join(page.get_text() for page in doc)
            doc.close()
            if len(text.strip()) > 50: # Daha anlamlı bir metin kontrolü
                return text
            else:
                print(f"UYARI: '{os.path.basename(pdf_path)}' dosyasından çok az metin çıkarıldı (muhtemelen resim tabanlı bir PDF).")
                return None
        except Exception as e:
            print(f"HATA (PDF Okuma): {os.path.basename(pdf_path)} dosyası okunurken hata: {e}")
            return None

    def create_cv_prompt(self, cv_text):
        """CV analizi için prompt oluşturur"""
        if len(cv_text) > 7000: # Limiti biraz artıralım
            cv_text = cv_text[:7000] + "..."
        
        return f"""Sen bir CV analiz uzmanısın. Aşağıdaki CV metnini analiz et ve istenen bilgileri JSON formatında çıkar.

CV Metni:
{cv_text}

Lütfen aşağıdaki bilgileri çıkar ve SADECE JSON formatında yanıtla. Başka hiçbir metin, açıklama veya markdown bloğu ekleme:

{{
  "ad_soyad": "Kişinin tam adı",
  "tc_kimlik_no": "TC kimlik numarası (varsa)",
  "telefon_numarasi": "Telefon numarası (varsa)",
  "eposta_adresi": "E-posta adresi (varsa)",
  "brans": "Öğretmenlik branşı veya uzmanlık alanı",
  "su_anda_gorev_yaptigi_okul": "Mevcut çalıştığı okul/kurum",
  "gorev_yaptigi_il_ilce": "Mevcut görev yaptığı yerin İl ve İlçe bilgisi",
  "tomer_belgesi": "TÖMER belgesi var mı? (Evet/Hayır)",
  "yurtdisi_gorev": "Daha önce yurtdışında görev yapmış mı? (Evet/Hayır)",
  "doktora_yuksek_lisans": "Doktora veya Yüksek Lisans yapmış mı? (Doktora/Yüksek Lisans/Hayır)",
  "doktora_yuksek_lisans_konusu": "Eğer yapmışsa, Doktora veya Yüksek Lisans tezinin konusu/alanı",
  "genel_degerlendirme": "CV hakkında 3-4 cümlelik özet. Erasmus, e-Twinning, TÜBİTAK, PİKTES projelerini özellikle belirt."
}}

Bulunamayan bilgiler için "Belirtilmemiş" yaz. Sadece JSON formatında yanıtla, başka açıklama ekleme."""

    def query_local_api(self, prompt):
        """Yerel API'ye istek gönderir"""
        try:
            print("BİLGİ: Yerel API'ye istek gönderiliyor...")
            payload = {
                "model": self.model_name,
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.1,
                "max_tokens": 1500, # Daha uzun değerlendirmeler için artırılabilir
                "stream": False
            }
            headers = {"Content-Type": "application/json"}
            
            response = requests.post(self.chat_url, json=payload, headers=headers, timeout=self.timeout)
            
            if response.status_code == 200:
                result = response.json()
                if 'choices' in result and len(result['choices']) > 0:
                    content = result['choices'][0]['message']['content']
                    print("BİLGİ: Yerel API'den başarılı yanıt alındı.")
                    return content
                else:
                    print(f"HATA: API yanıtında 'choices' bulunamadı. Yanıt: {result}")
                    return None
            else:
                print(f"HATA: API isteği başarısız. Status code: {response.status_code}\nYanıt: {response.text}")
                return None
        except requests.exceptions.Timeout:
            print(f"HATA: API isteği zaman aşımına uğradı ({self.timeout}s)")
            return None
        except requests.exceptions.RequestException as e:
            print(f"HATA: API isteği sırasında hata: {e}")
            return None

    def parse_json_response(self, response_text):
        """API yanıtını JSON olarak ayrıştırır (Markdown bloklarına karşı dayanıklı)"""
        if not response_text:
            print("HATA (JSON): Ayrıştırılacak yanıt metni boş.")
            return None

        # re.DOTALL, '.' karakterinin yeni satırları da içermesini sağlar.
        json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
        
        if json_match:
            json_str = json_match.group(0)
            try:
                return json.loads(json_str)
            except json.JSONDecodeError as e:
                print(f"HATA (JSON): JSON bloğu bulundu ancak ayrıştırılamadı: {e}")
                print(f"Ayrıştırılmaya çalışılan metin (ilk 200 karakter): {json_str[:200]}...")
                return None
        else:
            print("HATA (JSON): Yanıt içinde JSON formatı bulunamadı.")
            print(f"Alınan Ham Yanıt: {response_text}")
            return None

    def process_cv(self, pdf_path):
        """Tek bir CV'yi işler"""
        filename = os.path.basename(pdf_path)
        
        if filename in self.processed_files:
            print(f"ATLANDI: '{filename}' daha önce işlenmiş.")
            return None
        
        print(f"\nİşleniyor: {filename}")

        cv_text = self.extract_pdf_text(pdf_path)
        if not cv_text:
            self.failed_files.append((filename, "PDF Metin Çıkarma Hatası"))
            self.move_file(pdf_path, False)
            return None

        prompt = self.create_cv_prompt(cv_text)
        response_text = self.query_local_api(prompt)
        if not response_text:
            self.failed_files.append((filename, "API Sorgu Hatası"))
            self.move_file(pdf_path, False)
            return None

        cv_data = self.parse_json_response(response_text)
        if not cv_data:
            self.failed_files.append((filename, "JSON Parse Hatası"))
            self.move_file(pdf_path, False)
            return None

        print(f"BAŞARILI: '{filename}' için veriler ayrıştırıldı.")
        cv_data["dosya_adi"] = filename
        
        self.append_to_excel(cv_data)
        self.processed_files.add(filename)
        self.move_file(pdf_path, True)
        return cv_data

    def process_all_cvs(self):
        """Tüm CV'leri işler"""
        self.create_folders()
        
        pdf_files = list(Path(self.folder_path).glob("*.pdf"))
        if not pdf_files:
            print(f"UYARI: '{self.folder_path}' klasöründe işlenecek PDF dosyası bulunamadı.")
            return

        unprocessed_files = [f for f in pdf_files if f.name not in self.processed_files]
        if not unprocessed_files:
            print("BİLGİ: Tüm PDF dosyaları daha önce işlenmiş.")
            return

        print(f"Toplam {len(pdf_files)} PDF dosyası bulundu. Bunlardan {len(unprocessed_files)} tanesi işlenecek.")
        print("İşlem başlatılıyor...")
        
        total_to_process = len(unprocessed_files)
        initial_processed_count = len(self.processed_files)
        
        for i, pdf_file in enumerate(unprocessed_files, 1):
            print(f"\n--- İşlem {i}/{total_to_process} ---")
            
            try:
                self.process_cv(str(pdf_file))
                current_processed_count = initial_processed_count + i - len(self.failed_files)
                self.save_progress(pdf_file.name, len(pdf_files), current_processed_count)
                
            except KeyboardInterrupt:
                print("\n\nİŞLEM KULLANICI TARAFINDAN DURDURULDU!")
                break
            except Exception as e:
                print(f"HATA: '{pdf_file.name}' işlenirken beklenmeyen hata: {e}")
                self.failed_files.append((pdf_file.name, f"Beklenmeyen Hata: {e}"))
            
            if i < total_to_process:
                time.sleep(1) # API'ye yük bindirmemek için bekleme
        
        print("\n" + "="*50 + "\nİŞLEM TAMAMLANDI\n" + "="*50)
        successful_count = len(self.processed_files) - initial_processed_count
        print(f"ÖZET: {successful_count} CV başarıyla işlendi, {len(self.failed_files)} CV başarısız oldu.")
        print(f"Sonuçlar '{self.excel_file}' dosyasına kaydedildi.")
        
        if self.failed_files:
            print("\n--- Başarısız Olan Dosyalar ve Nedenleri ---")
            for filename, reason in self.failed_files:
                print(f"- {filename}: {reason}")

#################################################################
# --------------- ANA ÇALIŞTIRMA BÖLÜMÜ ----------------------- #
#################################################################
def main():
    print("CV Evaluator - Yerel API Server Sürümü")
    print("="*50)
    
    # Yerel API ayarları
    # BU SATIRIN DOĞRU OLDUĞUNDAN EMİN OLUN:
    api_base_url = "http://127.0.0.1:1234"
    
    model_name = "gemma-3-4b-it"
    
    # İşlenecek CV'lerin bulunduğu klasörün adını belirtin
    cv_folder = "cv_dosyalari"
    
    print(f"API Adresi: {api_base_url}")
    print(f"Model: {model_name}")
    print(f"CV Klasörü: {cv_folder}")
    
    try:
        evaluator = CVEvaluator(
            api_base_url=api_base_url,
            model_name=model_name,
            folder_path=cv_folder
        )
        evaluator.process_all_cvs()
    except Exception as e:
        print(f"HATA: Program çalıştırılırken hata oluştu: {e}")

if __name__ == "__main__":
    main()
