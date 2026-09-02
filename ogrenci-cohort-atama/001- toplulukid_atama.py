# -*- coding: utf-8 -*-
"""
Öğrencilerin sınav puanlarına göre ToplulukID atamasını yapan script.

Mantık:
  1) Her öğrenci için önce "2. Adım" (yerleştirme) sınavlarına bakılır.
     Bu sınavlardan (Filiz/Fidan/Çınar - Başlangıç/Temel/Orta/İleri) hangisinde
     puan varsa, NİHAİ seviye o sınavın kuralına göre belirlenir.
  2) Eğer öğrencinin hiçbir 2. Adım sınavında puanı yoksa, "1. Adım" (ana/genel)
     sınavına bakılır (Okul Öncesi / Filiz / Fidan / Çınar genel anketi) ve
     nihai seviye o sınavın yönlendirme kuralına göre belirlenir.
  3) Grup (Tohum/Filiz/Fidan/Çınar) + Seviye (Başlangıç/Temel/Orta/İleri) ikilisi,
     IDler.txt içindeki "İsim" alanına ( "{Grup}-{Seviye}" ) eşlenerek ToplulukID bulunur.

NOT (önemli varsayım): kurallar.txt'de Tohum grubu seviyeleri "Farkındalık" ve
"Hazırlık" olarak tanımlı, ancak IDler.txt'de bu isimlerle eşleşen bir ID yok;
sadece "Tohum-Başlangıç" (tohum1) ve "Tohum-Temel" (tohum2) var. Bu scriptte
Farkındalık -> Başlangıç, Hazırlık -> Temel şeklinde eşlendi (TOHUM_LEVEL_MAP).
Bu varsayım yanlışsa aşağıdaki sözlüğü güncelleyin.
"""
import pandas as pd

# =========================================================
# 1. DOSYALARI OKU
# =========================================================

notlar = pd.read_excel("SBF Notlar.xlsx")
kullanicilar = pd.read_excel("Kullanıcılar.xlsx")


# =========================================================
# 2. SÜTUN İSİMLERİNİ KONTROL ET / BOŞLUKLARI TEMİZLE
# =========================================================

notlar.columns = notlar.columns.str.strip()
kullanicilar.columns = kullanicilar.columns.str.strip()

print("SBF Notlar sütunları:")
print(notlar.columns.tolist())

print("\nKullanıcılar sütunları:")
print(kullanicilar.columns.tolist())


# =========================================================
# 3. ID'LERİ GÜVENLİ BİR ŞEKİLDE METNE ÇEVİR
# =========================================================

def temizle_id(x):
    if pd.isna(x):
        return None

    # Önce string yap
    x = str(x).strip()

    # 12345.0 -> 12345
    if x.endswith(".0"):
        x = x[:-2]

    # Virgüllü değer varsa
    if x.endswith(",0"):
        x = x[:-2]

    return x


notlar["ID_eslesme"] = notlar["ID numarası"].apply(temizle_id)
kullanicilar["ID_eslesme"] = kullanicilar["id"].apply(temizle_id)


# =========================================================
# 4. SADECE ID VE USERNAME AL
# =========================================================

kullanici_esleme = kullanicilar[["ID_eslesme", "username"]].copy()

# Aynı ID birden fazla varsa ilkini kullan
kullanici_esleme = kullanici_esleme.drop_duplicates(
    subset="ID_eslesme",
    keep="first"
)


# =========================================================
# 5. EŞLEŞTİR
# =========================================================

notlar = notlar.merge(
    kullanici_esleme,
    on="ID_eslesme",
    how="left"
)


# =========================================================
# 6. username SÜTUNUNU EN BAŞA AL
# =========================================================

username = notlar.pop("username")
notlar.insert(0, "username", username)

# Geçici ID sütununu sil
notlar.drop(columns=["ID_eslesme"], inplace=True)


# =========================================================
# 7. SONUCU KAYDET
# =========================================================

notlar.to_excel(
    "SBF Notlar.xlsx",
    index=False
)


# =========================================================
# 8. KONTROL RAPORU
# =========================================================

toplam = len(notlar)
eslesen = notlar["username"].notna().sum()
eslesmeyen = notlar["username"].isna().sum()

print("\n====================================")
print("İŞLEM TAMAMLANDI")
print("====================================")
print(f"Toplam kayıt       : {toplam}")
print(f"Eşleşen kayıt      : {eslesen}")
print(f"Eşleşmeyen kayıt   : {eslesmeyen}")
print("Dosya              : SBF Notlar_username_eklendi.xlsx")
print("====================================")


# Eşleşmeyen ilk 20 ID'yi göster
if eslesmeyen > 0:
    print("\nEşleşmeyen ilk 20 ID:")
    print(
        notlar.loc[
            notlar["username"].isna(),
            "ID numarası"
        ].head(20).to_string(index=False)
    )

# -*- coding: utf-8 -*-
"""
Öğrencilerin sınav puanlarına göre ToplulukID atamasını yapan script.
"""

import re
import numpy as np
import pandas as pd

# --------------------------------------------------------------------------
# 0) EXCEL VERİ TEMİZLEME VE HAZIRLIK
# --------------------------------------------------------------------------
notlar = pd.read_excel("SBF Notlar.xlsx")

# Hücrelerdeki sayısal format uyumsuzluklarını gider (',' -> '.')
notlar = notlar.replace(",", ".", regex=True)

# Sınava girmeyen / '-' olan alanları NaN yap
notlar = notlar.replace("-", np.nan)

# Temizlenmiş hali kaydet
notlar.to_excel("SBF Notlar.xlsx", index=False)
print("SBF.xlsx veri temizleme adımı tamamlandı.")


# --------------------------------------------------------------------------
# 1) ESNEK SÜTUN EŞLEŞTİRME VE NORMALİZASYON
# --------------------------------------------------------------------------
def normalize(s):
    """Türkçe karakterleri koruyarak harf dışındaki karakterleri temizler."""
    if s is None:
        return ""
    s = str(s).replace("İ", "i").replace("I", "ı").lower()
    s = re.sub(r"[^a-zçğıöşü]", "", s)
    return s


def build_column_norm_map(columns):
    return {col: normalize(col) for col in columns}


def find_step1_column(columns_norm, grup):
    """1. Adım (genel anket) sütununu bulur."""
    for col, norm in columns_norm.items():
        if grup == "Tohum":
            if "okul" in norm and "öncesi" in norm:
                return col
        else:
            grup_key = normalize(grup)
            if grup_key in norm and "grubu" in norm and "anketi" in norm:
                return col
    return None


def find_step2_column(columns_norm, grup, seviye):
    """2. Adım (yerleştirme) sınav sütununu bulur."""
    grup_key = normalize(grup)
    seviye_key = normalize(seviye)
    for col, norm in columns_norm.items():
        if (
            grup_key in norm
            and seviye_key in norm
            and "grubu" not in norm
            and "anketi" not in norm
        ):
            return col
    return None


def find_id_column(columns, *keywords):
    """Kullanıcı/Öğrenci sütunlarını esnek biçimde arar."""
    for col in columns:
        norm = normalize(col)
        if all(normalize(k) in norm for k in keywords):
            return col
    return None


# --------------------------------------------------------------------------
# 2) KURAL VE SEVİYE TANIMLARI
# --------------------------------------------------------------------------
STEP1_GRUPLAR = ["Tohum", "Filiz", "Fidan", "Çınar"]

STEP1_RULES = {
    "Tohum": [
        (0, 50, "Farkındalık"),
        (51, float("inf"), "Hazırlık"),
    ],
    "Filiz": [
        (0, 14, "Başlangıç"),
        (15, 29, "Temel"),
        (30, 45, "Orta"),
    ],
    "Fidan": [
        (0, 14, "Başlangıç"),
        (15, 29, "Temel"),
        (30, 45, "Orta"),
    ],
    "Çınar": [
        (0, 14, "Başlangıç"),
        (15, 29, "Temel"),
        (30, 44, "Orta"),
        (45, 60, "İleri"),
    ],
}

STEP2_KEYS = [
    ("Filiz", "Başlangıç"),
    ("Filiz", "Temel"),
    ("Filiz", "Orta"),
    ("Fidan", "Başlangıç"),
    ("Fidan", "Temel"),
    ("Fidan", "Orta"),
    ("Çınar", "Başlangıç"),
    ("Çınar", "Temel"),
    ("Çınar", "Orta"),
    ("Çınar", "İleri"),
]

STEP2_RULES = {
    ("Filiz", "Başlangıç"): [(0, 36, "Başlangıç"), (37, 66, "Temel")],
    ("Filiz", "Temel"): [(0, 41, "Temel"), (42, 69, "Orta")],
    ("Filiz", "Orta"): [(0, 36, "Temel"), (37, 60, "Orta")],
    ("Fidan", "Başlangıç"): [(0, 36, "Başlangıç"), (37, 66, "Temel")],
    ("Fidan", "Temel"): [(0, 41, "Temel"), (42, 69, "Orta")],
    ("Fidan", "Orta"): [(0, 36, "Temel"), (37, 60, "Orta")],
    ("Çınar", "Başlangıç"): [(0, 36, "Başlangıç"), (37, 66, "Temel")],
    ("Çınar", "Temel"): [(0, 41, "Temel"), (42, 69, "Orta")],
    ("Çınar", "Orta"): [(0, 36, "Orta"), (37, 60, "İleri")],
    ("Çınar", "İleri"): [(0, 32, "Orta"), (33, 54, "İleri")],
}

TOHUM_LEVEL_MAP = {
    "Farkındalık": "Başlangıç",
    "Hazırlık": "Temel",
}

STEP2_CHECK_ORDER = STEP2_KEYS


def _seviye_bul(puan, aralik_listesi):
    try:
        puan = float(puan)
    except (ValueError, TypeError):
        return None, f"Geçersiz puan formatı: {puan}"

    for alt, ust, seviye in aralik_listesi:
        if alt <= puan <= ust:
            return seviye, None

    min_alt = aralik_listesi[0][0]
    if puan < min_alt:
        return (
            aralik_listesi[0][2],
            f"Puan ({puan}) alt sınırın altında, en düşük seviyeye sabitlendi.",
        )
    else:
        return (
            aralik_listesi[-1][2],
            f"Puan ({puan}) üst sınırın üstünde, en yüksek seviyeye sabitlendi.",
        )


def load_topluluk_id_map(idler_path):
    df = pd.read_csv(idler_path, sep="\t", dtype=str)
    id_map = {}
    for _, row in df.iterrows():
        grup = row["Yaş"].strip()
        seviye = row["Dil"].strip()
        id_map[(grup, seviye)] = row["ToplulukID"].strip()
    return id_map


def ogrenci_seviye_belirle(row, step1_col_map, step2_col_map):
    # 1) 2. Adım (Yerleştirme) Sınav Kontrolü
    for grup, sinav_seviyesi in STEP2_CHECK_ORDER:
        col = step2_col_map.get((grup, sinav_seviyesi))
        if col is not None and col in row.index and pd.notna(row[col]):
            puan = row[col]
            seviye, uyari = _seviye_bul(
                puan, STEP2_RULES[(grup, sinav_seviyesi)]
            )
            return grup, seviye, col, puan, uyari

    # 2) 1. Adım (Genel Anket) Kontrolü
    for grup in STEP1_GRUPLAR:
        col = step1_col_map.get(grup)
        if col is not None and col in row.index and pd.notna(row[col]):
            puan = row[col]
            seviye, uyari = _seviye_bul(puan, STEP1_RULES[grup])
            if grup == "Tohum":
                seviye = TOHUM_LEVEL_MAP.get(seviye, seviye)
            return grup, seviye, col, puan, uyari

    return None, None, None, None, "Hiçbir sınav puanı bulunamadı"


def build_column_maps(columns):
    columns_norm = build_column_norm_map(columns)
    step1_col_map = {
        grup: find_step1_column(columns_norm, grup) for grup in STEP1_GRUPLAR
    }
    step2_col_map = {
        key: find_step2_column(columns_norm, key[0], key[1])
        for key in STEP2_KEYS
    }

    rapor = []
    for grup, col in step1_col_map.items():
        rapor.append((f"1.Adım - {grup}", col))
    for (grup, seviye), col in step2_col_map.items():
        rapor.append((f"2.Adım - {grup} {seviye}", col))

    eksikler = [ad for ad, col in rapor if col is None]
    return step1_col_map, step2_col_map, rapor, eksikler


# --------------------------------------------------------------------------
# 3) ANA ÇALIŞTIRMA FONKSİYONU
# --------------------------------------------------------------------------
def main(
    notlar_path="SBF Notlar.xlsx",
    idler_path="IDler.txt",
    output_path="topluluk_atamalari.xlsx",
):
    df = pd.read_excel(notlar_path)
    id_map = load_topluluk_id_map(idler_path)

    step1_col_map, step2_col_map, rapor, eksikler = build_column_maps(
        df.columns
    )

    print("=== Sütun Eşleştirme Raporu ===")
    for ad, col in rapor:
        print(f"  {ad:25s} -> {col!r}")
    if eksikler:
        print(
            "\n!! UYARI: Aşağıdaki sınav sütunları bulunamadı (işleme alınmayacak):"
        )
        for e in eksikler:
            print(f"   - {e}")
    print()

    # Kullanıcı ve kimlik sütunlarını dinamik yakalama
    kullanici_col = (
        find_id_column(df.columns, "username")
        or find_id_column(df.columns, "kullanıcı")
        or "username"
    )
    eposta_col = find_id_column(df.columns, "posta") or "E-posta adresi"

    # Ayrılmış ad ve soyad sütun kontrolü
    ad_col = find_id_column(df.columns, "öğrencinin", "adı") or find_id_column(
        df.columns, "ad"
    )
    soyad_col = find_id_column(
        df.columns, "öğrencinin", "soyadı"
    ) or find_id_column(df.columns, "soyad")
    tekil_ad_col = find_id_column(df.columns, "öğrencinin", "adı", "soyadı")

    sonuclar = []
    for _, row in df.iterrows():
        # İsim / Soyisim birleştirme
        if ad_col and soyad_col and ad_col != soyad_col:
            ad_val = str(row.get(ad_col, "")).strip()
            soyad_val = str(row.get(soyad_col, "")).strip()
            tam_ad = (
                f"{ad_val} {soyad_val}".strip()
                if (ad_val or soyad_val)
                else None
            )
        elif tekil_ad_col:
            tam_ad = row.get(tekil_ad_col)
        else:
            tam_ad = row.get("Öğrencinin adı / Öğrencinin soyadı")

        grup, seviye, kullanilan_sinav, puan, uyari = ogrenci_seviye_belirle(
            row, step1_col_map, step2_col_map
        )

        if grup is None:
            topluluk_id = None
        else:
            topluluk_id = id_map.get((grup, seviye))
            if topluluk_id is None:
                uyari = (
                    (uyari + " | " if uyari else "")
                    + f"IDler.txt içinde '{grup}-{seviye}' eşleşmesi bulunamadı!"
                )

        sonuclar.append(
            {
                "Öğrencinin adı / Öğrencinin soyadı": tam_ad,
                "Kullanıcı adı": row.get(kullanici_col),
                "E-posta adresi": row.get(eposta_col),
                "Grup": grup,
                "Seviye": seviye,
                "ToplulukID": topluluk_id,
                "Kullanılan Sınav": kullanilan_sinav,
                "Puan": puan,
                "Uyarı": uyari,
            }
        )

    sonuc_df = pd.DataFrame(sonuclar)
    sonuc_df.to_excel(output_path, index=False)

    print(f"Tamamlandı. {len(sonuc_df)} öğrenci işlendi -> {output_path}")
    print(f"  ToplulukID atanan: {sonuc_df['ToplulukID'].notna().sum()}")
    print(f"  Atanamayan: {sonuc_df['ToplulukID'].isna().sum()}")
    return sonuc_df


if __name__ == "__main__":
    main()


import pandas as pd

# ==========================================
# DOSYA ADLARI
# ==========================================

dosya1 = "topluluk_atamalari.xlsx"
dosya2 = "ogretmen_tasnifleri.xlsx"

cikti = "topluluk_atamalari_guncel.xlsx"


# ==========================================
# EXCEL DOSYALARINI OKU
# ==========================================

df1 = pd.read_excel(dosya1)
df2 = pd.read_excel(dosya2)


# ==========================================
# SÜTUN İSİMLERİNİ TEMİZLE
# ==========================================

df1.columns = df1.columns.astype(str).str.strip()
df2.columns = df2.columns.astype(str).str.strip()


# ==========================================
# KULLANICI ADI KONTROLÜ
# ==========================================

if "Kullanıcı adı" not in df1.columns:
    raise ValueError(
        f"'{dosya1}' dosyasında 'Kullanıcı adı' sütunu bulunamadı."
    )

if "Kullanıcı adı" not in df2.columns:
    raise ValueError(
        f"'{dosya2}' dosyasında 'Kullanıcı adı' sütunu bulunamadı."
    )


# ==========================================
# KULLANICI ADLARINI TEMİZLE
# ==========================================

df1["Kullanıcı adı"] = (
    df1["Kullanıcı adı"]
    .fillna("")
    .astype(str)
    .str.strip()
)

df2["Kullanıcı adı"] = (
    df2["Kullanıcı adı"]
    .fillna("")
    .astype(str)
    .str.strip()
)


# ==========================================
# İLK DOSYADA OLMAYAN KULLANICILARI BUL
# ==========================================

eksik_kullanicilar = df2[
    ~df2["Kullanıcı adı"].isin(df1["Kullanıcı adı"])
].copy()


# Boş kullanıcı adı olan kayıtları ekleme
eksik_kullanicilar = eksik_kullanicilar[
    eksik_kullanicilar["Kullanıcı adı"] != ""
]


# ==========================================
# İSTENEN SÜTUNLAR
# ==========================================

sutunlar = [
    "Öğrencinin adı / Öğrencinin soyadı",
    "Kullanıcı adı",
    "Grup",
    "Seviye",
    "ToplulukID"
]


# ==========================================
# İLK DOSYADA OLMAYAN SÜTUNLARI OLUŞTUR
# ==========================================

for sutun in sutunlar:
    if sutun not in df1.columns:
        df1[sutun] = pd.NA


# ==========================================
# İKİNCİ DOSYADA OLMAYAN SÜTUNLARI
# OTOMATİK OLARAK BOŞ OLUŞTUR
# ==========================================

eksik_kullanicilar = eksik_kullanicilar.reindex(
    columns=df1.columns
)


# ==========================================
# İKİ DOSYADAN GELEN VERİLERİ BİRLEŞTİR
# ==========================================

guncel_df = pd.concat(
    [df1, eksik_kullanicilar],
    ignore_index=True
)


# ==========================================
# EXCEL OLARAK KAYDET
# ==========================================

guncel_df.to_excel(
    cikti,
    index=False
)


# ==========================================
# SONUÇ
# ==========================================

print("==========================================")
print("İŞLEM TAMAMLANDI")
print("==========================================")
print(f"İlk dosyadaki kayıt sayısı      : {len(df1)}")
print(f"Eklenen yeni kullanıcı sayısı   : {len(eksik_kullanicilar)}")
print(f"Yeni toplam kayıt sayısı        : {len(guncel_df)}")
print(f"Oluşturulan dosya               : {cikti}")
print("==========================================")


import pandas as pd

# ==========================================
# DOSYA ADLARI
# ==========================================

dosya_kullanicilar = "Kullanıcılar.xlsx"
dosya_topluluk = "topluluk_atamalari_guncel.xlsx"

cikti = "topluluk_atamalari_ulke_eklenmis.xlsx"


# ==========================================
# EXCEL DOSYALARINI OKU
# ==========================================

kullanicilar = pd.read_excel(dosya_kullanicilar)
topluluk = pd.read_excel(dosya_topluluk)


# ==========================================
# SÜTUN İSİMLERİNİ TEMİZLE
# ==========================================

kullanicilar.columns = (
    kullanicilar.columns.astype(str).str.strip()
)

topluluk.columns = (
    topluluk.columns.astype(str).str.strip()
)


# ==========================================
# GEREKLİ SÜTUNLARI KONTROL ET
# ==========================================

gerekli_kullanici_sutunlari = [
    "username",
    "profile_field_ulke"
]

for sutun in gerekli_kullanici_sutunlari:
    if sutun not in kullanicilar.columns:
        raise ValueError(
            f"Kullanıcılar.xlsx dosyasında '{sutun}' sütunu bulunamadı."
        )


if "Kullanıcı adı" not in topluluk.columns:
    raise ValueError(
        "topluluk_atamalari_guncel.xlsx dosyasında "
        "'Kullanıcı adı' sütunu bulunamadı."
    )


# ==========================================
# KULLANICI ADLARINI TEMİZLE
# ==========================================

kullanicilar["username"] = (
    kullanicilar["username"]
    .fillna("")
    .astype(str)
    .str.strip()
)

topluluk["Kullanıcı adı"] = (
    topluluk["Kullanıcı adı"]
    .fillna("")
    .astype(str)
    .str.strip()
)


# ==========================================
# SADECE GEREKLİ BİLGİLERİ AL
# ==========================================

ulke_bilgileri = kullanicilar[
    ["username", "profile_field_ulke"]
].copy()


# ==========================================
# AYNI USERNAME'DEN BİRDEN FAZLA VARSA
# İLK KAYDI KULLAN
# ==========================================

ulke_bilgileri = ulke_bilgileri.drop_duplicates(
    subset="username",
    keep="first"
)


# ==========================================
# PROFILE_FIELD_ULKE BİLGİSİNİ EŞLEŞTİR
# ==========================================

topluluk = topluluk.merge(
    ulke_bilgileri,
    how="left",
    left_on="Kullanıcı adı",
    right_on="username"
)


# ==========================================
# username SÜTUNUNU SİL
# ==========================================

topluluk.drop(
    columns=["username"],
    inplace=True
)


# ==========================================
# SONUCU EXCEL OLARAK KAYDET
# ==========================================

topluluk.to_excel(
    cikti,
    index=False
)


# ==========================================
# SONUÇ BİLGİLERİ
# ==========================================

eslesen = topluluk["profile_field_ulke"].notna().sum()

print("==========================================")
print("İŞLEM TAMAMLANDI")
print("==========================================")
print(f"Toplam kayıt          : {len(topluluk)}")
print(f"Eşleşen kullanıcı     : {eslesen}")
print(f"Eşleşmeyen kullanıcı  : {len(topluluk) - eslesen}")
print(f"Oluşturulan dosya     : {cikti}")
print("==========================================")


import pandas as pd
import matplotlib.pyplot as plt

# ============================================================
# DOSYA
# ============================================================

dosya = "topluluk_atamalari_ulke_eklenmis.xlsx"

df = pd.read_excel(dosya)


# ============================================================
# RESMİ ÜLKE LİSTESİ
# ============================================================

resmi_ulkeler = [
    "Amerika Birleşik Devletleri",
    "Bulgaristan",
    "Hollanda",
    "Romanya",
    "Danimarka",
    "Finlandiya",
    "Norveç",
    "İsveç",
    "İtalya",
    "İrlanda",
    "Karadağ",
    "Senegal",
    "İspanya",
    "Çin",
    "Kanada",
    "Bosna Hersek"
]


# ============================================================
# GEREKLİ SÜTUNLARI KONTROL ET
# ============================================================

gerekli_sutunlar = [
    "ToplulukID",
    "profile_field_ulke"
]

for sutun in gerekli_sutunlar:
    if sutun not in df.columns:
        raise ValueError(
            f"'{sutun}' sütunu Excel dosyasında bulunamadı."
        )


# ============================================================
# VERİLERİ TEMİZLE
# ============================================================

df = df.dropna(
    subset=["ToplulukID", "profile_field_ulke"]
).copy()

df["profile_field_ulke"] = (
    df["profile_field_ulke"]
    .astype(str)
    .str.strip()
)


# ============================================================
# ÜLKELERİ 3 KATEGORİYE AYIR
# ============================================================

def kategori_belirle(ulke):

    if ulke == "Amerika Birleşik Devletleri":
        return "ABD"

    elif ulke == "Çin":
        return "Çin"

    elif ulke in resmi_ulkeler:
        return "Avrupa"

    else:
        # Resmi listede olmayan ülkeler de Diğer
        return "Avrupa"


df["Ülke Kategorisi"] = (
    df["profile_field_ulke"]
    .apply(kategori_belirle)
)


# ============================================================
# TOPLULUK + KATEGORİ BAZINDA ÖĞRENCİ SAYISI
# ============================================================

sayilar = (
    df.groupby(
        ["ToplulukID", "Ülke Kategorisi"]
    )
    .size()
    .reset_index(name="Öğrenci Sayısı")
)


# ============================================================
# YÜZDELERİ HESAPLA
# ============================================================

sayilar["Yüzde"] = (
    sayilar["Öğrenci Sayısı"]
    /
    sayilar.groupby("ToplulukID")["Öğrenci Sayısı"]
    .transform("sum")
    * 100
)

sayilar["Yüzde"] = sayilar["Yüzde"].round(1)


# ============================================================
# KATEGORİ SIRASINI BELİRLE
# ============================================================

kategori_sirasi = [
    "ABD",
    "Çin",
    "Avrupa"
]

sayilar["Ülke Kategorisi"] = pd.Categorical(
    sayilar["Ülke Kategorisi"],
    categories=kategori_sirasi,
    ordered=True
)

sayilar = sayilar.sort_values(
    ["ToplulukID", "Ülke Kategorisi"]
)


# ============================================================
# SAYISAL SONUÇLARI EKRANA YAZDIR
# ============================================================

print("\n")
print("=" * 70)
print("TOPLULUKLARA GÖRE ABD / ÇİN / DİĞER DAĞILIMI")
print("=" * 70)

for topluluk in sayilar["ToplulukID"].unique():

    print(f"\n--- {topluluk} ---")

    veri = sayilar[
        sayilar["ToplulukID"] == topluluk
    ]

    toplam = veri["Öğrenci Sayısı"].sum()

    for _, satir in veri.iterrows():

        print(
            f"{satir['Ülke Kategorisi']:>6} : "
            f"{satir['Öğrenci Sayısı']:>4} öğrenci "
            f"(%{satir['Yüzde']})"
        )

    print(f"Toplam : {toplam} öğrenci")


# ============================================================
# HER TOPLULUK İÇİN GRAFİK
# ============================================================

for topluluk in sayilar["ToplulukID"].unique():

    veri = sayilar[
        sayilar["ToplulukID"] == topluluk
    ].copy()

    # Eksik kategorileri de göster
    veri = (
        veri.set_index("Ülke Kategorisi")
        .reindex(kategori_sirasi)
        .fillna(0)
        .reset_index()
    )

    plt.figure(figsize=(9, 6))

    bars = plt.bar(
        veri["Ülke Kategorisi"],
        veri["Öğrenci Sayısı"]
    )

    # ========================================================
    # ÇUBUKLARIN ÜZERİNE SAYI + YÜZDE YAZ
    # ========================================================

    toplam = veri["Öğrenci Sayısı"].sum()

    for bar, sayi in zip(
        bars,
        veri["Öğrenci Sayısı"]
    ):

        if toplam > 0:
            yuzde = (sayi / toplam) * 100
        else:
            yuzde = 0

        plt.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height(),
            f"{int(sayi)} öğrenci\n(%{yuzde:.1f})",
            ha="center",
            va="bottom",
            fontsize=11
        )

    plt.title(
        f"{topluluk} - Öğrencilerin Ülkelere Göre Dağılımı",
        fontsize=15
    )

    plt.xlabel("Ülke Kategorisi")
    plt.ylabel("Öğrenci Sayısı")

    plt.tight_layout()

    plt.show()


# ============================================================
# İSTATİSTİKLERİ EXCEL'E KAYDET
# ============================================================

sayilar.to_excel(
    "abd_cin_diger_istatistik.xlsx",
    index=False
)


print("\n")
print("=" * 70)
print("İŞLEM TAMAMLANDI")
print("=" * 70)
print("İstatistik dosyası:")
print("abd_cin_diger_istatistik.xlsx")


import pandas as pd

# Excel dosyanızın adı
input_file = "topluluk_atamalari_guncel.xlsx"

# Excel'i oku
df = pd.read_excel(input_file)

# Gerekli sütunları seç
cohort_df = df[["Kullanıcı adı", "ToplulukID"]].copy()

# Sütun adlarını değiştir
cohort_df.columns = ["username", "cohort1"]

# Boş veya NaN ToplulukID'leri kaldır
cohort_df["cohort1"] = cohort_df["cohort1"].fillna("").astype(str).str.strip()
cohort_df = cohort_df[cohort_df["cohort1"] != ""]

# Kullanıcı adındaki boşlukları temizle
cohort_df["username"] = cohort_df["username"].astype(str).str.strip()

# CSV olarak kaydet
cohort_df.to_csv("cohort.csv", index=False, encoding="utf-8")

print(f"{len(cohort_df)} kayıt cohort.csv dosyasına yazıldı.")