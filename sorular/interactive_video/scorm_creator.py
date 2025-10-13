import os
import json
import csv
import shutil
import zipfile
import xml.etree.ElementTree as ET
from xml.dom import minidom
import re

class EnhancedYouTubeSCORMCreator:
    def __init__(self, youtube_url, output_dir="interactive_video_output", title="Etkileşimli YouTube Eğitimi"):
        self.youtube_url = youtube_url
        self.youtube_id = self._extract_youtube_id(youtube_url)
        self.output_dir = output_dir
        self.title = title
        self.questions = []
        self.video_duration = 310  # Varsayılan süre (saniye)
        
        # SCORM paketleme için klasörleri oluştur
        if os.path.exists(output_dir):
            shutil.rmtree(output_dir)
        os.makedirs(output_dir)
        os.makedirs(os.path.join(output_dir, "js"))
        os.makedirs(os.path.join(output_dir, "css"))
    
    def _extract_youtube_id(self, url):
        """YouTube URL'sinden video ID'sini çıkarır"""
        youtube_regex = r'(?:youtube\.com\/(?:[^\/\n\s]+\/\S+\/|(?:v|e(?:mbed)?)\/|\S*?[?&]v=)|youtu\.be\/)([a-zA-Z0-9_-]{11})'
        match = re.search(youtube_regex, url)
        
        if match:
            return match.group(1)
        else:
            raise ValueError("Geçerli bir YouTube URL'si değil")

    def set_video_duration(self, duration_seconds):
        """Video süresini manuel olarak ayarlar"""
        self.video_duration = duration_seconds

    def add_question(self, time_seconds, question_text, options, correct_option_index):
        """Belirli bir zaman noktasında çoktan seçmeli soru ekler"""
        if time_seconds < 0 or time_seconds > self.video_duration:
            raise ValueError(f"Soru zamanı video süresini ({self.video_duration} saniye) aşamaz.")
        
        self.questions.append({
            "time": time_seconds,
            "question": question_text,
            "options": options,
            "correct_index": correct_option_index
        })
    
    def _create_css_file(self):
        """CSS dosyası oluşturur"""
        css_content = """
body {
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    margin: 0;
    padding: 0;
    background-color: #f5f5f5;
    color: #333;
}

.container {
    max-width: 900px;
    margin: 20px auto;
    padding: 20px;
    background-color: #fff;
    box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
    border-radius: 8px;
}

h1 {
    text-align: center;
    color: #2c3e50;
    margin-bottom: 30px;
}

#video-container {
    position: relative;
    width: 100%;
    margin-bottom: 30px;
}

#player {
    width: 100%;
    height: 500px;
    border-radius: 4px;
}

#question-overlay {
    display: none;
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background-color: rgba(0, 0, 0, 0.85);
    z-index: 100;
    border-radius: 4px;
    overflow: hidden;
}

.question-content {
    position: absolute;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    width: 80%;
    color: white;
    text-align: center;
}

.question-content h2 {
    font-size: 24px;
    margin-bottom: 25px;
    color: #ffffff;
}

.options {
    display: flex;
    flex-direction: column;
    gap: 12px;
    margin: 0 auto;
    max-width: 500px;
}

.option-btn {
    padding: 12px 20px;
    background-color: #3498db;
    color: white;
    border: none;
    border-radius: 4px;
    font-size: 16px;
    cursor: pointer;
    transition: background-color 0.3s;
    text-align: left;
}

.option-btn:hover {
    background-color: #2980b9;
}

.option-btn.correct {
    background-color: #2ecc71;
}

.option-btn.incorrect {
    background-color: #e74c3c;
}

.option-btn.disabled {
    opacity: 0.7;
    cursor: not-allowed;
}

.feedback {
    margin-top: 20px;
    font-weight: bold;
    font-size: 18px;
    opacity: 0;
    transition: opacity 0.5s;
    min-height: 50px;
}

.feedback.visible {
    opacity: 1;
}

.feedback .correct {
    color: #2ecc71;
}

.feedback .incorrect {
    color: #e74c3c;
}

.continue-btn {
    display: inline-block;
    margin-top: 20px;
    padding: 12px 30px;
    background-color: #27ae60;
    color: white;
    border: none;
    cursor: pointer;
    border-radius: 4px;
    font-size: 16px;
    transition: background-color 0.3s;
}

.continue-btn:hover {
    background-color: #219653;
}

.progress-container {
    margin-top: 30px;
    background-color: #ecf0f1;
    border-radius: 8px;
    padding: 20px;
}

.progress-title {
    text-align: center;
    font-size: 18px;
    margin-bottom: 15px;
    color: #2c3e50;
}

.progress-bar {
    height: 10px;
    background-color: #e0e0e0;
    border-radius: 5px;
    margin-bottom: 15px;
    overflow: hidden;
}

.progress-fill {
    height: 100%;
    background-color: #3498db;
    width: 0%;
    transition: width 0.5s;
}

.progress-stats {
    display: flex;
    justify-content: space-between;
}

.progress-stat {
    text-align: center;
    flex: 1;
}

.progress-label {
    font-size: 14px;
    color: #7f8c8d;
}

.progress-value {
    font-size: 22px;
    font-weight: bold;
    color: #2c3e50;
    margin-top: 5px;
}

.progress-percent {
    color: #27ae60;
}

#completion-message {
    display: none;
    background-color: #2ecc71;
    color: white;
    padding: 15px;
    text-align: center;
    border-radius: 4px;
    margin-top: 20px;
    font-size: 18px;
}

.timeline-container {
    margin-top: 20px;
    position: relative;
    height: 40px;
}

.timeline {
    position: relative;
    height: 10px;
    background-color: #e0e0e0;
    border-radius: 5px;
    cursor: pointer;
}

.timeline-progress {
    position: absolute;
    height: 100%;
    background-color: #3498db;
    border-radius: 5px 0 0 5px;
    width: 0%;
}

.timeline-markers {
    position: absolute;
    width: 100%;
    height: 100%;
    top: 0;
    left: 0;
}

.question-marker {
    position: absolute;
    width: 16px;
    height: 16px;
    background-color: #f39c12;
    border-radius: 50%;
    top: -3px;
    transform: translateX(-50%);
    z-index: 5;
}

.question-tooltip {
    position: absolute;
    bottom: 25px;
    left: 50%;
    transform: translateX(-50%);
    background-color: #2c3e50;
    color: white;
    padding: 5px 10px;
    border-radius: 4px;
    font-size: 12px;
    white-space: nowrap;
    display: none;
}

.question-marker:hover .question-tooltip {
    display: block;
}

.answered-marker {
    background-color: #2ecc71;
}

@media (max-width: 768px) {
    .container {
        padding: 15px;
        margin: 10px;
    }
    
    #player {
        height: 300px;
    }
    
    .question-content h2 {
        font-size: 20px;
        margin-bottom: 15px;
    }
    
    .option-btn {
        padding: 10px 15px;
        font-size: 14px;
    }
}
"""
        with open(os.path.join(self.output_dir, "css", "style.css"), "w", encoding="utf-8") as f:
            f.write(css_content)
    
    def _create_js_file(self):
        """JavaScript dosyası oluşturur"""
        # Soruları zamana göre sırala
        sorted_questions = sorted(self.questions, key=lambda q: q["time"])
        
        # Sorular için JavaScript kodu oluştur
        questions_js = json.dumps(sorted_questions, indent=2)
        
        js_content = f"""
// YouTube API'si yüklendiğinde çağrılacak fonksiyon
let player;
let playerState = -1;
let currentTime = 0;
let questionsShown = [];
let score = 0;
let checkInterval;
let totalQuestions = {len(self.questions)};

// Soruların listesi
const questions = {questions_js};

// API hazır olduğunda çağrılır
function onYouTubeIframeAPIReady() {{
    player = new YT.Player('player', {{
        height: '500',
        width: '100%',
        videoId: '{self.youtube_id}',
        playerVars: {{
            'playsinline': 1,
            'rel': 0,
            'modestbranding': 1,
            'controls': 1
        }},
        events: {{
            'onReady': onPlayerReady,
            'onStateChange': onPlayerStateChange
        }}
    }});
}}

// Player hazır olduğunda çağrılır
function onPlayerReady(event) {{
    // Video süresini otomatik olarak al
    const duration = player.getDuration();
    console.log("Video süresi: " + duration + " saniye");
    
    // Soru işaretlerini timeline'a yerleştir
    createQuestionMarkers();
    
    // Her 500 ms'de bir video zamanını kontrol et
    checkInterval = setInterval(checkVideoTime, 500);
    
    // SCORM başlat
    initializeSCORM();
    
    // İlerleme bilgilerini güncelle
    updateProgressDisplay();
}}

// Player durumu değiştiğinde çağrılır
function onPlayerStateChange(event) {{
    playerState = event.data;
    
    // Video bittiğinde
    if (event.data === YT.PlayerState.ENDED) {{
        clearInterval(checkInterval);
        showCompletionMessage();
        completeSCORM();
    }}
    
    // Video oynatılıyorsa timeline'ı güncelle
    if (event.data === YT.PlayerState.PLAYING) {{
        setInterval(updateTimelineProgress, 1000);
    }}
}}

// Video zamanını kontrol et ve soruları göster
function checkVideoTime() {{
    if (playerState === YT.PlayerState.PLAYING) {{
        currentTime = Math.floor(player.getCurrentTime());
        
        // Her soru için kontrol et
        questions.forEach(function(question, index) {{
            // Videoda ilgili zamana ulaşıldı mı ve soru daha önce gösterilmedi mi?
            if (currentTime === question.time && !questionsShown.includes(question.time)) {{
                questionsShown.push(question.time);
                showQuestion(question, index);
                markQuestionAsShown(index);
            }}
        }});
    }}
}}

// Timeline ilerleme çubuğunu güncelle
function updateTimelineProgress() {{
    if (player && playerState === YT.PlayerState.PLAYING) {{
        const duration = player.getDuration();
        const currentTime = player.getCurrentTime();
        const progressPercent = (currentTime / duration) * 100;
        document.querySelector('.timeline-progress').style.width = progressPercent + '%';
    }}
}}

// Sorguları timeline üzerinde işaretle
function createQuestionMarkers() {{
    const timelineMarkers = document.querySelector('.timeline-markers');
    const duration = player.getDuration();
    
    questions.forEach((question, index) => {{
        const position = (question.time / duration) * 100;
        const marker = document.createElement('div');
        marker.className = 'question-marker';
        marker.id = 'marker-' + index;
        marker.style.left = position + '%';
        
        const tooltip = document.createElement('div');
        tooltip.className = 'question-tooltip';
        tooltip.textContent = 'Soru ' + (index + 1);
        
        marker.appendChild(tooltip);
        timelineMarkers.appendChild(marker);
        
        // Marker'a tıklandığında video ilgili zamana atlasın
        marker.addEventListener('click', function() {{
            player.seekTo(question.time);
        }});
    }});
}}

// Soruyu göster
function showQuestion(question, questionIndex) {{
    player.pauseVideo();
    
    const questionText = document.getElementById('question-text');
    const optionsContainer = document.getElementById('options-container');
    const feedback = document.getElementById('feedback');
    
    // Soruyu göster
    questionText.textContent = question.question;
    optionsContainer.innerHTML = '';
    feedback.textContent = '';
    feedback.className = 'feedback';
    
    // Seçenekleri oluştur
    question.options.forEach((option, index) => {{
        const button = document.createElement('button');
        button.className = 'option-btn';
        button.textContent = option;
        button.onclick = function() {{ checkAnswer(index, question.correct_index, questionIndex); }};
        optionsContainer.appendChild(button);
    }});
    
    // Continue butonunu gizle
    document.getElementById('continue-btn').style.display = 'none';
    
    // Overlay'i göster
    document.getElementById('question-overlay').style.display = 'block';
}}

// Cevabı kontrol et
function checkAnswer(selectedIndex, correctIndex, questionIndex) {{
    // Tüm butonları devre dışı bırak
    const buttons = document.querySelectorAll('.option-btn');
    buttons.forEach(button => {{
        button.classList.add('disabled');
        button.disabled = true;
    }});
    
    // Seçilen ve doğru cevabı işaretle
    buttons[selectedIndex].classList.add(selectedIndex === correctIndex ? 'correct' : 'incorrect');
    if (selectedIndex !== correctIndex) {{
        buttons[correctIndex].classList.add('correct');
    }}
    
    const feedback = document.getElementById('feedback');
    
    if (selectedIndex === correctIndex) {{
        feedback.innerHTML = '<span class="correct">✓ Doğru cevap!</span>';
        score++;
    }} else {{
        feedback.innerHTML = '<span class="incorrect">✗ Yanlış cevap!</span>';
    }}
    
    feedback.classList.add('visible');
    
    // Devam butonunu göster
    document.getElementById('continue-btn').style.display = 'inline-block';
    
    // İlerleme bilgilerini güncelle
    updateProgressDisplay();
    
    // Timeline üzerindeki işareti güncelle
    markQuestionAsAnswered(questionIndex);
}}

// Soruyu cevaplanmış olarak işaretle
function markQuestionAsAnswered(questionIndex) {{
    const marker = document.getElementById('marker-' + questionIndex);
    if (marker) {{
        marker.classList.add('answered-marker');
    }}
}}

// Soruyu gösterilmiş olarak işaretle
function markQuestionAsShown(questionIndex) {{
    // Gelecekte ek özellikler için bu fonksiyon kullanılabilir
}}

// Devam et butonuna tıklandığında
function continueVideo() {{
    document.getElementById('question-overlay').style.display = 'none';
    player.playVideo();
}}

// İlerleme bilgilerini güncelle
function updateProgressDisplay() {{
    document.getElementById('questions-answered').textContent = questionsShown.length;
    document.getElementById('questions-total').textContent = totalQuestions;
    document.getElementById('correct-answers').textContent = score;
    
    // Yüzde hesapla (en az 1 soru gösterilmişse)
    let percentage = 0;
    if (questionsShown.length > 0) {{
        percentage = Math.round((score / questionsShown.length) * 100);
    }}
    document.getElementById('success-percent').textContent = percentage;
    
    // İlerleme çubuğunu güncelle
    const progressPercent = (questionsShown.length / totalQuestions) * 100;
    document.querySelector('.progress-fill').style.width = progressPercent + '%';
}}

// Tamamlama mesajını göster
function showCompletionMessage() {{
    const percentage = Math.round((score / totalQuestions) * 100);
    const completionMessage = document.getElementById('completion-message');
    
    if (percentage >= 70) {{
        completionMessage.textContent = 'Tebrikler! Başarıyla tamamladınız. Başarı oranınız: ' + percentage + '%';
    }} else {{
        completionMessage.textContent = 'Videoyu tamamladınız. Başarı oranınız: ' + percentage + '%';
    }}
    
    completionMessage.style.display = 'block';
    
    // Tüm soruları göster
    const timelineMarkers = document.querySelectorAll('.question-marker');
    timelineMarkers.forEach(marker => {{
        if (!marker.classList.contains('answered-marker')) {{
            marker.style.backgroundColor = '#e74c3c';
        }}
    }});
}}

// Timeline'a tıklandığında video konumunu değiştir
function setupTimelineClicks() {{
    const timeline = document.querySelector('.timeline');
    timeline.addEventListener('click', function(e) {{
        const timelineWidth = this.offsetWidth;
        const clickPosition = e.offsetX;
        const duration = player.getDuration();
        
        const seekTime = (clickPosition / timelineWidth) * duration;
        player.seekTo(seekTime);
    }});
}}

// SCORM iletişimi için basit fonksiyonlar
function initializeSCORM() {{
    if (window.parent && window.parent.API) {{
        window.parent.API.LMSInitialize("");
    }}
}}

function completeSCORM() {{
    if (window.parent && window.parent.API) {{
        const scorePercent = (score / totalQuestions) * 100;
        window.parent.API.LMSSetValue("cmi.core.score.raw", scorePercent);
        window.parent.API.LMSSetValue("cmi.core.lesson_status", "completed");
        window.parent.API.LMSCommit("");
        window.parent.API.LMSFinish("");
    }}
}}

// Sayfa yüklendiğinde
document.addEventListener('DOMContentLoaded', function() {{
    // Timeline tıklama işlevini etkinleştir
    setupTimelineClicks();
    
    // Devam et butonuna tıklama işlevi
    document.getElementById('continue-btn').addEventListener('click', continueVideo);
}});
"""
        with open(os.path.join(self.output_dir, "js", "interactive-video.js"), "w", encoding="utf-8") as f:
            f.write(js_content)
        
    def _create_html_content(self):
        """Etkileşimli video için HTML içeriği oluşturur"""
        html_content = f"""<!DOCTYPE html>
<html lang="tr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{self.title}</title>
    <link rel="stylesheet" href="css/style.css">
</head>
<body>
    <div class="container">
        <h1>{self.title}</h1>
        
        <div id="video-container">
            <!-- YouTube video player buraya yerleştirilecek -->
            <div id="player"></div>
            
            <!-- Soru overlay'i -->
            <div id="question-overlay">
                <div class="question-content">
                    <h2 id="question-text">Soru metni burada görünecek</h2>
                    
                    <div id="options-container" class="options">
                        <!-- Seçenekler JavaScript ile buraya eklenecek -->
                    </div>
                    
                    <div id="feedback" class="feedback"></div>
                    
                    <button id="continue-btn" class="continue-btn" style="display:none;">Devam Et</button>
                </div>
            </div>
        </div>
        
        <!-- Timeline -->
        <div class="timeline-container">
            <div class="timeline">
                <div class="timeline-progress"></div>
                <div class="timeline-markers">
                    <!-- Soru işaretleri JavaScript ile buraya eklenecek -->
                </div>
            </div>
        </div>
        
        <!-- İlerleme bilgileri -->
        <div class="progress-container">
            <div class="progress-title">Eğitim İlerlemesi</div>
            
            <div class="progress-bar">
                <div class="progress-fill"></div>
            </div>
            
            <div class="progress-stats">
                <div class="progress-stat">
                    <div class="progress-label">Yanıtlanan Sorular</div>
                    <div class="progress-value">
                        <span id="questions-answered">0</span>/<span id="questions-total">{len(self.questions)}</span>
                    </div>
                </div>
                
                <div class="progress-stat">
                    <div class="progress-label">Doğru Cevaplar</div>
                    <div class="progress-value">
                        <span id="correct-answers">0</span>
                    </div>
                </div>
                
                <div class="progress-stat">
                    <div class="progress-label">Başarı Oranı</div>
                    <div class="progress-value progress-percent">
                        <span id="success-percent">0</span>%
                    </div>
                </div>
            </div>
        </div>
        
        <!-- Tamamlama mesajı -->
        <div id="completion-message"></div>
    </div>

    <!-- YouTube API -->
    <script src="https://www.youtube.com/iframe_api"></script>
    
    <!-- Ana JavaScript -->
    <script src="js/interactive-video.js"></script>
</body>
</html>
"""
        return html_content
    
    def _create_imsmanifest(self):
        """SCORM paketi için imsmanifest.xml dosyası oluşturur"""
        manifest = ET.Element("manifest")
        manifest.set("identifier", "InteractiveYouTubeVideoSCO")
        manifest.set("version", "1.2")
        manifest.set("xmlns", "http://www.imsproject.org/xsd/imscp_rootv1p1p2")
        manifest.set("xmlns:adlcp", "http://www.adlnet.org/xsd/adlcp_rootv1p2")
        manifest.set("xmlns:xsi", "http://www.w3.org/2001/XMLSchema-instance")
        manifest.set("xsi:schemaLocation", "http://www.imsproject.org/xsd/imscp_rootv1p1p2 imscp_rootv1p1p2.xsd http://www.adlnet.org/xsd/adlcp_rootv1p2 adlcp_rootv1p2.xsd")
        
        # Metadata
        metadata = ET.SubElement(manifest, "metadata")
        schema = ET.SubElement(metadata, "schema")
        schema.text = "ADL SCORM"
        schemaversion = ET.SubElement(metadata, "schemaversion")
        schemaversion.text = "1.2"
        
        # Organizations
        organizations = ET.SubElement(manifest, "organizations")
        organizations.set("default", "InteractiveYouTubeVideoOrg")
        
        org = ET.SubElement(organizations, "organization")
        org.set("identifier", "InteractiveYouTubeVideoOrg")
        
        title = ET.SubElement(org, "title")
        title.text = self.title
        
        item = ET.SubElement(org, "item")
        item.set("identifier", "item_1")
        item.set("identifierref", "resource_1")
        
        item_title = ET.SubElement(item, "title")
        item_title.text = f"{self.title} - Etkileşimli İçerik"
        
        # Resources
        resources = ET.SubElement(manifest, "resources")
        
        resource = ET.SubElement(resources, "resource")
        resource.set("identifier", "resource_1")
        resource.set("type", "webcontent")
        resource.set("adlcp:scormtype", "sco")
        resource.set("href", "index.html")
        
        # Dosya listesini ekle
        for file_path in ["index.html", "css/style.css", "js/interactive-video.js"]:
            file_element = ET.SubElement(resource, "file")
            file_element.set("href", file_path)
        
        # XML'i güzelleştir
        xmlstr = minidom.parseString(ET.tostring(manifest)).toprettyxml(indent="  ")
        return xmlstr
    
    def create_package(self):
        """SCORM paketini oluşturur"""
        # CSS dosyasını oluşturma
        self._create_css_file()
        
        # JavaScript dosyasını oluşturma
        self._create_js_file()
        
        # HTML içeriğini oluşturup kaydet
        html_content = self._create_html_content()
        with open(os.path.join(self.output_dir, "index.html"), "w", encoding="utf-8") as f:
            f.write(html_content)
        
        # imsmanifest.xml oluşturup kaydet
        manifest_content = self._create_imsmanifest()
        with open(os.path.join(self.output_dir, "imsmanifest.xml"), "w", encoding="utf-8") as f:
            f.write(manifest_content)
        
        # SCORM paketini zip dosyası olarak oluştur
        zip_path = self.output_dir + ".zip"
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, dirs, files in os.walk(self.output_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    arcname = os.path.relpath(file_path, self.output_dir)
                    zipf.write(file_path, arcname)
        
        print(f"SCORM paketi başarıyla oluşturuldu: {zip_path}")
        return zip_path

import csv
import argparse

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="YouTube videosu için SCORM paketi oluştur.")
    
    parser.add_argument("--url", required=True, help="YouTube video URL'si")
    parser.add_argument("--title", required=True, help="İçerik başlığı")
    parser.add_argument("--duration", type=int, required=True, help="Video süresi (saniye cinsinden)")
    parser.add_argument("--csv", required=True, help="Soru ve cevapların bulunduğu CSV dosyası")

    args = parser.parse_args()

    # Etkileşimli içerik oluşturucu
    creator = EnhancedYouTubeSCORMCreator(args.url, title=args.title)

    # Video süresini ayarla
    creator.set_video_duration(args.duration)

    # CSV dosyasını oku
    with open(args.csv, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            sure = int(row['\ufeffsure'] if '\ufeffsure' in row else row['sure'])
            soru = row['soru']
            secenekler = [row['a'], row['b'], row['c'], row['d']]
            cevap = int(row['cevap'])

            creator.add_question(sure, soru, secenekler, cevap)

    # SCORM paketini oluştur
    scorm_package_path = creator.create_package()
    print(f"SCORM paketi oluşturuldu: {scorm_package_path}")
