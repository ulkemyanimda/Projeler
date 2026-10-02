import os
import cairosvg

INPUT_FOLDER = "logos"
OUTPUT_FOLDER = "pngler"

# SVG'yi kaç kat büyütmek istediğin
SCALE = 4

os.makedirs(OUTPUT_FOLDER, exist_ok=True)

for filename in os.listdir(INPUT_FOLDER):

    if not filename.lower().endswith(".svg"):
        continue

    svg_path = os.path.join(INPUT_FOLDER, filename)
    png_name = os.path.splitext(filename)[0] + ".png"
    png_path = os.path.join(OUTPUT_FOLDER, png_name)

    cairosvg.svg2png(
        url=svg_path,
        write_to=png_path,
        scale=SCALE
    )

    print(f"✓ {filename} → {png_name}")

print("\nTüm SVG dosyaları başarıyla dönüştürüldü.")