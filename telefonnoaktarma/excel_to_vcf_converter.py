import pandas as pd
import os
from datetime import datetime

def excel_to_vcf(excel_file, vcf_file="contacts.vcf"):
    """
    Excel dosyasını VCF formatına dönüştürür
    
    Args:
        excel_file (str): Excel dosyasının yolu
        vcf_file (str): Oluşturulacak VCF dosyasının adı
    """
    
    try:
        # Excel dosyasını oku
        df = pd.read_excel(excel_file)
        
        # Sütun isimlerini kontrol et ve standartlaştır
        expected_columns = ['Ad Soyad', 'Email', 'Telefon', 'Etiket']
        
        # Sütun isimlerini temizle (boşlukları kaldır)
        df.columns = df.columns.str.strip()
        
        print("Excel dosyasındaki sütunlar:", df.columns.tolist())
        
        # Eksik sütunları kontrol et
        missing_columns = [col for col in expected_columns if col not in df.columns]
        if missing_columns:
            print(f"Uyarı: Bu sütunlar bulunamadı: {missing_columns}")
        
        # VCF dosyasını oluştur
        vcf_content = []
        
        for index, row in df.iterrows():
            # Boş satırları atla
            if pd.isna(row.get('Ad Soyad', '')) and pd.isna(row.get('Email', '')) and pd.isna(row.get('Telefon', '')):
                continue
                
            # vCard başlat
            vcf_content.append("BEGIN:VCARD")
            vcf_content.append("VERSION:3.0")
            
            # Ad Soyad
            full_name = str(row.get('Ad Soyad', '')).strip() if pd.notna(row.get('Ad Soyad', '')) else ''
            if full_name:
                # İsim ve soyismi ayır
                name_parts = full_name.split(' ', 1)
                first_name = name_parts[0] if len(name_parts) > 0 else ''
                last_name = name_parts[1] if len(name_parts) > 1 else ''
                
                vcf_content.append(f"FN:{full_name}")
                vcf_content.append(f"N:{last_name};{first_name};;;")
            
            # Email
            email = str(row.get('Email', '')).strip() if pd.notna(row.get('Email', '')) else ''
            if email and email.lower() != 'nan':
                vcf_content.append(f"EMAIL;TYPE=INTERNET:{email}")
            
            # Telefon
            phone = str(row.get('Telefon', '')).strip() if pd.notna(row.get('Telefon', '')) else ''
            if phone and phone.lower() != 'nan':
                # Telefon numarasını temizle
                phone = phone.replace(' ', '').replace('-', '').replace('(', '').replace(')', '')
                vcf_content.append(f"TEL;TYPE=CELL:{phone}")
            
            # Etiket (Not olarak ekle)
            label = str(row.get('Etiket', '')).strip() if pd.notna(row.get('Etiket', '')) else ''
            if label and label.lower() != 'nan':
                vcf_content.append(f"NOTE:{label}")
            
            # Oluşturulma tarihi
            vcf_content.append(f"REV:{datetime.now().strftime('%Y%m%dT%H%M%SZ')}")
            
            # vCard bitir
            vcf_content.append("END:VCARD")
            vcf_content.append("")  # Boş satır ekle
        
        # VCF dosyasını yaz
        with open(vcf_file, 'w', encoding='utf-8') as f:
            f.write('\n'.join(vcf_content))
        
        print(f"✅ VCF dosyası başarıyla oluşturuldu: {vcf_file}")
        print(f"📊 Toplam {len(df)} kayıt işlendi")
        
        return True
        
    except FileNotFoundError:
        print(f"❌ Hata: '{excel_file}' dosyası bulunamadı!")
        return False
    except Exception as e:
        print(f"❌ Hata oluştu: {str(e)}")
        return False

def main():
    """Ana fonksiyon - kullanım örneği"""
    
    # Excel dosyasının adı
    excel_dosyasi = "liste.xlsx"
    
    # Dosyanın varlığını kontrol et
    if not os.path.exists(excel_dosyasi):
        print(f"❌ '{excel_dosyasi}' dosyası bulunamadı!")
        print("Lütfen Excel dosyasının bu Python dosyasıyla aynı klasörde olduğundan emin olun.")
        return
    
    # Dönüştürme işlemini başlat
    print("🔄 Excel dosyası VCF formatına dönüştürülüyor...")
    
    success = excel_to_vcf(excel_dosyasi, "kişiler.vcf")
    
    if success:
        print("\n✨ İşlem tamamlandı!")
        print("📱 'kişiler.vcf' dosyasını telefonunuza aktararak kişilerinizi içe aktarabilirsiniz.")
    else:
        print("\n❌ İşlem başarısız oldu!")

if __name__ == "__main__":
    main()
