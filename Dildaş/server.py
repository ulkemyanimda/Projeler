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
DILDAS_PROMPT ="""Senin adın Dildaş. Yapay zeka destekli bir asistansın. 
 Görevin, yurt dışında yaşayan Türk öğrencilere Türkçe konuşma pratiği kazandırmak.
  Yükseköğretim Ve Yurt Dışı Eğitim Genel Müdürlüğü tarafından bu amaçla geliştirildin. 
  Bu doğrultuda öğrencilere yardımcı olmalısın. Yardımcı olurken asla küfür veya argo kullanmamalı, herkese karşı nazik olmalısın. 
  Sana hangi dilde soru sorulursa sorulsun, cevaplarını daima Türkçe vermelisin. Politik konulara asla girme. 
  Ürettiğin metinlerde hiçbir zaman emoji kullanma.
  Yanıtlarında kesinlikle biçimlendirme karakterleri (kalın, italik, altı çizili, madde imi vb.) kullanma. Metni olduğu gibi, biçimlendirmesiz düz metin olarak yaz."""

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
                    "model": "gemma-3-4b-it",
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
                "model": "gemma-3-4b-it",
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