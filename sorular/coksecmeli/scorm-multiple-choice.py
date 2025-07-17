import csv
import os
import shutil
import zipfile
import uuid
import json
from datetime import datetime

def create_scorm_package(csv_file_path, output_dir="scorm_output"):
    """
    CSV dosyasından SCORM paketi oluşturur.
    CSV dosyası: soru,doğru cevap,seçenek1,seçenek2,seçenek3,... formatında olmalıdır
    """
    # Output dizinini oluştur
    os.makedirs(output_dir, exist_ok=True)
    
    # Gerekli SCORM dizin yapısını oluştur
    scorm_dirs = ["assets", "scripts", "styles"]
    for dir_name in scorm_dirs:
        os.makedirs(os.path.join(output_dir, dir_name), exist_ok=True)
    
    # CSV'den soruları oku
    questions = []
    with open(csv_file_path, 'r', encoding='utf-8') as file:
        csv_reader = csv.reader(file)
        headers = next(csv_reader, None)  # Başlık satırını atla
        
        for row in csv_reader:
            if len(row) >= 3:  # En az soru, doğru cevap ve bir seçenek olmalı
                # İlk sütun soru, ikinci sütun doğru cevap, geri kalanlar seçenekler
                options = row[1:]  # Doğru cevap dahil tüm seçenekler
                
                # Seçeneklerin sırasını karıştır
                import random
                correct_answer = row[1]  # Doğru cevabı kaydet
                random.shuffle(options)  # Seçenekleri karıştır
                
                questions.append({
                    "id": str(uuid.uuid4()),
                    "question": row[0],
                    "correct_answer": correct_answer,
                    "options": options
                })
    
    # HTML içeriği oluştur
    html_content = create_html_content(questions)
    with open(os.path.join(output_dir, "index.html"), 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    # CSS dosyası oluştur
    css_content = create_css_content()
    with open(os.path.join(output_dir, "styles", "main.css"), 'w', encoding='utf-8') as f:
        f.write(css_content)
    
    # JavaScript dosyası oluştur
    js_content = create_js_content()
    with open(os.path.join(output_dir, "scripts", "main.js"), 'w', encoding='utf-8') as f:
        f.write(js_content)
    
    # SCORM manifest dosyası oluştur
    manifest_content = create_manifest_content()
    with open(os.path.join(output_dir, "imsmanifest.xml"), 'w', encoding='utf-8') as f:
        f.write(manifest_content)
    
    # JSON veri dosyası oluştur
    with open(os.path.join(output_dir, "assets", "questions.json"), 'w', encoding='utf-8') as f:
        json.dump(questions, f, ensure_ascii=False, indent=2)
    
    # SCORM paketini zip olarak oluştur
    package_name = f"scorm_quiz_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    zip_path = f"{package_name}.zip"
    
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(output_dir):
            for file in files:
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, output_dir)
                zipf.write(file_path, arcname)
    
    print(f"SCORM paketi oluşturuldu: {zip_path}")
    return zip_path

def create_html_content(questions):
    """HTML içeriğini oluşturur"""
    html = """<!DOCTYPE html>
<html lang="tr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Çoktan Seçmeli Quiz</title>
    <link rel="stylesheet" href="styles/main.css">
</head>
<body>
    <div class="quiz-container">
        <h1>Çoktan Seçmeli Quiz</h1>
        <div id="quiz-content">
            <div id="start-screen" class="screen">
                <h2>Quiz'e Hoş Geldiniz</h2>
                <button id="start-btn" class="btn">Başla</button>
            </div>
            
            <div id="question-screen" class="screen hidden">
                <div id="progress-bar">
                    <div id="progress-fill"></div>
                </div>
                <div id="question-number"></div>
                <h2 id="question-text"></h2>
                <div id="options-container">
                    <!-- Seçenekler JavaScript ile eklenecek -->
                </div>
                <div id="feedback-container" class="hidden">
                    <div id="feedback-text"></div>
                </div>
                <div id="navigation">
                    <button id="prev-btn" class="btn nav-btn">Önceki</button>
                    <button id="next-btn" class="btn nav-btn">Sonraki</button>
                </div>
            </div>
            
            <div id="results-screen" class="screen hidden">
                <h2>Quiz Tamamlandı!</h2>
                <div id="results-summary"></div>
                <div id="detailed-results"></div>
                <button id="restart-btn" class="btn">Yeniden Başla</button>
            </div>
        </div>
    </div>
    
    <script src="assets/questions.json" type="application/json" id="questions-data"></script>
    <script src="scripts/main.js"></script>
</body>
</html>"""
    return html

def create_css_content():
    """CSS içeriğini oluşturur"""
    css = """body {
    font-family: Arial, sans-serif;
    margin: 0;
    padding: 0;
    background-color: #f5f5f5;
}

.quiz-container {
    max-width: 800px;
    margin: 20px auto;
    background-color: #fff;
    border-radius: 10px;
    box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
    padding: 20px;
}

h1 {
    text-align: center;
    color: #333;
}

.screen {
    padding: 20px;
}

.hidden {
    display: none;
}

.btn {
    background-color: #4CAF50;
    color: white;
    border: none;
    padding: 10px 15px;
    text-align: center;
    text-decoration: none;
    display: inline-block;
    font-size: 16px;
    margin: 10px 0;
    cursor: pointer;
    border-radius: 5px;
    transition: background-color 0.3s;
}

.btn:hover {
    background-color: #45a049;
}

#navigation {
    display: flex;
    justify-content: space-between;
    margin-top: 20px;
}

#question-number {
    color: #666;
    margin-bottom: 10px;
}

#progress-bar {
    width: 100%;
    height: 10px;
    background-color: #ddd;
    border-radius: 5px;
    margin-bottom: 20px;
}

#progress-fill {
    height: 100%;
    background-color: #4CAF50;
    border-radius: 5px;
    width: 0%;
    transition: width 0.3s;
}

#options-container {
    margin: 20px 0;
}

.option-btn {
    display: block;
    width: 100%;
    padding: 12px;
    margin: 8px 0;
    text-align: left;
    background-color: #f9f9f9;
    border: 1px solid #ddd;
    border-radius: 5px;
    cursor: pointer;
    transition: all 0.3s;
}

.option-btn:hover {
    background-color: #e9e9e9;
}

.option-btn.selected {
    background-color: #dff0d8;
    border-color: #4CAF50;
}

.option-btn.correct {
    background-color: #dff0d8;
    border-color: #4CAF50;
}

.option-btn.incorrect {
    background-color: #f2dede;
    border-color: #d9534f;
}

#feedback-container {
    margin: 15px 0;
    padding: 10px;
    border-radius: 5px;
}

#feedback-container.correct {
    background-color: #dff0d8;
    border-left: 5px solid #4CAF50;
}

#feedback-container.incorrect {
    background-color: #f2dede;
    border-left: 5px solid #d9534f;
}

#results-summary {
    margin: 20px 0;
    padding: 15px;
    background-color: #f9f9f9;
    border-radius: 5px;
}

#detailed-results {
    margin-top: 20px;
}

.result-item {
    padding: 10px;
    margin-bottom: 10px;
    border-radius: 5px;
}

.result-item.correct {
    background-color: #dff0d8;
}

.result-item.incorrect {
    background-color: #f2dede;
}"""
    return css

def create_js_content():
    """JavaScript içeriğini oluşturur"""
    js = """// SCORM API Entegrasyonu
let API = null;
let API_1484_11 = null;

// SCORM API'sini bul
function findAPI(win) {
    let findAPITries = 0;
    while ((win.API == null) && (win.API_1484_11 == null) && (win.parent != null) && (win.parent != win) && (findAPITries <= 500)) {
        findAPITries++;
        win = win.parent;
    }
    return win;
}

// SCORM API'sini başlat
function initializeSCORM() {
    let win = window;
    try {
        while (win.API == null && win.API_1484_11 == null && win.parent != null && win.parent != win) {
            win = win.parent;
        }
        API = win.API || null;
        API_1484_11 = win.API_1484_11 || null;
        
        if (API) {
            API.LMSInitialize("");
            console.log("SCORM 1.2 API bulundu ve başlatıldı");
        } else if (API_1484_11) {
            API_1484_11.Initialize("");
            console.log("SCORM 2004 API bulundu ve başlatıldı");
        } else {
            console.log("SCORM API bulunamadı, yerel modda çalışılıyor");
        }
    } catch (e) {
        console.error("SCORM API başlatma hatası:", e);
    }
}

// SCORM'a ilerleme durumunu kaydet
function setSCORMProgress(progress, score) {
    try {
        if (API) {
            API.LMSSetValue("cmi.core.score.raw", score);
            API.LMSSetValue("cmi.core.lesson_location", currentQuestionIndex);
            API.LMSCommit("");
        } else if (API_1484_11) {
            API_1484_11.SetValue("cmi.score.raw", score);
            API_1484_11.SetValue("cmi.score.scaled", score / 100);
            API_1484_11.SetValue("cmi.progress_measure", progress / 100);
            API_1484_11.SetValue("cmi.location", currentQuestionIndex);
            API_1484_11.Commit("");
        }
    } catch (e) {
        console.error("SCORM ilerleme kaydetme hatası:", e);
    }
}

// SCORM oturumunu tamamla
function completeSCORM(score) {
    try {
        if (API) {
            API.LMSSetValue("cmi.core.score.raw", score);
            API.LMSSetValue("cmi.core.lesson_status", "completed");
            API.LMSCommit("");
            API.LMSFinish("");
        } else if (API_1484_11) {
            API_1484_11.SetValue("cmi.score.raw", score);
            API_1484_11.SetValue("cmi.score.scaled", score / 100);
            API_1484_11.SetValue("cmi.completion_status", "completed");
            API_1484_11.SetValue("cmi.success_status", score >= 70 ? "passed" : "failed");
            API_1484_11.Commit("");
            API_1484_11.Terminate("");
        }
    } catch (e) {
        console.error("SCORM tamamlama hatası:", e);
    }
}

// Quiz işlevleri
let questions = [];
let currentQuestionIndex = 0;
let userAnswers = [];
let score = 0;

// JSON veri dosyasından soruları yükle
function loadQuestions() {
    try {
        // Önce JSON veri dosyasından yüklemeyi dene
        const questionsData = document.getElementById('questions-data');
        if (questionsData) {
            const content = questionsData.textContent;
            if (content) {
                questions = JSON.parse(content);
                // Kullanıcı cevapları dizisini oluştur
                userAnswers = new Array(questions.length).fill(null);
                return;
            }
        }
        
        // Alternatif olarak fetch ile yükle
        fetch('assets/questions.json')
            .then(response => response.json())
            .then(data => {
                questions = data;
                userAnswers = new Array(questions.length).fill(null);
                initializeQuiz();
            })
            .catch(error => console.error('Veri yükleme hatası:', error));
    } catch (e) {
        console.error('Soru yükleme hatası:', e);
        questions = []; // Hata durumunda boş dizi
    }
}

// Quiz'i başlat
function initializeQuiz() {
    document.getElementById('start-btn').addEventListener('click', startQuiz);
    document.getElementById('prev-btn').addEventListener('click', goToPrevQuestion);
    document.getElementById('next-btn').addEventListener('click', goToNextQuestion);
    document.getElementById('restart-btn').addEventListener('click', restartQuiz);
    
    // SCORM API'sini başlat
    initializeSCORM();
    
    // Soruları yükle
    loadQuestions();
}

// Quiz'i başlat
function startQuiz() {
    document.getElementById('start-screen').classList.add('hidden');
    document.getElementById('question-screen').classList.remove('hidden');
    loadQuestion(currentQuestionIndex);
}

// Soruyu yükle
function loadQuestion(index) {
    if (index >= 0 && index < questions.length) {
        const question = questions[index];
        document.getElementById('question-number').textContent = `Soru ${index + 1}/${questions.length}`;
        document.getElementById('question-text').textContent = question.question;
        
        // Seçenekleri oluştur
        const optionsContainer = document.getElementById('options-container');
        optionsContainer.innerHTML = '';
        
        question.options.forEach((option, optIndex) => {
            const optionBtn = document.createElement('button');
            optionBtn.textContent = option;
            optionBtn.className = 'option-btn';
            optionBtn.dataset.index = optIndex;
            
            // Eğer kullanıcı daha önce bu soruyu cevapladıysa seçili hale getir
            if (userAnswers[index] !== null && userAnswers[index] === option) {
                optionBtn.classList.add('selected');
            }
            
            optionBtn.addEventListener('click', function() {
                selectOption(index, option);
            });
            
            optionsContainer.appendChild(optionBtn);
        });
        
        // Feedback alanını sıfırla
        const feedbackContainer = document.getElementById('feedback-container');
        feedbackContainer.classList.add('hidden');
        feedbackContainer.classList.remove('correct', 'incorrect');
        
        // İlerleme çubuğunu güncelle
        updateProgressBar();
        
        // Gezinme düğmelerini güncelle
        document.getElementById('prev-btn').disabled = index === 0;
        document.getElementById('next-btn').textContent = index === questions.length - 1 ? 'Bitir' : 'Sonraki';
    }
}

// Seçeneği seç
function selectOption(questionIndex, selectedOption) {
    // Önceki seçimi kaldır
    const options = document.querySelectorAll('.option-btn');
    options.forEach(opt => opt.classList.remove('selected', 'correct', 'incorrect'));
    
    // Yeni seçimi uygula
    const selectedBtn = Array.from(options).find(opt => opt.textContent === selectedOption);
    if (selectedBtn) {
        selectedBtn.classList.add('selected');
    }
    
    // Kullanıcı cevabını kaydet
    userAnswers[questionIndex] = selectedOption;
    
    // Feedback göster
    const question = questions[questionIndex];
    const isCorrect = selectedOption === question.correct_answer;
    
    const feedbackContainer = document.getElementById('feedback-container');
    feedbackContainer.classList.remove('hidden');
    
    if (isCorrect) {
        feedbackContainer.classList.add('correct');
        feedbackContainer.classList.remove('incorrect');
        document.getElementById('feedback-text').textContent = 'Doğru cevap!';
        
        // Doğru olan seçeneği belirt
        if (selectedBtn) {
            selectedBtn.classList.add('correct');
        }
    } else {
        feedbackContainer.classList.add('incorrect');
        feedbackContainer.classList.remove('correct');
        document.getElementById('feedback-text').textContent = `Yanlış cevap. Doğru cevap: ${question.correct_answer}`;
        
        // Yanlış olan seçeneği belirt
        if (selectedBtn) {
            selectedBtn.classList.add('incorrect');
        }
        
        // Doğru olan seçeneği göster
        const correctBtn = Array.from(options).find(opt => opt.textContent === question.correct_answer);
        if (correctBtn) {
            correctBtn.classList.add('correct');
        }
    }
    
    // Skoru ve ilerlemeyi güncelle
    updateScore();
    updateSCORMProgress();
}

// Skoru hesapla
function updateScore() {
    score = 0;
    let answeredCount = 0;
    
    for (let i = 0; i < questions.length; i++) {
        if (userAnswers[i] !== null) {
            answeredCount++;
            if (userAnswers[i] === questions[i].correct_answer) {
                score++;
            }
        }
    }
    
    return Math.round((score / questions.length) * 100);
}

// SCORM ilerleme bilgisini güncelle
function updateSCORMProgress() {
    const answeredCount = userAnswers.filter(answer => answer !== null).length;
    const progress = Math.round((answeredCount / questions.length) * 100);
    const scorePercent = updateScore();
    
    setSCORMProgress(progress, scorePercent);
}

// İlerleme çubuğunu güncelle
function updateProgressBar() {
    const answeredCount = userAnswers.filter(answer => answer !== null).length;
    const progress = Math.round((answeredCount / questions.length) * 100);
    document.getElementById('progress-fill').style.width = `${progress}%`;
}

// Önceki soruya git
function goToPrevQuestion() {
    if (currentQuestionIndex > 0) {
        currentQuestionIndex--;
        loadQuestion(currentQuestionIndex);
    }
}

// Sonraki soruya git
function goToNextQuestion() {
    if (currentQuestionIndex < questions.length - 1) {
        currentQuestionIndex++;
        loadQuestion(currentQuestionIndex);
    } else {
        showResults();
    }
}

// Sonuçları göster
function showResults() {
    document.getElementById('question-screen').classList.add('hidden');
    document.getElementById('results-screen').classList.remove('hidden');
    
    const scorePercent = updateScore();
    const answeredCount = userAnswers.filter(answer => answer !== null).length;
    
    document.getElementById('results-summary').innerHTML = `
        <p>Toplam ${questions.length} sorudan ${answeredCount} tanesini cevapladınız.</p>
        <p>Doğru cevap sayısı: ${score}</p>
        <p>Başarı oranı: %${scorePercent}</p>
    `;
    
    // Detaylı sonuçları göster
    const detailedResults = document.getElementById('detailed-results');
    detailedResults.innerHTML = '<h3>Soru Detayları</h3>';
    
    questions.forEach((question, index) => {
        const userAnswer = userAnswers[index];
        const isCorrect = userAnswer === question.correct_answer;
        
        const resultItem = document.createElement('div');
        resultItem.className = `result-item ${isCorrect ? 'correct' : 'incorrect'}`;
        
        resultItem.innerHTML = `
            <p><strong>Soru ${index + 1}:</strong> ${question.question}</p>
            <p>Doğru cevap: ${question.correct_answer}</p>
            <p>Sizin cevabınız: ${userAnswer || 'Cevaplanmadı'}</p>
        `;
        
        detailedResults.appendChild(resultItem);
    });
    
    // SCORM'u tamamla
    completeSCORM(scorePercent);
}

// Quiz'i yeniden başlat
function restartQuiz() {
    currentQuestionIndex = 0;
    userAnswers = new Array(questions.length).fill(null);
    score = 0;
    document.getElementById('results-screen').classList.add('hidden');
    document.getElementById('question-screen').classList.remove('hidden');
    loadQuestion(currentQuestionIndex);
}

// Sayfa yüklendiğinde Quiz'i başlat
window.addEventListener('load', initializeQuiz);"""
    return js

def create_manifest_content():
    """SCORM manifest dosyasını oluşturur"""
    manifest = """<?xml version="1.0" encoding="UTF-8"?>
<manifest identifier="com.scorm.quiz" version="1.0"
          xmlns="http://www.imsproject.org/xsd/imscp_rootv1p1p2"
          xmlns:adlcp="http://www.adlnet.org/xsd/adlcp_rootv1p2"
          xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
          xsi:schemaLocation="http://www.imsproject.org/xsd/imscp_rootv1p1p2 imscp_rootv1p1p2.xsd
                              http://www.imsglobal.org/xsd/imsmd_rootv1p2p1 imsmd_rootv1p2p1.xsd
                              http://www.adlnet.org/xsd/adlcp_rootv1p2 adlcp_rootv1p2.xsd">
  <metadata>
    <schema>ADL SCORM</schema>
    <schemaversion>1.2</schemaversion>
  </metadata>
  <organizations default="default_org">
    <organization identifier="default_org">
      <title>Çoktan Seçmeli Quiz</title>
      <item identifier="item_1" identifierref="resource_1">
        <title>Çoktan Seçmeli Quiz</title>
        <adlcp:masteryscore>70</adlcp:masteryscore>
      </item>
    </organization>
  </organizations>
  <resources>
    <resource identifier="resource_1" type="webcontent" adlcp:scormtype="sco" href="index.html">
      <file href="index.html"/>
      <file href="styles/main.css"/>
      <file href="scripts/main.js"/>
      <file href="assets/questions.json"/>
    </resource>
  </resources>
</manifest>"""
    return manifest

if __name__ == "__main__":
    csv_file = input("CSV dosyasının yolunu girin (örn: sorular.csv): ")
    if os.path.exists(csv_file):
        output_scorm = create_scorm_package(csv_file)
        print(f"SCORM paketi başarıyla oluşturuldu: {output_scorm}")
    else:
        print("Dosya bulunamadı!")
