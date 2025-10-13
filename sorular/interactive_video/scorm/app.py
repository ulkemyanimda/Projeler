from flask import Flask, render_template, request, send_file, redirect, url_for, flash
import os
import csv
import tempfile
from werkzeug.utils import secure_filename
from scorm_creator import EnhancedYouTubeSCORMCreator  # Kodunuzu ayrı bir dosyaya koyun, örn: scorm_creator.py

app = Flask(__name__)
app.secret_key = 'scorm_creator_secret'

UPLOAD_FOLDER = tempfile.gettempdir()
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/')
def index():
    return render_template('form.html')

@app.route('/create', methods=['POST'])
def create_scorm():
    try:
        youtube_url = request.form['url']
        title = request.form['title']
        duration = int(request.form['duration'])

        # CSV dosyası yüklendi mi?
        csv_file = request.files.get('csv_file')
        if not csv_file or not csv_file.filename.endswith('.csv'):
            flash("Lütfen geçerli bir CSV dosyası yükleyin.", "error")
            return redirect(url_for('index'))

        # Geçici CSV dosyası olarak kaydet
        csv_path = os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(csv_file.filename))
        csv_file.save(csv_path)

        # SCORM oluşturucuyu başlat
        output_dir = tempfile.mkdtemp()
        creator = EnhancedYouTubeSCORMCreator(
            youtube_url=youtube_url,
            output_dir=output_dir,
            title=title
        )
        creator.set_video_duration(duration)

        # CSV'den soruları oku
        with open(csv_path, newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                # UTF-8 BOM sorunu için
                time_key = '\ufeffsure' if '\ufeffsure' in row else 'sure'
                sure = int(row[time_key])
                soru = row['soru']
                secenekler = [row['a'], row['b'], row['c'], row['d']]
                cevap = int(row['cevap'])
                creator.add_question(sure, soru, secenekler, cevap)

        # Paketi oluştur
        zip_path = creator.create_package()

        # Geçici dosyaları temizle (isteğe bağlı)
        os.remove(csv_path)

        return send_file(zip_path, as_attachment=True)

    except Exception as e:
        flash(f"Hata oluştu: {str(e)}", "error")
        return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)