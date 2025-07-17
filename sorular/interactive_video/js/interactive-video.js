
// YouTube API'si yüklendiğinde çağrılacak fonksiyon
let player;
let playerState = -1;
let currentTime = 0;
let questionsShown = [];
let score = 0;
let checkInterval;
let totalQuestions = 11;

// Soruların listesi
const questions = [
  {
    "time": 43,
    "question": "Sevgili \u00e7ocuklar, sizce \u201c\u00c7anakkale Ge\u00e7ilmez\u201d ne demektir?",
    "options": [
      "\u00c7anakkale Sava\u015f\u0131\u2019nda T\u00fcrk askerlerinin b\u00fcy\u00fck bir kahramanl\u0131kla vatan\u0131 savunarak d\u00fc\u015fman\u0131 ge\u00e7irmemesi anlam\u0131na gelir.",
      " \u00c7anakkale'de hi\u00e7 sava\u015f olmam\u0131\u015ft\u0131r, bu y\u00fczden kimse ge\u00e7ememi\u015ftir. ",
      "\u00c7anakkale sadece turistlere kapal\u0131 oldu\u011fu i\u00e7in ge\u00e7ilemez denmi\u015ftir. ",
      "\u00c7anakkale\u2019de k\u00f6pr\u00fc olmad\u0131\u011f\u0131 i\u00e7in ge\u00e7mek m\u00fcmk\u00fcn olmam\u0131\u015ft\u0131r."
    ],
    "correct_index": 0
  },
  {
    "time": 97,
    "question": "\u00c7ocuklar haftasonu gezisi i\u00e7in hangi \u015fehri ziyaret edecekler?",
    "options": [
      "Edirne",
      "Sivas",
      "\u00c7anakkale",
      "Kaysei"
    ],
    "correct_index": 2
  },
  {
    "time": 135,
    "question": "Cephe ne demektir?",
    "options": [
      "Sava\u015f\u0131n yap\u0131ld\u0131\u011f\u0131 yer",
      "Askerlerin s\u0131\u011f\u0131na\u011f\u0131",
      "Askerlerin yemek yedi\u011fi yer",
      ""
    ],
    "correct_index": 0
  },
  {
    "time": 180,
    "question": "D\u00fc\u015fmanlar \u00c7anakkale'yi ge\u00e7ip hangi \u015fehire gitmek istiyorlard\u0131?",
    "options": [
      "Samsun",
      "\u0130stanbul",
      "Ankara",
      ""
    ],
    "correct_index": 1
  },
  {
    "time": 200,
    "question": "Bu g\u00f6rd\u00fc\u011f\u00fcn\u00fcz top mermisi ka\u00e7 kg a\u011f\u0131rl\u0131\u011f\u0131nda olabilir?",
    "options": [
      "10",
      "200",
      "275",
      "300"
    ],
    "correct_index": 2
  },
  {
    "time": 223,
    "question": "275 kiloluk top mermisini ta\u015f\u0131yan kahraman askerrin ad\u0131 nedir?",
    "options": [
      "Seyit Onba\u015f\u0131 ",
      "Koca Yusuf",
      "Naim S\u00fcleymano\u011flu ",
      "Kara Fatma"
    ],
    "correct_index": 0
  },
  {
    "time": 282,
    "question": "D\u00fc\u015fman gemilerinin geri d\u00f6nmesini sa\u011flayan may\u0131n gemisinin ad\u0131 nedir?",
    "options": [
      "Seyit",
      "Nusret",
      "Murat",
      ""
    ],
    "correct_index": 1
  },
  {
    "time": 311,
    "question": "Conk bay\u0131r\u0131ndan sava\u015f\u0131 y\u00f6neten komutan kimdir?",
    "options": [
      "Enver Pa\u015fa",
      "Gazi Osman Pa\u015fa",
      "Mustafa Kemal Atat\u00fcrk",
      "Kaz\u0131m Karabekir"
    ],
    "correct_index": 2
  },
  {
    "time": 341,
    "question": "\u015eehit ne demektir?",
    "options": [
      "Vatan\u0131n\u0131 korumak i\u00e7in yaralanan ki\u015fi",
      "Vatan\u0131n\u0131 korumak i\u00e7in askere giden ki\u015fi",
      "Vatan\u0131n\u0131 korumak i\u00e7in can\u0131n\u0131 veren ki\u015fi",
      ""
    ],
    "correct_index": 2
  },
  {
    "time": 371,
    "question": "Sizce \u00c7anakkale\u2019yi \u201cge\u00e7ilmez\u201d yapan nedir?",
    "options": [
      "T\u00fcrk askerlerinin vatan sevgisi, cesareti ve birlik ruhu",
      "D\u00fc\u015fman gemilerinin yanl\u0131\u015f yola sapmas\u0131",
      "Havan\u0131n \u00e7ok ya\u011fmurlu olmas\u0131",
      "\u00c7anakkale\u2019de hi\u00e7 sava\u015f olmamas\u0131"
    ],
    "correct_index": 0
  },
  {
    "time": 434,
    "question": "\u00c7anakkale'yi ge\u00e7ilmez k\u0131lan a\u015fa\u011f\u0131dakilerden hangisidir?",
    "options": [
      "Askerlerin cesareti ve merhameti",
      "Askerlerin azmi ve kararl\u0131l\u0131\u011f\u0131",
      "\u00c7anakkale ruhu",
      "hepsi"
    ],
    "correct_index": 3
  }
];

// API hazır olduğunda çağrılır
function onYouTubeIframeAPIReady() {
    player = new YT.Player('player', {
        height: '500',
        width: '100%',
        videoId: 'LRrVe9yYt4I',
        playerVars: {
            'playsinline': 1,
            'rel': 0,
            'modestbranding': 1,
            'controls': 1
        },
        events: {
            'onReady': onPlayerReady,
            'onStateChange': onPlayerStateChange
        }
    });
}

// Player hazır olduğunda çağrılır
function onPlayerReady(event) {
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
}

// Player durumu değiştiğinde çağrılır
function onPlayerStateChange(event) {
    playerState = event.data;
    
    // Video bittiğinde
    if (event.data === YT.PlayerState.ENDED) {
        clearInterval(checkInterval);
        showCompletionMessage();
        completeSCORM();
    }
    
    // Video oynatılıyorsa timeline'ı güncelle
    if (event.data === YT.PlayerState.PLAYING) {
        setInterval(updateTimelineProgress, 1000);
    }
}

// Video zamanını kontrol et ve soruları göster
function checkVideoTime() {
    if (playerState === YT.PlayerState.PLAYING) {
        currentTime = Math.floor(player.getCurrentTime());
        
        // Her soru için kontrol et
        questions.forEach(function(question, index) {
            // Videoda ilgili zamana ulaşıldı mı ve soru daha önce gösterilmedi mi?
            if (currentTime === question.time && !questionsShown.includes(question.time)) {
                questionsShown.push(question.time);
                showQuestion(question, index);
                markQuestionAsShown(index);
            }
        });
    }
}

// Timeline ilerleme çubuğunu güncelle
function updateTimelineProgress() {
    if (player && playerState === YT.PlayerState.PLAYING) {
        const duration = player.getDuration();
        const currentTime = player.getCurrentTime();
        const progressPercent = (currentTime / duration) * 100;
        document.querySelector('.timeline-progress').style.width = progressPercent + '%';
    }
}

// Sorguları timeline üzerinde işaretle
function createQuestionMarkers() {
    const timelineMarkers = document.querySelector('.timeline-markers');
    const duration = player.getDuration();
    
    questions.forEach((question, index) => {
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
        marker.addEventListener('click', function() {
            player.seekTo(question.time);
        });
    });
}

// Soruyu göster
function showQuestion(question, questionIndex) {
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
    question.options.forEach((option, index) => {
        const button = document.createElement('button');
        button.className = 'option-btn';
        button.textContent = option;
        button.onclick = function() { checkAnswer(index, question.correct_index, questionIndex); };
        optionsContainer.appendChild(button);
    });
    
    // Continue butonunu gizle
    document.getElementById('continue-btn').style.display = 'none';
    
    // Overlay'i göster
    document.getElementById('question-overlay').style.display = 'block';
}

// Cevabı kontrol et
function checkAnswer(selectedIndex, correctIndex, questionIndex) {
    // Tüm butonları devre dışı bırak
    const buttons = document.querySelectorAll('.option-btn');
    buttons.forEach(button => {
        button.classList.add('disabled');
        button.disabled = true;
    });
    
    // Seçilen ve doğru cevabı işaretle
    buttons[selectedIndex].classList.add(selectedIndex === correctIndex ? 'correct' : 'incorrect');
    if (selectedIndex !== correctIndex) {
        buttons[correctIndex].classList.add('correct');
    }
    
    const feedback = document.getElementById('feedback');
    
    if (selectedIndex === correctIndex) {
        feedback.innerHTML = '<span class="correct">✓ Doğru cevap!</span>';
        score++;
    } else {
        feedback.innerHTML = '<span class="incorrect">✗ Yanlış cevap!</span>';
    }
    
    feedback.classList.add('visible');
    
    // Devam butonunu göster
    document.getElementById('continue-btn').style.display = 'inline-block';
    
    // İlerleme bilgilerini güncelle
    updateProgressDisplay();
    
    // Timeline üzerindeki işareti güncelle
    markQuestionAsAnswered(questionIndex);
}

// Soruyu cevaplanmış olarak işaretle
function markQuestionAsAnswered(questionIndex) {
    const marker = document.getElementById('marker-' + questionIndex);
    if (marker) {
        marker.classList.add('answered-marker');
    }
}

// Soruyu gösterilmiş olarak işaretle
function markQuestionAsShown(questionIndex) {
    // Gelecekte ek özellikler için bu fonksiyon kullanılabilir
}

// Devam et butonuna tıklandığında
function continueVideo() {
    document.getElementById('question-overlay').style.display = 'none';
    player.playVideo();
}

// İlerleme bilgilerini güncelle
function updateProgressDisplay() {
    document.getElementById('questions-answered').textContent = questionsShown.length;
    document.getElementById('questions-total').textContent = totalQuestions;
    document.getElementById('correct-answers').textContent = score;
    
    // Yüzde hesapla (en az 1 soru gösterilmişse)
    let percentage = 0;
    if (questionsShown.length > 0) {
        percentage = Math.round((score / questionsShown.length) * 100);
    }
    document.getElementById('success-percent').textContent = percentage;
    
    // İlerleme çubuğunu güncelle
    const progressPercent = (questionsShown.length / totalQuestions) * 100;
    document.querySelector('.progress-fill').style.width = progressPercent + '%';
}

// Tamamlama mesajını göster
function showCompletionMessage() {
    const percentage = Math.round((score / totalQuestions) * 100);
    const completionMessage = document.getElementById('completion-message');
    
    if (percentage >= 70) {
        completionMessage.textContent = 'Tebrikler! Başarıyla tamamladınız. Başarı oranınız: ' + percentage + '%';
    } else {
        completionMessage.textContent = 'Videoyu tamamladınız. Başarı oranınız: ' + percentage + '%';
    }
    
    completionMessage.style.display = 'block';
    
    // Tüm soruları göster
    const timelineMarkers = document.querySelectorAll('.question-marker');
    timelineMarkers.forEach(marker => {
        if (!marker.classList.contains('answered-marker')) {
            marker.style.backgroundColor = '#e74c3c';
        }
    });
}

// Timeline'a tıklandığında video konumunu değiştir
function setupTimelineClicks() {
    const timeline = document.querySelector('.timeline');
    timeline.addEventListener('click', function(e) {
        const timelineWidth = this.offsetWidth;
        const clickPosition = e.offsetX;
        const duration = player.getDuration();
        
        const seekTime = (clickPosition / timelineWidth) * duration;
        player.seekTo(seekTime);
    });
}

// SCORM iletişimi için basit fonksiyonlar
function initializeSCORM() {
    if (window.parent && window.parent.API) {
        window.parent.API.LMSInitialize("");
    }
}

function completeSCORM() {
    if (window.parent && window.parent.API) {
        const scorePercent = (score / totalQuestions) * 100;
        window.parent.API.LMSSetValue("cmi.core.score.raw", scorePercent);
        window.parent.API.LMSSetValue("cmi.core.lesson_status", "completed");
        window.parent.API.LMSCommit("");
        window.parent.API.LMSFinish("");
    }
}

// Sayfa yüklendiğinde
document.addEventListener('DOMContentLoaded', function() {
    // Timeline tıklama işlevini etkinleştir
    setupTimelineClicks();
    
    // Devam et butonuna tıklama işlevi
    document.getElementById('continue-btn').addEventListener('click', continueVideo);
});
