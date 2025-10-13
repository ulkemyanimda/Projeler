from flask import Flask, render_template, request, send_file, jsonify, session
import os
import csv
import tempfile
import secrets
from werkzeug.utils import secure_filename
import json

# Mevcut YouTube SCORM Creator kodunuzu import edin
# from youtube_scorm_creator import EnhancedYouTubeSCORMCreator

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)
app.config['UPLOAD_FOLDER'] = tempfile.gettempdir()
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max dosya boyutu

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/validate-url', methods=['POST'])
def validate_url():
    """YouTube URL'sini doğrula"""
    data = request.get_json()
    url = data.get('url', '')
    
    try:
        # YouTube URL pattern kontrolü
        import re
        youtube_regex = r'(?:youtube\.com\/(?:[^\/\n\s]+\/\S+\/|(?:v|e(?:mbed)?)\/|\S*?[?&]v=)|youtu\.be\/)([a-zA-Z0-9_-]{11})'
        match = re.search(youtube_regex, url)
        
        if match:
            video_id = match.group(1)
            return jsonify({
                'valid': True,
                'video_id': video_id,
                'thumbnail': f'https://img.youtube.com/vi/{video_id}/mqdefault.jpg'
            })
        else:
            return jsonify({'valid': False, 'error': 'Geçersiz YouTube URL\'si'})
    except Exception as e:
        return jsonify({'valid': False, 'error': str(e)})

@app.route('/api/upload-csv', methods=['POST'])
def upload_csv():
    """CSV dosyasını yükle ve parse et"""
    if 'file' not in request.files:
        return jsonify({'error': 'Dosya bulunamadı'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'Dosya seçilmedi'}), 400
    
    if not file.filename.endswith('.csv'):
        return jsonify({'error': 'Sadece CSV dosyaları yüklenebilir'}), 400
    
    try:
        # CSV içeriğini oku
        content = file.read().decode('utf-8')
        csv_reader = csv.DictReader(content.splitlines())
        
        questions = []
        for row in csv_reader:
            # BOM karakterini temizle
            sure_key = 'sure'
            if '\ufeffsure' in row:
                sure_key = '\ufeffsure'
            
            question = {
                'time': int(row[sure_key]),
                'question': row['soru'],
                'options': [row['a'], row['b'], row['c'], row['d']],
                'correct': int(row['cevap'])
            }
            questions.append(question)
        
        # Session'a kaydet
        session['questions'] = questions
        
        return jsonify({
            'success': True,
            'questions': questions,
            'count': len(questions)
        })
    
    except Exception as e:
        return jsonify({'error': f'CSV okuma hatası: {str(e)}'}), 400

@app.route('/api/create-scorm', methods=['POST'])
def create_scorm():
    """SCORM paketini oluştur"""
    try:
        data = request.get_json()
        
        youtube_url = data.get('url')
        title = data.get('title')
        duration = int(data.get('duration'))
        questions = data.get('questions', [])
        
        if not all([youtube_url, title, duration, questions]):
            return jsonify({'error': 'Eksik bilgi'}), 400
        
        # SCORM Creator'ı kullan
        from youtube_scorm_creator import EnhancedYouTubeSCORMCreator
        
        # Geçici klasör oluştur
        temp_dir = tempfile.mkdtemp()
        output_dir = os.path.join(temp_dir, "scorm_package")
        
        creator = EnhancedYouTubeSCORMCreator(
            youtube_url=youtube_url,
            output_dir=output_dir,
            title=title
        )
        
        creator.set_video_duration(duration)
        
        # Soruları ekle
        for q in questions:
            creator.add_question(
                time_seconds=q['time'],
                question_text=q['question'],
                options=q['options'],
                correct_option_index=q['correct']
            )
        
        # SCORM paketini oluştur
        zip_path = creator.create_package()
        
        # Dosyayı gönder
        return send_file(
            zip_path,
            as_attachment=True,
            download_name=f"{title.replace(' ', '_')}_SCORM.zip",
            mimetype='application/zip'
        )
    
    except Exception as e:
        return jsonify({'error': f'SCORM oluşturma hatası: {str(e)}'}), 500

@app.route('/api/add-question', methods=['POST'])
def add_question():
    """Manuel soru ekleme"""
    data = request.get_json()
    
    if 'questions' not in session:
        session['questions'] = []
    
    questions = session['questions']
    questions.append({
        'time': data['time'],
        'question': data['question'],
        'options': data['options'],
        'correct': data['correct']
    })
    
    session['questions'] = questions
    
    return jsonify({
        'success': True,
        'questions': questions,
        'count': len(questions)
    })

@app.route('/api/delete-question/<int:index>', methods=['DELETE'])
def delete_question(index):
    """Soru silme"""
    if 'questions' not in session:
        return jsonify({'error': 'Soru bulunamadı'}), 404
    
    questions = session['questions']
    
    if 0 <= index < len(questions):
        questions.pop(index)
        session['questions'] = questions
        return jsonify({
            'success': True,
            'questions': questions,
            'count': len(questions)
        })
    
    return jsonify({'error': 'Geçersiz index'}), 400

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
