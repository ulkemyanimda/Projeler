# Girdi ve çıktı dosyalarının adlarını belirtiyoruz.
input_filename = 'dosya.txt'
output_filename = 'duzenlenmis_dosya.txt'

# İşlenmiş ve tek satır haline getirilmiş girişleri saklamak için boş bir liste oluşturuyoruz.
processed_lines = []
# Mevcut girişi (kelime ve tanımını) birleştirmek için geçici bir değişken.
current_entry = ""

try:
    # Dosyayı UTF-8 formatında okumak için açıyoruz (Türkçe karakterler için önemli).
    with open(input_filename, 'r', encoding='utf-8') as file:
        # Dosyadaki tüm satırları okuyoruz.
        for line in file:
            # Satır başı ve sonundaki boşlukları temizliyoruz.
            stripped_line = line.strip()

            # Eğer satır boşsa atlıyoruz.
            if not stripped_line:
                continue

            # Eğer satırda ':' karakteri varsa, bu yeni bir kelime tanımının başlangıcıdır.
            if ':' in stripped_line:
                # Eğer daha önceden biriktirdiğimiz bir giriş varsa, bunu listeye ekliyoruz.
                if current_entry:
                    processed_lines.append(current_entry)
                
                # Yeni girişi bu satır olarak başlatıyoruz.
                current_entry = stripped_line
            else:
                # Eğer satırda ':' yoksa, bu bir önceki girişin devamıdır.
                # Bir boşluk ekleyerek mevcut girişe ekliyoruz.
                current_entry += ' ' + stripped_line

    # Dosyanın sonundaki son girişi de listeye eklemeyi unutmuyoruz.
    if current_entry:
        processed_lines.append(current_entry)

    # Düzenlenmiş verileri yeni bir dosyaya yazıyoruz.
    with open(output_filename, 'w', encoding='utf-8') as file:
        for line in processed_lines:
            file.write(line + '\n')

    print(f"İşlem başarıyla tamamlandı! Düzenlenmiş dosyanız '{output_filename}' adıyla kaydedildi.")

except FileNotFoundError:
    print(f"Hata: '{input_filename}' adında bir dosya bulunamadı. Lütfen dosya adını kontrol edin.")
except Exception as e:
    print(f"Bir hata oluştu: {e}")