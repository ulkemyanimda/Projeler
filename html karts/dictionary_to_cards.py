import re
import json

def parse_dictionary_line(line):
    """Sözlük satırını ayrıştırır"""
    line = line.strip()
    if not line:
        return None
    
    # Kelimeyi ayır (: ya da → karakterine kadar)
    if ':' in line:
        parts = line.split(':', 1)
        word = parts[0].strip()
        rest = parts[1].strip()
    else:
        return None
    
    # Bağlantı bilgisini bul [Aile-Akrabalar-s. 169] formatında
    category_match = re.search(r'\[([^\]]+)-s\.\s*(\d+)\]', rest)
    category = ""
    image_num = ""
    
    if category_match:
        category = category_match.group(1)
        image_num = category_match.group(2)
        rest = rest.replace(category_match.group(0), '').strip()
    
    # Kalan metni anlam ve örnek olarak ayır
    # Genellikle ilk cümle anlam, ikinci cümle örnektir
    sentences = re.split(r'(?<=[.!?])\s+', rest)
    
    meaning = ""
    example = ""
    
    if len(sentences) >= 1:
        meaning = sentences[0].strip()
    if len(sentences) >= 2:
        example = ' '.join(sentences[1:]).strip()
    
    return {
        'word': word,
        'category': category,
        'image_num': image_num,
        'meaning': meaning,
        'example': example
    }

def generate_html_cards(dictionary_file_path, output_file_path):
    """Sözlük dosyasından HTML kelime kartları oluşturur"""
    
    # Sözlük dosyasını oku
    with open(dictionary_file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # Her satırı ayrıştır
    cards_data = []
    for line in lines:
        parsed = parse_dictionary_line(line)
        if parsed:
            cards_data.append(parsed)
    
    # JavaScript için JSON verisini hazırla
    cards_json = json.dumps(cards_data, ensure_ascii=False)
    
    # HTML içeriğini oluştur
    html_content = f"""<!DOCTYPE html>
<html lang="tr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Türkçe Kelime Kartları</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }}
        
        .container {{
            max-width: 1200px;
            margin: 0 auto;
        }}
        
        h1 {{
            text-align: center;
            color: white;
            margin-bottom: 30px;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.5);
            font-size: 2.5em;
        }}
        
        .controls {{
            text-align: center;
            margin-bottom: 30px;
        }}
        
        .btn {{
            background: #4CAF50;
            color: white;
            border: none;
            padding: 12px 24px;
            margin: 0 10px;
            border-radius: 25px;
            cursor: pointer;
            font-size: 16px;
            transition: all 0.3s ease;
            box-shadow: 0 4px 15px rgba(0,0,0,0.2);
        }}
        
        .btn:hover {{
            background: #45a049;
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(0,0,0,0.3);
        }}
        
        .btn-prev {{
            background: #ff6b6b;
        }}
        
        .btn-prev:hover {{
            background: #ff5252;
        }}
        
        .btn-next {{
            background: #4ecdc4;
        }}
        
        .btn-next:hover {{
            background: #26c6da;
        }}
        
        .card-container {{
            display: flex;
            justify-content: center;
            margin-bottom: 30px;
        }}
        
        .card {{
            background: white;
            border-radius: 20px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.3);
            padding: 30px;
            max-width: 500px;
            width: 100%;
            text-align: center;
            transform: scale(1);
            transition: all 0.3s ease;
        }}
        
        .card:hover {{
            transform: scale(1.02);
            box-shadow: 0 15px 40px rgba(0,0,0,0.4);
        }}
        
        .word {{
            font-size: 2.5em;
            color: #e74c3c;
            margin-bottom: 15px;
            font-weight: bold;
            text-shadow: 1px 1px 2px rgba(0,0,0,0.1);
        }}
        
        .category {{
            color: #9b59b6;
            font-size: 1.1em;
            margin-bottom: 20px;
            font-style: italic;
        }}
        
        .image-container {{
            margin: 20px 0;
        }}
        
        .word-image {{
            width: 410px;
            height: 349px;
            object-fit: cover;
            border-radius: 15px;
            box-shadow: 0 5px 15px rgba(0,0,0,0.2);
            max-width: 100%;
            height: auto;
        }}
        
        .meaning {{
            font-size: 1.3em;
            color: #2c3e50;
            margin-bottom: 20px;
            line-height: 1.5;
            background: #ecf0f1;
            padding: 15px;
            border-radius: 10px;
            border-left: 5px solid #3498db;
        }}
        
        .example {{
            font-size: 1.1em;
            color: #27ae60;
            font-style: italic;
            background: #d5f4e6;
            padding: 15px;
            border-radius: 10px;
            border-left: 5px solid #27ae60;
        }}
        
        .card-counter {{
            text-align: center;
            color: white;
            font-size: 1.2em;
            margin-bottom: 20px;
        }}
        
        .no-image {{
            color: #7f8c8d;
            font-style: italic;
            margin: 20px 0;
        }}
        
        @media (max-width: 768px) {{
            .card {{
                margin: 0 10px;
                padding: 20px;
            }}
            
            .word {{
                font-size: 2em;
            }}
            
            .word-image {{
                width: 100%;
                height: auto;
            }}
            
            h1 {{
                font-size: 2em;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>🇹🇷 Türkçe Kelime Kartları 📚</h1>
        
        <div class="card-counter">
            <span id="current-card">1</span> / <span id="total-cards">{len(cards_data)}</span>
        </div>
        
        <div class="controls">
            <button class="btn btn-prev" onclick="previousCard()">⬅ Önceki</button>
            <button class="btn" onclick="toggleCard()">🔄 Çevir</button>
            <button class="btn btn-next" onclick="nextCard()">Sonraki ➡</button>
        </div>
        
        <div class="card-container">
            <div class="card" id="word-card">
                <!-- Kart içeriği JavaScript ile doldurulacak -->
            </div>
        </div>
    </div>

    <script>
        const cardsData = {cards_json};
        
        let currentCardIndex = 0;
        let showingFront = true;
        let visitedCards = new Set(); // Ziyaret edilen kartları takip et
        
        function updateCardCounter() {{
            document.getElementById('current-card').textContent = currentCardIndex + 1;
        }}
        
        function displayCard(index, showFront = true) {{
            const card = cardsData[index];
            const cardElement = document.getElementById('word-card');
            visitedCards.add(index);
            
            if (showFront) {{
                // Ön yüz: Sadece kelime
                cardElement.innerHTML = `
                    <div class="current-word-indicator">Kelime #${{index + 1}} / ${{cardsData.length}}</div>
                    <div class="word">${{card.word}}</div>
                    <div style="color: #7f8c8d; margin-top: 20px;">Kartı çevirmek için 🔄 butonuna tıklayın</div>
                `;
            }} else {{
                // Arka yüz: Tüm bilgiler
                let imageHtml = '';
                if (card.image_num) {{
                    imageHtml = `
                        <div class="image-container">
                            <img src="imgs/${{card.image_num}}.png" alt="${{card.word}}" class="word-image" onerror="this.style.display='none'">
                        </div>
                    `;
                }}
                
                let categoryHtml = '';
                if (card.category) {{
                    categoryHtml = `<div class="category">📂 ${{card.category}}</div>`;
                }}
                
                cardElement.innerHTML = `
                    <div class="current-word-indicator">Kelime #${{index + 1}} / ${{cardsData.length}}</div>
                    <div class="word">${{card.word}}</div>
                    ${{categoryHtml}}
                    ${{imageHtml}}
                    <div class="meaning">💡 ${{card.meaning}}</div>
                    ${{card.example ? `<div class="example">📝 ${{card.example}}</div>` : ''}}
                `;
            }}
            
            updateCardCounter();
        }}
        
        function nextCard() {{
            if (currentCardIndex < cardsData.length - 1) {{
                currentCardIndex++;
                showingFront = true;
                displayCard(currentCardIndex, showingFront);
            }}
        }}
        
        function previousCard() {{
            if (currentCardIndex > 0) {{
                currentCardIndex--;
                showingFront = true;
                displayCard(currentCardIndex, showingFront);
            }}
        }}
        
        function toggleCard() {{
            showingFront = !showingFront;
            displayCard(currentCardIndex, showingFront);
        }}
        
        function randomCard() {{
            // Rastgele kart seç
            const randomIndex = Math.floor(Math.random() * cardsData.length);
            currentCardIndex = randomIndex;
            showingFront = true;
            displayCard(currentCardIndex, showingFront);
            hideSearchResults();
        }}
        
        function searchWord() {{
            const searchTerm = document.getElementById('search-input').value.trim().toLowerCase();
            if (!searchTerm) {{
                alert('Lütfen arama yapacağınız kelimeyi girin!');
                return;
            }}
            
            const resultsContainer = document.getElementById('search-results');
            const results = cardsData.filter((card, index) => 
                card.word.toLowerCase().includes(searchTerm) ||
                card.meaning.toLowerCase().includes(searchTerm) ||
                card.example.toLowerCase().includes(searchTerm)
            ).map((card, originalIndex) => {{
                // Orijinal indexi bul
                const realIndex = cardsData.findIndex(c => c.word === card.word);
                return {{ ...card, realIndex }};
            }});
            
            if (results.length === 0) {{
                resultsContainer.innerHTML = '<div class="search-result-item">Sonuç bulunamadı 😔</div>';
                resultsContainer.style.display = 'block';
                return;
            }}
            
            if (results.length === 1) {{
                // Tek sonuç varsa direkt git
                currentCardIndex = results[0].realIndex;
                showingFront = true;
                displayCard(currentCardIndex, showingFront);
                hideSearchResults();
                return;
            }}
            
            // Çoklu sonuçları göster
            resultsContainer.innerHTML = results.slice(0, 10).map(result => `
                <div class="search-result-item" onclick="goToCard(${{result.realIndex}})">
                    <strong>${{result.word}}</strong> - ${{result.meaning.substring(0, 50)}}...
                </div>
            `).join('');
            
            if (results.length > 10) {{
                resultsContainer.innerHTML += `<div class="search-result-item" style="text-align: center; color: #7f8c8d;">+${{results.length - 10}} sonuç daha...</div>`;
            }}
            
            resultsContainer.style.display = 'block';
        }}
        
        function goToCard(index) {{
            currentCardIndex = index;
            showingFront = true;
            displayCard(currentCardIndex, showingFront);
            hideSearchResults();
            document.getElementById('search-input').value = '';
        }}
        
        function hideSearchResults() {{
            document.getElementById('search-results').style.display = 'none';
        }}
        
        // Klavye kontrolları
        document.addEventListener('keydown', function(event) {{
            // Arama kutusuna odaklanılmışsa klavye kısayollarını devre dışı bırak
            if (document.activeElement === document.getElementById('search-input')) {{
                if (event.key === 'Enter') {{
                    searchWord();
                }}
                return;
            }}
            
            switch(event.key) {{
                case 'ArrowLeft':
                    previousCard();
                    break;
                case 'ArrowRight':
                    nextCard();
                    break;
                case ' ':
                case 'Enter':
                    event.preventDefault();
                    toggleCard();
                    break;
                case 'r':
                case 'R':
                    randomCard();
                    break;
                case '/':
                    event.preventDefault();
                    document.getElementById('search-input').focus();
                    break;
                case 'Escape':
                    hideSearchResults();
                    document.getElementById('search-input').blur();
                    break;
            }}
        }});
        
        // Sayfaya tıklanınca arama sonuçlarını gizle
        document.addEventListener('click', function(event) {{
            const searchContainer = event.target.closest('.search-container');
            const searchResults = event.target.closest('.search-results');
            if (!searchContainer && !searchResults) {{
                hideSearchResults();
            }}
        }});
        
        // İlk kartı rastgele seç
        randomCard();
    </script>
</body>
</html>"""
    
    # Dosyaya yaz
    with open(output_file_path, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"✅ {len(cards_data)} kelime kartı başarıyla oluşturuldu!")
    print(f"📁 Dosya kaydedildi: {output_file_path}")
    print("🖼️  imgs/ klasörüne resimlerinizi koyup HTML dosyasını açabilirsiniz.")

# Kullanım örneği
if __name__ == "__main__":
    # Sözlük dosyasının yolunu belirtin
    dictionary_file = "sozluk.txt"  # Sözlük dosyanızın adı
    output_file = "kelime_kartlari.html"  # Çıktı HTML dosyası
    
    try:
        generate_html_cards(dictionary_file, output_file)
        print("\n🎉 Kelime kartları hazır! Şimdi şunları yapın:")
        print("1. imgs/ adında bir klasör oluşturun")
        print("2. Resimleri imgs/169.png, imgs/170.png şeklinde bu klasöre koyun")
        print(f"3. {output_file} dosyasını tarayıcıda açın")
        print("\n⌨️  Klavye kısayolları:")
        print("   • Sol/Sağ ok tuşları: Kartlar arası geçiş")
        print("   • Boşluk/Enter: Kartı çevir")
    except FileNotFoundError:
        print(f"❌ Hata: '{dictionary_file}' dosyası bulunamadı!")
        print("Lütfen sözlük dosyanızı doğru isimle kaydedin veya kodu düzenleyin.")
    except Exception as e:
        print(f"❌ Hata oluştu: {e}")
