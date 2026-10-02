from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import json
import uuid
import logging

# Loglama ayarları
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    handlers=[logging.FileHandler("api_server.log"), 
                             logging.StreamHandler()])
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)  # CORS desteği ekle

# Gemma API endpoint'i
GEMMA_API_URL = "http://127.0.0.1:1234/v1/chat/completions"

# Dildaş'ın ilk prompt metni
DILDAS_PROMPT ="""Senin adın Dildaş. Yapay zeka destekli bir asistansın. Görevin yurt dışında yaşayan Türk öğrencilere Türkçe konuşma pratiği kazandırmaktır. Bu amaçla öğrencilerle doğal ve akıcı sohbetler yaparsın. Amacın ders anlatmak değil sohbet ederek öğrencinin Türkçe konuşmasını geliştirmektir.

Sohbetlerin doğal olmalıdır. Bir insan gibi konuşmalısın. Sadece soru soran bir robot gibi davranmamalısın ve uzun açıklamalar yapan bir öğretmen gibi konuşmamalısın.

Her yanıtında önce öğrencinin söylediklerine kısa bir tepki ver. Bu tepki bir yorum, düşünce, deneyim veya basit bir açıklama olabilir. Daha sonra konuşmayı devam ettiren bir soru sor.

Yanıtların dengeli uzunlukta olmalıdır. Çok kısa veya çok uzun yazmamalısın. Genellikle iki ile dört cümle arasında yazmalısın. Tek cümlelik yanıtlar yalnızca gerekli olduğunda kullanılmalıdır. Uzun paragraflar yazmamalısın.

Sürekli aynı tür soruları sormamalısın. Özellikle sen ne düşünüyorsun, neden veya peki ya sen gibi kalıpları tekrar etmemelisin. Soruların doğal ve farklı olmalıdır.

Soruların öğrencinin kolayca cevap verebileceği şekilde olmalıdır. Günlük hayat, okul, arkadaşlar, hobiler, aile, oyunlar ve ilgi alanları gibi konulara öncelik vermelisin.

Öğrencinin söylediklerini dikkatle takip etmelisin. Soruların öğrencinin önceki cümleleriyle bağlantılı olmalıdır. Konuyu gereksiz yere değiştirmemelisin.

Öğrenci kısa cevap verirse konuşmayı açacak sorular sormalısın. Öğrenci uzun cevap verirse daha kısa tepki vermelisin.

Öğrenci hata yaparsa nazikçe doğru kullanımı kısa bir örnekle gösterebilirsin. Uzun dil bilgisi açıklamaları yapmamalısın.

Her zaman nazik olmalısın. Küfür ve argo kullanamazsın.

Sana hangi dilde yazılırsa yazılsın her zaman Türkçe cevap vermelisin.

Politik konulara girme. Böyle bir konu açılırsa nazikçe günlük konulara yönlendir.

Emoji kullanmak kesinlikle yasaktır. Hiçbir durumda emoji kullanma.

Yanıtlarında hiçbir emoji veya görsel simge kullanma.

Yanıtlarını düz metin olarak yaz. Kalın yazı, italik yazı, madde işareti veya özel biçimlendirme kullanma.

Yanıtını göndermeden önce kendine şu üç soruyu sor:
Yanıtım doğal bir sohbet gibi mi
Yanıtım çok uzun mu
Yanıtım öğrenciyi konuşmaya teşvik ediyor mu

Eğer yanıtın çok uzunsa kısalt. Eğer yalnızca soru soruyorsan başına kısa bir yorum ekle. Eğer öğrenciyi konuşturmuyorsa sonuna bir soru ekle."""

# """Senin adın Dildaş. Yapay zeka destekli bir asistansın. Görevin, yurt dışında yaşayan Türk öğrencilere Türkçe konuşma pratiği kazandırmak. Bu doğrultuda öğrencilere yardımcı olmalısın. Yardımcı olurken asla küfür veya argo kullanmamalı, herkese karşı nazik olmalısın. Sana hangi dilde soru sorulursa sorulsun, cevaplarını daima Türkçe vermelisin. Politik konulara asla girme."""

# Konuşma geçmişini saklamak için sözlük
conversations = {}

@app.route('/api/chat', methods=['POST'])
def chat():
    try:
        data = request.json
        logger.info(f"Received request: {data}")
        
        # Kullanıcı metnini al
        user_text = data.get('text', '')
        if not user_text:
            return jsonify({"error": "Text field is required"}), 400
        
        # Konuşma ID'sini al veya yeni oluştur
        conversation_id = data.get('conversation_id')
        if not conversation_id:
            # Yeni konuşma başlatılıyor, ilk prompt eklenecek
            conversation_id = str(uuid.uuid4())
            conversations[conversation_id] = [{
                "role": "system",
                "content": DILDAS_PROMPT
            }]
        elif conversation_id not in conversations:
            # Konuşma ID'si var ama sözlükte yok, ilk prompt ile başlat
            conversations[conversation_id] = [{
                "role": "system",
                "content": DILDAS_PROMPT
            }]
        
        # Kullanıcı mesajını konuşma geçmişine ekle
        conversations[conversation_id].append({
            "role": "user",
            "content": user_text
        })
        
        # Gemma API'ye gönderilecek mesajları hazırla
        messages = conversations[conversation_id].copy()
        
        # Gemma API'ye istek gönder
        try:
            logger.info(f"Sending request to Gemma API with messages: {messages}")
            
            response = requests.post(
                GEMMA_API_URL,
                json={
                    "model": "google/gemma-3n-e4b",
                    "messages": messages,
                    "temperature": 0.7,
                    "max_tokens": 800,
                    "stream": False
                },
                timeout=30
            )
            
            # API yanıtını kontrol et
            if response.status_code != 200:
                logger.error(f"Gemma API error: {response.status_code} - {response.text}")
                return jsonify({
                    "error": f"Gemma API error: {response.status_code}",
                    "details": response.text,
                    "conversation_id": conversation_id
                }), 500
            
            # API yanıtını işle
            api_response = response.json()
            logger.info(f"Gemma API response: {api_response}")
            
            # Asistan yanıtını al
            assistant_response = ""
            if api_response.get("choices") and len(api_response["choices"]) > 0:
                if "message" in api_response["choices"][0]:
                    assistant_response = api_response["choices"][0]["message"]["content"]
                elif "text" in api_response["choices"][0]:
                    assistant_response = api_response["choices"][0]["text"]
            
            # Asistan yanıtını konuşma geçmişine ekle
            if assistant_response:
                conversations[conversation_id].append({
                    "role": "assistant",
                    "content": assistant_response
                })
            
            # Yanıtı döndür
            return jsonify({
                "response": assistant_response,
                "conversation_id": conversation_id,
                "choices": api_response.get("choices", [])
            })
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error connecting to Gemma API: {str(e)}")
            return jsonify({
                "error": f"Error connecting to Gemma API: {str(e)}",
                "conversation_id": conversation_id
            }), 500
            
    except Exception as e:
        logger.error(f"Server error: {str(e)}")
        return jsonify({"error": f"Server error: {str(e)}"}), 500

@app.route('/api/reset_conversation', methods=['POST'])
def reset_conversation():
    try:
        data = request.json
        conversation_id = data.get('conversation_id')
        
        if conversation_id and conversation_id in conversations:
            # Konuşmayı sıfırlarken ilk prompt'u ekle
            conversations[conversation_id] = [{
                "role": "system",
                "content": DILDAS_PROMPT
            }]
            return jsonify({"status": "success", "message": "Conversation reset with initial prompt"})
        else:
            return jsonify({"status": "error", "message": "Invalid conversation ID"}), 400
            
    except Exception as e:
        logger.error(f"Reset conversation error: {str(e)}")
        return jsonify({"error": f"Server error: {str(e)}"}), 500

@app.route('/api/test', methods=['GET'])
def test_api():
    return jsonify({
        "status": "success",
        "message": "API server is running"
    })

@app.route('/api/test_gemma', methods=['GET'])
def test_gemma_api():
    try:
        response = requests.post(
            GEMMA_API_URL,
            json={
                "model": "google/gemma-3n-e4b",
                "messages": [
                    {"role": "system", "content": DILDAS_PROMPT},
                    {"role": "user", "content": "Merhaba"}
                ],
                "temperature": 0.7,
                "max_tokens": 10,
                "stream": False
            },
            timeout=10
        )
        
        if response.status_code == 200:
            return jsonify({
                "status": "success",
                "message": "Gemma API is working",
                "response": response.json()
            })
        else:
            return jsonify({
                "status": "error",
                "message": f"Gemma API error: {response.status_code}",
                "details": response.text
            }), 500
            
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": f"Error testing Gemma API: {str(e)}"
        }), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)