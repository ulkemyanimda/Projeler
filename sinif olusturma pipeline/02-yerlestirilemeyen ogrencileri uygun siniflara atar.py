import os
import pandas as pd
from pathlib import Path
import re
from datetime import datetime

class SinifBirlestirici:
    def __init__(self, klasor_yolu='./Siniflar'):
        self.klasor_yolu = klasor_yolu
        self.min_ogrenci = 5
        self.rapor = []
        
        # Birleşebilir gruplar
        self.yas_gruplari = [
            {'Sophomore', 'Freshman'},
            {'Junior', 'Senior'}
        ]
        self.seviye_gruplari = [
            {'Türkçeyi_hiç_bilmez', 'Türkçeyi_anlayabilir_fakat_konuşamaz'}
        ]
        
    def dosya_bilgilerini_ayikla(self, dosya_adi):
        """Excel dosya adından sınıf bilgilerini çıkartır"""
        try:
            # Dosya adını parçalara ayır
            parcalar = dosya_adi.replace('.xlsx', '').split('@')
            
            if len(parcalar) < 5:
                return None
                
            sinif_sayisi = int(parcalar[0])
            bolge = parcalar[1]
            yas = parcalar[2]
            zaman = parcalar[3]
            seviye = parcalar[4]
            
            return {
                'dosya_adi': dosya_adi,
                'sinif_sayisi': sinif_sayisi,
                'bolge': bolge,
                'yas': yas,
                'zaman': zaman,
                'seviye': seviye
            }
        except Exception as e:
            self.log(f"❌ Dosya adı ayrıştırılamadı: {dosya_adi} - Hata: {str(e)}")
            return None
    
    def excel_oku(self, dosya_yolu):
        """Excel dosyasını okur ve öğrenci sayısını döndürür"""
        try:
            df = pd.read_excel(dosya_yolu)
            return df, len(df)
        except Exception as e:
            self.log(f"❌ Excel okunamadı: {dosya_yolu} - Hata: {str(e)}")
            return None, 0
    
    def birlesebilir_mi(self, sinif1, sinif2):
        """İki sınıfın birleşip birleşemeyeceğini kontrol eder"""
        # Bölge ve zaman aynı olmalı
        if sinif1['bolge'] != sinif2['bolge']:
            return False
        if sinif1['zaman'] != sinif2['zaman']:
            return False
        
        # Yaş kontrolü
        yas_uyumlu = False
        if sinif1['yas'] == sinif2['yas']:
            yas_uyumlu = True
        else:
            for grup in self.yas_gruplari:
                if sinif1['yas'] in grup and sinif2['yas'] in grup:
                    yas_uyumlu = True
                    break
        
        if not yas_uyumlu:
            return False
        
        # Seviye kontrolü
        seviye_uyumlu = False
        if sinif1['seviye'] == sinif2['seviye']:
            seviye_uyumlu = True
        else:
            for grup in self.seviye_gruplari:
                if sinif1['seviye'] in grup and sinif2['seviye'] in grup:
                    seviye_uyumlu = True
                    break
        
        return seviye_uyumlu
    
    def yeni_dosya_adi_olustur(self, siniflar, toplam_ogrenci):
        """Birleştirilmiş sınıf için yeni dosya adı oluşturur"""
        # İlk sınıfın özelliklerini temel al
        ornek = siniflar[0]
        
        # Yaş grubu belirle
        yaslar = set(s['yas'] for s in siniflar)
        if len(yaslar) == 1:
            yas = list(yaslar)[0]
        else:
            # Birleşik yaş grubu
            if yaslar.issubset({'Sophomore', 'Freshman'}):
                yas = 'Freshman-Sophomore'
            elif yaslar.issubset({'Junior', 'Senior'}):
                yas = 'Junior-Senior'
            else:
                yas = '-'.join(sorted(yaslar))
        
        # Seviye grubu belirle
        seviyeler = set(s['seviye'] for s in siniflar)

        if len(seviyeler) == 1:
            seviye = list(seviyeler)[0]
        else:
            seviye = 'Karma_Seviye'

        
        # Yeni dosya adı
        yeni_ad = f"1@{ornek['bolge']}@{yas}@{ornek['zaman']}@{seviye}.xlsx"
        return yeni_ad
    
    def siniflari_birlestir(self, siniflar, dosya_yollari):
        """Birden fazla sınıfı tek bir Excel dosyasında birleştirir"""
        try:
            # Tüm dataframe'leri birleştir
            tum_dataframeler = []
            for yol in dosya_yollari:
                df, _ = self.excel_oku(yol)
                if df is not None:
                    tum_dataframeler.append(df)
            
            if not tum_dataframeler:
                return None
            
            # Birleştir
            birlesik_df = pd.concat(tum_dataframeler, ignore_index=True)
            
            # Yeni dosya adı oluştur
            yeni_ad = self.yeni_dosya_adi_olustur(siniflar, len(birlesik_df))
            yeni_yol = os.path.join(self.klasor_yolu, yeni_ad)
            
            # Kaydet
            birlesik_df.to_excel(yeni_yol, index=False)
            
            return yeni_yol, len(birlesik_df)
            
        except Exception as e:
            self.log(f"❌ Birleştirme hatası: {str(e)}")
            return None
    
    def log(self, mesaj):
        """Rapor mesajı ekler"""
        self.rapor.append(mesaj)
        print(mesaj)
    
    def calistir(self):
        """Ana işlem fonksiyonu"""
        self.log("=" * 80)
        self.log("🎓 SINIF BİRLEŞTİRME PROGRAMI BAŞLATILDI")
        self.log("=" * 80)
        self.log(f"📁 Klasör: {self.klasor_yolu}")
        self.log(f"👥 Minimum öğrenci sayısı: {self.min_ogrenci}")
        self.log("")
        
        # Excel dosyalarını bul
        excel_dosyalari = [f for f in os.listdir(self.klasor_yolu) if f.endswith('.xlsx')]
        self.log(f"📊 Toplam {len(excel_dosyalari)} Excel dosyası bulundu\n")
        
        # Sınıf bilgilerini topla
        sinif_bilgileri = []
        for dosya in excel_dosyalari:
            bilgi = self.dosya_bilgilerini_ayikla(dosya)
            if bilgi:
                dosya_yolu = os.path.join(self.klasor_yolu, dosya)
                df, ogrenci_sayisi = self.excel_oku(dosya_yolu)
                if df is not None:
                    bilgi['ogrenci_sayisi'] = ogrenci_sayisi
                    bilgi['dosya_yolu'] = dosya_yolu
                    sinif_bilgileri.append(bilgi)
        
        # Küçük sınıfları ayır
        kucuk_siniflar = [s for s in sinif_bilgileri if s['ogrenci_sayisi'] < self.min_ogrenci]
        buyuk_siniflar = [s for s in sinif_bilgileri if s['ogrenci_sayisi'] >= self.min_ogrenci]
        
        self.log(f"✅ Yeterli mevcutlu sınıf: {len(buyuk_siniflar)}")
        self.log(f"⚠️  Birleştirilmesi gereken sınıf: {len(kucuk_siniflar)}\n")
        
        if not kucuk_siniflar:
            self.log("🎉 Tüm sınıflar yeterli mevcuda sahip!")
            return
        
        # Küçük sınıfları listele
        self.log("📋 BİRLEŞTİRİLMESİ GEREKEN SINIFLAR:")
        self.log("-" * 80)
        for s in kucuk_siniflar:
            self.log(f"  • {s['dosya_adi']}")
            self.log(f"    👥 Öğrenci: {s['ogrenci_sayisi']} | 📍 {s['bolge']} | 🕐 {s['zaman']}")
            self.log(f"    🎂 {s['yas']} | 📚 {s['seviye']}\n")
        
        # Birleştirme işlemleri
        self.log("\n🔄 BİRLEŞTİRME İŞLEMLERİ BAŞLIYOR...")
        self.log("=" * 80)
        
        islenen = set()
        birlestirme_sayisi = 0
        
        for i, sinif1 in enumerate(kucuk_siniflar):
            if sinif1['dosya_adi'] in islenen:
                continue
            
            # Uyumlu sınıfları bul
            uyumlu_siniflar = [sinif1]
            uyumlu_yollar = [sinif1['dosya_yolu']]
            toplam_ogrenci = sinif1['ogrenci_sayisi']
            
            for sinif2 in kucuk_siniflar[i+1:]:
                if sinif2['dosya_adi'] in islenen:
                    continue
                
                if self.birlesebilir_mi(sinif1, sinif2):
                    uyumlu_siniflar.append(sinif2)
                    uyumlu_yollar.append(sinif2['dosya_yolu'])
                    toplam_ogrenci += sinif2['ogrenci_sayisi']
            
            # Birleştirme yap
            if len(uyumlu_siniflar) > 1:
                birlestirme_sayisi += 1
                self.log(f"\n🔀 BİRLEŞTİRME #{birlestirme_sayisi}")
                self.log("-" * 60)
                
                for s in uyumlu_siniflar:
                    self.log(f"  ➕ {s['dosya_adi']} ({s['ogrenci_sayisi']} öğrenci)")
                
                sonuc = self.siniflari_birlestir(uyumlu_siniflar, uyumlu_yollar)
                
                if sonuc:
                    yeni_yol, yeni_ogrenci = sonuc
                    yeni_dosya = os.path.basename(yeni_yol)
                    self.log(f"  ✅ Yeni sınıf: {yeni_dosya}")
                    self.log(f"  👥 Toplam öğrenci: {yeni_ogrenci}")
                    
                    # Eski dosyaları sil
                    for yol in uyumlu_yollar:
                        try:
                            os.remove(yol)
                            islenen.add(os.path.basename(yol))
                            self.log(f"  🗑️  Silindi: {os.path.basename(yol)}")
                        except Exception as e:
                            self.log(f"  ❌ Silinemedi: {os.path.basename(yol)} - {str(e)}")
            
            elif sinif1['dosya_adi'] not in islenen:
                self.log(f"\n⚠️  BİRLEŞTİRİLEMEDİ: {sinif1['dosya_adi']}")
                self.log(f"  👥 {sinif1['ogrenci_sayisi']} öğrenci - Uyumlu sınıf bulunamadı")
        
        # Özet rapor
        self.log("\n" + "=" * 80)
        self.log("📊 ÖZET RAPOR")
        self.log("=" * 80)
        self.log(f"✅ Toplam birleştirme sayısı: {birlestirme_sayisi}")
        self.log(f"📁 İşlenen dosya sayısı: {len(islenen)}")
        
        # Güncel durum
        yeni_dosyalar = [f for f in os.listdir(self.klasor_yolu) if f.endswith('.xlsx')]
        self.log(f"📊 Güncel toplam Excel dosyası: {len(yeni_dosyalar)}")
        
        # Raporu dosyaya kaydet
        rapor_dosyasi = f"birleştirme_raporu_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        with open(rapor_dosyasi, 'w', encoding='utf-8') as f:
            f.write('\n'.join(self.rapor))
        
        self.log(f"\n📄 Detaylı rapor kaydedildi: {rapor_dosyasi}")
        self.log("\n✨ İşlem tamamlandı!")

# Programı çalıştır
if __name__ == "__main__":
    birlestirici = SinifBirlestirici('./Siniflar')
    birlestirici.calistir()
