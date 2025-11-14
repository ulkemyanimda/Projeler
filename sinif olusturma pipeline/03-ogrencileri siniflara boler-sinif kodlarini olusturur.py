import os
import pandas as pd
from pathlib import Path
import shutil
from datetime import datetime
import math

class SinifBolme:
    def __init__(self, kaynak_klasor='./Siniflar', hedef_klasor='./YeniSiniflar', donem_kodu='25'):
        self.kaynak_klasor = kaynak_klasor
        self.hedef_klasor = hedef_klasor
        self.donem_kodu = donem_kodu
        
        # Hedef klasörü oluştur
        os.makedirs(hedef_klasor, exist_ok=True)
        
        # Standart sınıf büyüklüğü ve esneklik
        self.standart_buyukluk = 15
        self.esneklik = 2  # 15±2 = 13-17 arası kabul edilebilir
        self.min_sinif = 5
        
        # Kod sözlükleri
        self.yas_kodlari = {
            "Freshman": "01",
            "Sophomore": "02",
            "Junior": "03",
            "Senior": "04",
            "Freshman-Sophomore": "01",  # Birleşik sınıflar için
            "Junior-Senior": "03"
        }
        
        self.seviye_kodlari = {
            "Türkçeyi_hiç_bilmez": "01",
            "Türkçeyi_anlayabilir_fakat_konuşamaz": "02",
            "Türkçeyi_anlayabilir_konuşabilir_fakat_yazamaz": "03",
            "Türkçeyi_anlayabilir_konuşabilir_yazabilir": "04",
            "Karma_Seviye": "02"  # Birleşik seviyeler için varsayılan
        }
        
        self.plaka_kodlari = {
            "Amerika_Birleşik_Devletleri": "US",
            "Iskandinavya": "IX",
            "Bulgaristan": "BG",
            "Hollanda": "NL",
            "Çin": "CN",
            "İspanya": "ES",
            "İtalya": "IT",
            "Avrupa": "AV"
        }
        
        # Kullanılan kodları takip et
        self.kullanilan_kodlar = {}
        self.rapor = []
        
    def log(self, mesaj):
        """Rapor mesajı ekler"""
        self.rapor.append(mesaj)
        print(mesaj)
    
    def dosya_bilgilerini_ayikla(self, dosya_adi):
        """Excel dosya adından sınıf bilgilerini çıkartır"""
        try:
            parcalar = dosya_adi.replace('.xlsx', '').split('@')
            
            if len(parcalar) < 5:
                return None
                
            return {
                'dosya_adi': dosya_adi,
                'sinif_sayisi': int(parcalar[0]),
                'bolge': parcalar[1],
                'yas': parcalar[2],
                'zaman': parcalar[3],
                'seviye': parcalar[4]
            }
        except Exception as e:
            self.log(f"❌ Dosya adı ayrıştırılamadı: {dosya_adi} - {str(e)}")
            return None
    
    def optimal_bolme_hesapla(self, toplam_ogrenci):
        """
        Öğrencileri optimal şekilde bölmek için hesaplama yapar.
        Sınıflar mümkün olduğunca eşit ve min_sinif ile standart_buyukluk+esneklik arasında olmalı.
        """
        max_sinif = self.standart_buyukluk + self.esneklik
        
        # Eğer toplam öğrenci zaten uygun aralıktaysa bölme
        if self.min_sinif <= toplam_ogrenci <= max_sinif:
            return [toplam_ogrenci]
        
        # Kaç sınıfa bölüneceğini hesapla
        sinif_sayisi = math.ceil(toplam_ogrenci / self.standart_buyukluk)
        
        # Her sınıfa düşen ortalama öğrenci sayısı
        ortalama = toplam_ogrenci / sinif_sayisi
        
        # Eğer ortalama çok düşükse, sınıf sayısını azalt
        if ortalama < self.min_sinif:
            sinif_sayisi = math.floor(toplam_ogrenci / self.min_sinif)
            if sinif_sayisi == 0:
                sinif_sayisi = 1
            ortalama = toplam_ogrenci / sinif_sayisi
        
        # Öğrencileri dağıt
        bolumler = []
        kalan = toplam_ogrenci
        
        for i in range(sinif_sayisi):
            if i == sinif_sayisi - 1:
                # Son sınıfa kalanı ver
                bolumler.append(kalan)
            else:
                # Mümkün olduğunca eşit dağıt
                bu_sinif = round(ortalama)
                # Min ve max kontrolü
                bu_sinif = max(self.min_sinif, min(bu_sinif, max_sinif))
                bolumler.append(bu_sinif)
                kalan -= bu_sinif
        
        # Son kontrol: eğer son sınıf çok küçükse, önceki sınıflardan dağıt
        if bolumler[-1] < self.min_sinif and len(bolumler) > 1:
            eksik = self.min_sinif - bolumler[-1]
            bolumler[-1] = self.min_sinif
            # Eksik olanı diğer sınıflardan al
            for i in range(len(bolumler) - 1):
                if bolumler[i] > self.standart_buyukluk:
                    azalma = min(eksik, bolumler[i] - self.standart_buyukluk)
                    bolumler[i] -= azalma
                    eksik -= azalma
                    if eksik <= 0:
                        break
        
        return bolumler
    
    def yeni_kod_olustur(self, bolge, yas, seviye):
        """Benzersiz sınıf kodu oluşturur"""
        # Kod parçalarını al
        bolge_kod = self.plaka_kodlari.get(bolge, "XX")
        yas_kod = self.yas_kodlari.get(yas, "00")
        seviye_kod = self.seviye_kodlari.get(seviye, "00")
        
        # Ana kod (donem-bolge-yas-seviye)
        ana_kod = f"{self.donem_kodu}-{bolge_kod}-{yas_kod}-{seviye_kod}"
        
        # Bu ana kod için sıra numarası bul
        if ana_kod not in self.kullanilan_kodlar:
            self.kullanilan_kodlar[ana_kod] = 0
        else:
            self.kullanilan_kodlar[ana_kod] += 1
        
        sira = self.kullanilan_kodlar[ana_kod]
        
        # Tam kod
        tam_kod = f"{ana_kod}-{sira:02d}"
        
        return tam_kod
    
    def dataframe_bol(self, df, bolumler):
        """DataFrame'i belirtilen bölümlere ayırır"""
        parcalar = []
        baslangic = 0
        
        for bolum_boyutu in bolumler:
            bitis = baslangic + bolum_boyutu
            parca = df.iloc[baslangic:bitis].copy()
            parcalar.append(parca)
            baslangic = bitis
        
        return parcalar
    
    def sinif_isle(self, dosya_adi, bilgi):
        """Bir sınıfı işler: gerekirse böler, yeniden adlandırır ve kaydeder"""
        dosya_yolu = os.path.join(self.kaynak_klasor, dosya_adi)
        
        try:
            # Excel'i oku
            df = pd.read_excel(dosya_yolu)
            toplam_ogrenci = len(df)
            
            # ÖNEMLİ: Orijinal dosya ismini ekle (uzantısız)
            orijinal_dosya_ismi = dosya_adi.replace('.xlsx', '')
            df.insert(0, 'Orijinal_Dosya', orijinal_dosya_ismi)
            
            self.log(f"\n📚 İşleniyor: {dosya_adi}")
            self.log(f"   👥 Toplam öğrenci: {toplam_ogrenci}")
            self.log(f"   📍 Bölge: {bilgi['bolge']} | 🎂 Yaş: {bilgi['yas']} | 📚 Seviye: {bilgi['seviye']}")
            
            # Optimal bölme hesapla
            bolumler = self.optimal_bolme_hesapla(toplam_ogrenci)
            
            if len(bolumler) == 1:
                self.log(f"   ✅ Bölünmeyecek (Uygun büyüklükte)")
            else:
                self.log(f"   🔪 {len(bolumler)} sınıfa bölünecek: {bolumler}")
            
            # DataFrame'i böl
            df_parcalari = self.dataframe_bol(df, bolumler)
            
            # Her parçayı kaydet
            for i, parca in enumerate(df_parcalari):
                # Yeni kod oluştur
                yeni_kod = self.yeni_kod_olustur(bilgi['bolge'], bilgi['yas'], bilgi['seviye'])
                yeni_dosya_adi = f"{yeni_kod}.xlsx"
                yeni_dosya_yolu = os.path.join(self.hedef_klasor, yeni_dosya_adi)
                
                # Kaydet
                parca.to_excel(yeni_dosya_yolu, index=False)
                
                self.log(f"   ➡️  [{i+1}/{len(df_parcalari)}] {yeni_dosya_adi} ({len(parca)} öğrenci)")
            
            return len(bolumler)
            
        except Exception as e:
            self.log(f"   ❌ HATA: {str(e)}")
            return 0
    
    def calistir(self):
        """Ana işlem fonksiyonu"""
        self.log("=" * 100)
        self.log("🎓 SINIF BÖLME VE YENİDEN İSİMLENDİRME PROGRAMI")
        self.log("=" * 100)
        self.log(f"📁 Kaynak klasör: {self.kaynak_klasor}")
        self.log(f"📂 Hedef klasör: {self.hedef_klasor}")
        self.log(f"🔢 Dönem kodu: {self.donem_kodu}")
        self.log(f"👥 Standart sınıf büyüklüğü: {self.standart_buyukluk} (±{self.esneklik})")
        self.log(f"🔻 Minimum sınıf büyüklüğü: {self.min_sinif}")
        self.log(f"📝 Özellik: Orijinal dosya ismi her satıra ekleniyor")
        self.log("")
        
        # Excel dosyalarını bul
        excel_dosyalari = [f for f in os.listdir(self.kaynak_klasor) if f.endswith('.xlsx')]
        
        if not excel_dosyalari:
            self.log("❌ Hiç Excel dosyası bulunamadı!")
            return
        
        self.log(f"📊 Toplam {len(excel_dosyalari)} Excel dosyası bulundu")
        self.log("=" * 100)
        
        # İstatistikler
        toplam_islenen = 0
        toplam_olusturulan = 0
        toplam_ogrenci = 0
        
        # Her dosyayı işle
        for dosya in excel_dosyalari:
            bilgi = self.dosya_bilgilerini_ayikla(dosya)
            
            if bilgi:
                olusturulan_sinif = self.sinif_isle(dosya, bilgi)
                toplam_islenen += 1
                toplam_olusturulan += olusturulan_sinif
                
                # Öğrenci sayısını hesapla
                try:
                    df = pd.read_excel(os.path.join(self.kaynak_klasor, dosya))
                    toplam_ogrenci += len(df)
                except:
                    pass
        
        # Özet rapor
        self.log("\n" + "=" * 100)
        self.log("📊 ÖZET RAPOR")
        self.log("=" * 100)
        self.log(f"✅ İşlenen dosya sayısı: {toplam_islenen}")
        self.log(f"📝 Oluşturulan yeni sınıf sayısı: {toplam_olusturulan}")
        self.log(f"👥 Toplam öğrenci sayısı: {toplam_ogrenci}")
        self.log(f"📂 Yeni dosyalar: {self.hedef_klasor}")
        self.log(f"📋 Her öğrenci kaydında 'Orijinal_Dosya' sütunu eklendi")
        
        # Kullanılan kod örnekleri
        if self.kullanilan_kodlar:
            self.log("\n📋 KULLANILAN KOD ÖRNEKLERİ:")
            for ana_kod, sayi in sorted(self.kullanilan_kodlar.items()):
                self.log(f"   {ana_kod}-XX : {sayi + 1} sınıf")
        
        # Raporu dosyaya kaydet
        rapor_dosyasi = f"sinif_bolme_raporu_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        with open(rapor_dosyasi, 'w', encoding='utf-8') as f:
            f.write('\n'.join(self.rapor))
        
        self.log(f"\n📄 Detaylı rapor kaydedildi: {rapor_dosyasi}")
        self.log("\n✨ İşlem tamamlandı!")
        
        # Kod açıklaması
        self.log("\n" + "=" * 100)
        self.log("📖 KOD AÇIKLAMASI")
        self.log("=" * 100)
        self.log("Örnek: 25-AV-01-04-00")
        self.log("  25     : Dönem kodu")
        self.log("  AV     : Bölge (Avrupa)")
        self.log("  01     : Yaş grubu (Freshman)")
        self.log("  04     : Seviye (Türkçeyi anlayabilir konuşabilir yazabilir)")
        self.log("  00     : Sıra numarası (aynı özelliklerdeki sınıflar için)")
        self.log("=" * 100)

# Programı çalıştır
if __name__ == "__main__":
    # Dönem kodunu buradan değiştirebilirsiniz
    donem_kodu = input("Dönem kodunu girin (örn: 25): ").strip() or "25"
    
    print(f"\n🚀 Program başlatılıyor... Dönem: {donem_kodu}\n")
    
    bolme = SinifBolme(
        kaynak_klasor='./Siniflar',
        hedef_klasor='./YeniSiniflar',
        donem_kodu=donem_kodu
    )
    bolme.calistir()