import os
import base64
import requests
import json
import re

# --- AYARLAR ---
API_URL = "http://127.0.0.1:1234/v1/chat/completions"

# DİKKAT: Metin modelleri (Gemma gibi) görsel işleyemez. 
# LLaVA, Qwen-VL, Moondream veya PaliGemma gibi bir "Vision" modeli kullandığınızdan emin olun.
MODEL_NAME = "llava-v1.5-7b" 

IMAGE_FOLDER = "x"  # İşlenecek görsellerin bulunduğu klasör yolu


def encode_image(image_path):
    with open(image_path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")


def build_prompt():
    return """
Sen bir jüri üyesisin. Aşağıdaki resmi verilen rubriğe göre PUANLA.

SADECE JSON döndür. Başka hiçbir açıklama yapma.

Format:
{
  "tema": int,
  "ozgunluk": int,
  "estetik": int,
  "caba": int,
  "duygu": int,
  "toplam": int
}

RUBRİK:

1. Tema Uygunluğu (30 puan)
2. Özgünlük ve Yaratıcılık (25 puan)
3. Estetik ve Görsel Düzen (20 puan)
4. Yaş Düzeyine Uygun Çaba (15 puan)
5. Duygu ve Anlatım Gücü (10 puan)

Toplam = 100

DİKKAT:
- Her kategori kendi max puanını aşamaz
- Toplamı doğru hesapla
"""


def send_image(image_path):
    base64_img = encode_image(image_path)

    payload = {
        "model": MODEL_NAME,
        "messages": [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": build_prompt()},
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{base64_img}"
                        }
                    }
                ]
            }
        ],
        "temperature": 0.2
    }

    try:
        response = requests.post(API_URL, json=payload)
        response.raise_for_status() # HTTP 400/500 hatalarını yakalar
        
        result_text = response.json()["choices"][0]["message"]["content"]
        
        # LLM'in fazladan ekleyebileceği Markdown (```json ... ```) etiketlerini temizle
        clean_text = re.sub(r"```json", "", result_text, flags=re.IGNORECASE)
        clean_text = re.sub(r"```", "", clean_text)
        clean_text = clean_text.strip()
        
        return json.loads(clean_text)
        
    except requests.exceptions.RequestException as e:
        print(f"[-] API Bağlantı/Yanıt Hatası ({image_path}): {e}")
        if 'response' in locals() and response is not None:
            print(f"    API Detayı: {response.text}")
        return None
    except json.JSONDecodeError:
        print(f"[-] JSON Parse Hatası ({image_path}):")
        print(f"    Modelin ürettiği ham metin:\n{result_text}\n")
        return None
    except Exception as e:
        print(f"[-] Beklenmeyen Hata ({image_path}): {e}")
        return None


def main():
    results = []

    # Klasör kontrolü
    if not os.path.exists(IMAGE_FOLDER):
        print(f"HATA: '{IMAGE_FOLDER}' adında bir klasör bulunamadı. Lütfen IMAGE_FOLDER yolunu kontrol edin.")
        return

    print("Değerlendirme süreci başlatılıyor...\n")

    for root, _, files in os.walk(IMAGE_FOLDER):
        for file in files:
            # Hem küçük hem büyük harf uzantıları yakalamak için
            if file.lower().endswith((".jpg", ".jpeg", ".png")):
                path = os.path.join(root, file)
                print(f"İşleniyor: {file}...")

                score = send_image(path)

                if score:
                    score["file"] = file
                    results.append(score)
                    print(f"  > Başarılı. Toplam Puan: {score.get('toplam', '?')}")
                else:
                    print("  > Başarısız. Bu görsel atlandı.")

    # Eğer hiç sonuç elde edilemediyse programı sonlandır
    if not results:
        print("\nHiçbir görsel başarıyla puanlanamadı. Lütfen yukarıdaki hata mesajlarını inceleyin.")
        return

    # Toplam puana göre azalan sırada sıralama
    results = sorted(results, key=lambda x: x.get("toplam", 0), reverse=True)

    print("\n=== SONUÇLAR ===\n")

    for r in results:
        print(f"{r['file']} -> {r['toplam']} puan")
        print(f"  Tema: {r.get('tema', 0)}")
        print(f"  Özgünlük: {r.get('ozgunluk', 0)}")
        print(f"  Estetik: {r.get('estetik', 0)}")
        print(f"  Çaba: {r.get('caba', 0)}")
        print(f"  Duygu: {r.get('duygu', 0)}\n")

    # JSON Olarak Kaydetme
    output_file = "sonuclar.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
        
    print(f"Değerlendirme tamamlandı. Başarılı sonuçlar '{output_file}' dosyasına kaydedildi.")


if __name__ == "__main__":
    main()