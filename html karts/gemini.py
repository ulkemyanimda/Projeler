import re

def parse_line(line):
    """
    Bir sözlük satırını kelime, resim_no, anlam ve örnek olarak ayrıştırır.
    Örnek: 'abi / ağabey: [Aile-Akrabalar-s. 169] Büyük erkek kardeş. Ben 9 yaşındayım, abim 16 yaşında.'
    """
    # Regex deseni:
    # 1. Grup (kelime): ':' karakterine kadar olan her şey.
    # 2. Grup (resim_no): '[...s. 169...]' içindeki sayı. Bu bölüm opsiyoneldir.
    # 3. Grup (anlam): Bağlantıdan sonraki ve ilk noktaya kadar olan bölüm.
    # 4. Grup (örnek): Anlamdan sonra satırın geri kalanı.
    pattern = r"^(.*?):\s*(?:\[.*?s\.\s*(\d+).*?\])?\s*(.*?)\.\s*(.*)$"
    
    match = re.match(pattern, line)
    
    if not match:
        return None

    kelime = match.group(1).strip()
    resim_no = match.group(2) # None olabilir eğer bağlantı yoksa
    anlam = match.group(3).strip() + '.'
    ornek = match.group(4).strip()
    
    return {
        'kelime': kelime,
        'resim_no': resim_no,
        'anlam': anlam,
        'ornek': ornek
    }

def create_html_card(data):
    """
    Verilen sözlük verisinden bir HTML kart bloğu oluşturur.
    """
    kelime = data['kelime']
    resim_no = data['resim_no']
    anlam = data['anlam']
    ornek = data['ornek']
    
    # Resim varsa, <img> etiketini oluştur.
    resim_html = ""
    if resim_no:
        resim_html = f'<img src="imgs/{resim_no}.png" alt="{kelime}" width="410" height="349">'
        
    # HTML kart şablonu
    card_html = f"""
    <div class="card">
        {resim_html}
        <div class="card-content">
            <h2 class="word">{kelime}</h2>
            <p class="definition">{anlam}</p>
            <p class="example">"{ornek}"</p>
        </div>
    </div>
    """
    return card_html

def generate_html_file(input_file='sozluk.txt', output_file='kelime_kartlari.html'):
    """
    Giriş dosyasını okur ve tüm kelime kartlarını içeren HTML dosyasını oluşturur.
    """
    # HTML dosyasının başlangıcı ve CSS stilleri
    html_template_start = """
<!DOCTYPE html>
<html lang="tr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Kelime Kartları</title>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Roboto:ital,wght@0,400;0,700;1,400&display=swap');

        body {
            font-family: 'Roboto', sans-serif;
            background-color: #f0f2f5;
            color: #333;
            margin: 0;
            padding: 20px;
        }
        .container {
            display: flex;
            flex-wrap: wrap;
            justify-content: center;
            gap: 25px;
        }
        .card {
            background-color: #ffffff;
            border-radius: 12px;
            box-shadow: 0 6px 12px rgba(0,0,0,0.1);
            overflow: hidden;
            width: 410px;
            transition: transform 0.2s ease-in-out;
        }
        .card:hover {
            transform: translateY(-5px);
        }
        .card img {
            display: block;
            width: 410px;
            height: 349px;
            object-fit: cover; /* Resmin orantısını bozmadan alanı kaplamasını sağlar */
        }
        .card-content {
            padding: 20px;
        }
        .word {
            font-size: 2em; /* 32px */
            color: #005A9C; /* Koyu Mavi */
            margin: 0 0 10px 0;
            font-weight: 700;
        }
        .definition {
            font-size: 1.1em; /* 18px */
            color: #1d1d1d; /* Koyu Gri */
            margin: 0 0 15px 0;
        }
        .example {
            font-size: 1em; /* 16px */
            color: #2E7D32; /* Yeşil */
            font-style: italic;
            margin: 0;
            padding-left: 15px;
            border-left: 3px solid #AED581; /* Açık Yeşil */
        }
    </style>
</head>
<body>
    <div class="container">
"""

    # HTML dosyasının sonu
    html_template_end = """
    </div>
</body>
</html>
"""

    with open(output_file, 'w', encoding='utf-8') as f_out:
        f_out.write(html_template_start)
        
        try:
            with open(input_file, 'r', encoding='utf-8') as f_in:
                for line in f_in:
                    if line.strip(): # Boş satırları atla
                        data = parse_line(line)
                        if data:
                            card = create_html_card(data)
                            f_out.write(card)
                        else:
                            print(f"Uyarı: Bu satır ayrıştırılamadı -> {line.strip()}")
            
            f_out.write(html_template_end)
            print(f"Başarılı! '{output_file}' dosyası oluşturuldu.")

        except FileNotFoundError:
            print(f"Hata: '{input_file}' dosyası bulunamadı. Lütfen dosya adını ve konumunu kontrol edin.")


if __name__ == "__main__":
    generate_html_file()