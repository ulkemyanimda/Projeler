import qrcode
import qrcode.image.svg

# vCard bilgileri
first_name = "Kahraman"
last_name = "Koştaş"
organization = "YYEGM"
title = "Millî Eğitim Uzmanı"
phone_work = "+90 312 413 5646"
phone_mobile = "+90 555 555 5555"
email = "kahraman.kostas@meb.gov.tr"
website = "https://kahramankostas.github.io"

# vCard formatı
vcard = f"""BEGIN:VCARD
VERSION:3.0
N:{last_name};{first_name};;;
FN:{first_name} {last_name}
ORG:{organization}
TITLE:{title}
TEL;TYPE=WORK,VOICE:{phone_work}
TEL;TYPE=CELL,VOICE:{phone_mobile}
EMAIL:{email}
URL:{website}
END:VCARD
"""

# vCard'ı bir dosyaya kaydet (opsiyonel)
with open("contact.vcf", "w", encoding="utf-8") as f:
    f.write(vcard)

# SVG QR kod üretici
factory = qrcode.image.svg.SvgImage

# QR kod oluştur
qr = qrcode.QRCode(version=3, box_size=10, border=4)
qr.add_data(vcard)
qr.make(fit=True)

# SVG görsel oluştur ve kaydet
img = qr.make_image(image_factory=factory)
img.save("contact_qr.svg")

print("vCard dosyası (contact.vcf) ve SVG QR kod (contact_qr.svg) başarıyla oluşturuldu.")
