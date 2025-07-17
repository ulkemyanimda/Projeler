// SCORM API Entegrasyonu
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
window.addEventListener('load', initializeQuiz);