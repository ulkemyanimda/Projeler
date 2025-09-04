import re

def parse_line(line):
    pattern = r"^(.*?):\s*(?:\[.*?s\.\s*(\d+).*?\])?\s*(.*?)\.\s*(.*)$"
    match = re.match(pattern, line)
    if not match: return None
    return {'kelime': match.group(1).strip(), 'resim_no': match.group(2), 'anlam': match.group(3).strip() + '.', 'ornek': match.group(4).strip()}

def create_html_card(data):
    resim_html = f'<img src="imgs/{data["resim_no"]}.png" alt="{data["kelime"]}" width="410" height="349">' if data['resim_no'] else ""
    return f"""
    <div class="card">
        {resim_html}
        <div class="card-content">
            <h2 class="word">{data['kelime']}</h2>
            <p class="definition">{data['anlam']}</p>
            <p class="example">"{data['ornek']}"</p>
        </div>
    </div>
    """

def generate_html_file(input_file='sozluk.txt', output_file='kelime_kartlari.html'):
    html_template_start = """
<!DOCTYPE html>
<html lang="tr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Kelime Kartları</title>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Roboto:ital,wght@0,400;0,700;1,400&display=swap');
        body { font-family: 'Roboto', sans-serif; background-color: #f0f2f5; color: #333; margin: 0; padding: 20px; }
        .search-container { text-align: center; margin-bottom: 30px; padding: 10px; }
        #searchInput { width: 50%; max-width: 500px; padding: 15px 25px; font-size: 1.1em; border-radius: 30px; border: 1px solid #ddd; box-shadow: 0 4px 8px rgba(0,0,0,0.05); transition: all 0.3s ease-in-out; }
        #searchInput:focus { outline: none; border-color: #007bff; box-shadow: 0 4px 12px rgba(0,123,255,0.2); }
        .container { display: flex; flex-wrap: wrap; justify-content: center; gap: 25px; }
        .card { background-color: #ffffff; border-radius: 12px; box-shadow: 0 6px 12px rgba(0,0,0,0.1); overflow: hidden; width: 410px; transition: transform 0.2s ease-in-out; display: block; }
        .card:hover { transform: translateY(-5px); }
        .card img { display: block; width: 410px; height: 349px; object-fit: cover; }
        .card-content { padding: 20px; }
        .word { font-size: 2em; color: #005A9C; margin: 0 0 10px 0; font-weight: 700; }
        .definition { font-size: 1.1em; color: #1d1d1d; margin: 0 0 15px 0; }
        .example { font-size: 1em; color: #2E7D32; font-style: italic; margin: 0; padding-left: 15px; border-left: 3px solid #AED581; }
    </style>
</head>
<body>
    <div class="search-container">
        <input type="text" id="searchInput" placeholder="Kartlar içinde kelime ara...">
    </div>
    <div class="container">
"""
    html_template_end = """
    </div>
    <script>
        document.addEventListener('DOMContentLoaded', function() {
            const searchInput = document.getElementById('searchInput');
            const cards = document.querySelectorAll('.card');
            searchInput.addEventListener('input', function() {
                const searchTerm = this.value.toLocaleLowerCase('tr-TR');
                cards.forEach(function(card) {
                    const wordElement = card.querySelector('.word');
                    if (wordElement) {
                        const wordText = wordElement.textContent.toLocaleLowerCase('tr-TR');
                        if (wordText.includes(searchTerm)) {
                            card.style.display = 'block';
                        } else {
                            card.style.display = 'none';
                        }
                    }
                });
            });
        });
    </script>
</body>
</html>
"""
    try:
        with open(output_file, 'w', encoding='utf-8') as f_out:
            f_out.write(html_template_start)
            with open(input_file, 'r', encoding='utf-8') as f_in:
                for line in f_in:
                    if line.strip():
                        data = parse_line(line)
                        if data: f_out.write(create_html_card(data))
                        else: print(f"Uyarı: Bu satır ayrıştırılamadı -> {line.strip()}")
            f_out.write(html_template_end)
            print(f"Başarılı! Arama özellikli '{output_file}' dosyası oluşturuldu.")
    except FileNotFoundError:
        print(f"Hata: '{input_file}' dosyası bulunamadı. Lütfen dosya adını ve konumunu kontrol edin.")

if __name__ == "__main__":
    generate_html_file()