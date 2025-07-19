import os

# Klasör adı
folder_path = 'text_output'
# Birleştirilmiş dosya adı
output_file = 'merged_output.txt'

# Yazma modunda çıktı dosyasını aç
with open(output_file, 'w', encoding='utf-8') as outfile:
    for filename in sorted(os.listdir(folder_path)):
        file_path = os.path.join(folder_path, filename)
        if os.path.isfile(file_path) and filename.endswith('.txt'):
            with open(file_path, 'r', encoding='utf-8') as infile:
                content = infile.read()
                outfile.write(f'--- {filename} ---\n')  # İsteğe bağlı: dosya adını belirt
                outfile.write(content + '\n\n')

print(f"Tüm dosyalar '{output_file}' adlı dosyada birleştirildi.")
