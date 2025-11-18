#!/usr/bin/env python
# coding: utf-8

# In[17]:


import pandas as pd
import random
import string
from datetime import datetime, timedelta
df=pd.read_excel("adsoyad.xlsx")
# Veri listeleri
ad = ["Ahmet", "Mehmet", "Ali", "Ayşe", "Fatma", "Zeynep", "Mustafa", "Emine", "Hüseyin", "Hatice",
      "İbrahim", "Elif", "Yusuf", "Meryem", "Ömer", "Rabia", "Burak", "Esra", "Emre", "Selin",
      "Can", "Deniz", "Ece", "Kerem", "Merve", "Berkay", "Dilara", "Arda", "Yağmur", "Efe"]

soyad = ["Yılmaz", "Kaya", "Demir", "Şahin", "Çelik", "Yıldız", "Yıldırım", "Öztürk", "Aydın", "Özdemir",
         "Arslan", "Doğan", "Kılıç", "Aslan", "Çetin", "Kara", "Koç", "Kurt", "Özkan", "Şimşek",
         "Polat", "Erdoğan", "Özer", "Karaca", "Güneş", "Tekin", "Aktaş", "Bulut", "Ay", "Tunç"]

sehir = ["İstanbul", "Ankara", "İzmir", "Bursa", "Antalya", "Adana", "Konya", "Gaziantep", "Şanlıurfa", 
         "Kocaeli", "Mersin", "Diyarbakır", "Hatay", "Manisa", "Kayseri", "Samsun", "Balıkesir", 
         "Kahramanmaraş", "Van", "Aydın", "Denizli", "Sakarya", "Tekirdağ", "Muğla", "Eskişehir"]
ad=list(df["AD"].values)
soyad=list(df["SOYAD"].values)
sehir=list(df["CITY"].values)
schedule_options = {
    "Amerika Birleşik Devletleri": [
        "Cumartesi 09:00 - 10:30", "Pazar 09:00 - 10:30",
        "Cumartesi 12:00 - 13:30", "Pazar 12:00 - 13:30"
    ],
    "Bulgaristan": [
        "Cumartesi 10:00 - 11:30", "Pazar 10:00 - 11:30",
        "Cumartesi 17:00 - 18:30", "Pazar 17:00 - 18:30",
        "Salı 19:00 - 20:30", "Çarşamba 19:00 - 20:30", "Perşembe 19:00 - 20:30"
    ],
    "Çin": ["Cumartesi 17:00 - 18:30", "Pazar 17:00 - 18:30"],
    "Hollanda": [
        "Cumartesi 09:00 - 10:30", "Pazar 09:00 - 10:30",
        "Cumartesi 12:00 - 13:30", "Pazar 12:00 - 13:30",
        "Cumartesi 17:00 - 18:30", "Pazar 17:00 - 18:30",
        "Salı 18:00 - 19:30", "Çarşamba 18:00 - 19:30", "Perşembe 18:00 - 19:30"
    ],
    "İsveç": [
        "Cumartesi 09:00 - 10:30", "Pazar 09:00 - 10:30",
        "Cumartesi 12:00 - 13:30", "Pazar 12:00 - 13:30",
        "Cumartesi 17:00 - 18:30", "Pazar 17:00 - 18:30",
        "Salı 18:00 - 19:30", "Çarşamba 18:00 - 19:30", "Perşembe 18:00 - 19:30"
    ],
    "Finlandiya": [
        "Cumartesi 09:00 - 10:30", "Pazar 09:00 - 10:30",
        "Cumartesi 12:00 - 13:30", "Pazar 12:00 - 13:30",
        "Cumartesi 17:00 - 18:30", "Pazar 17:00 - 18:30",
        "Salı 18:00 - 19:30", "Çarşamba 18:00 - 19:30", "Perşembe 18:00 - 19:30"
    ],
    "Norveç": [
        "Cumartesi 09:00 - 10:30", "Pazar 09:00 - 10:30",
        "Cumartesi 12:00 - 13:30", "Pazar 12:00 - 13:30",
        "Cumartesi 17:00 - 18:30", "Pazar 17:00 - 18:30",
        "Salı 18:00 - 19:30", "Çarşamba 18:00 - 19:30", "Perşembe 18:00 - 19:30"
    ],
    "Danimarka": [
        "Cumartesi 09:00 - 10:30", "Pazar 09:00 - 10:30",
        "Cumartesi 12:00 - 13:30", "Pazar 12:00 - 13:30",
        "Cumartesi 17:00 - 18:30", "Pazar 17:00 - 18:30",
        "Salı 18:00 - 19:30", "Çarşamba 18:00 - 19:30", "Perşembe 18:00 - 19:30"
    ],
    "İtalya": [
        "Cumartesi 09:00 - 10:30", "Pazar 09:00 - 10:30",
        "Cumartesi 12:00 - 13:30", "Pazar 12:00 - 13:30",
        "Cumartesi 17:00 - 18:30", "Pazar 17:00 - 18:30",
        "Salı 18:00 - 19:30", "Çarşamba 18:00 - 19:30", "Perşembe 18:00 - 19:30"
    ],
    "İspanya": [
        "Cumartesi 09:00 - 10:30", "Pazar 09:00 - 10:30",
        "Cumartesi 12:00 - 13:30", "Pazar 12:00 - 13:30",
        "Cumartesi 17:00 - 18:30", "Pazar 17:00 - 18:30",
        "Salı 18:00 - 19:30", "Çarşamba 18:00 - 19:30", "Perşembe 18:00 - 19:30"
    ],
    "İzlanda": [
        "Cumartesi 09:00 - 10:30", "Pazar 09:00 - 10:30",
        "Cumartesi 12:00 - 13:30", "Pazar 12:00 - 13:30",
        "Cumartesi 17:00 - 18:30", "Pazar 17:00 - 18:30",
        "Salı 18:00 - 19:30", "Çarşamba 18:00 - 19:30", "Perşembe 18:00 - 19:30"
    ]
}

dil_seviyesi = [
    'Türkçeyi anlayabilir, konuşabilir fakat yazamaz',
    'Türkçeyi hiç bilmez',
    'Türkçeyi anlayabilir, konuşabilir, yazabilir',
    'Türkçeyi anlayabilir fakat konuşamaz'
]

# Türkçe ay isimleri
ay_isimleri = {
    1: "Ocak", 2: "Şubat", 3: "Mart", 4: "Nisan", 5: "Mayıs", 6: "Haziran",
    7: "Temmuz", 8: "Ağustos", 9: "Eylül", 10: "Ekim", 11: "Kasım", 12: "Aralık"
}

gun_isimleri = ["Pazartesi", "Salı", "Çarşamba", "Perşembe", "Cuma", "Cumartesi", "Pazar"]

def generate_username(existing_usernames):
    while True:
        length = random.randint(6, 10)
        username = ''.join(random.choices(string.ascii_lowercase + string.digits, k=length))
        if username not in existing_usernames:
            existing_usernames.add(username)
            return username

def generate_password():
    upper = random.choice(string.ascii_uppercase)
    lower = random.choice(string.ascii_lowercase)
    special = random.choice('!@#$%^&*')
    digits = ''.join(random.choices(string.digits, k=random.randint(5, 8)))
    password_chars = list(upper + lower + special + digits)
    random.shuffle(password_chars)
    return ''.join(password_chars)

def generate_email(number):
    domain = random.choice(['student', 'example'])
    return f"{domain}{number}@uy.gov.tr"

def generate_random_date():
    start_date = datetime(2010, 1, 1)
    end_date = datetime(2021, 12, 31)
    days_between = (end_date - start_date).days
    random_days = random.randint(0, days_between)
    random_date = start_date + timedelta(days=random_days)
    
    gun = gun_isimleri[random_date.weekday()]
    ay = ay_isimleri[random_date.month]
    saat = f"{random.randint(0, 23):02d}:{random.randint(0, 59):02d}"
    ampm = "AM" if random.randint(0, 1) == 0 else "PM"
    
    return f"{gun}, {random_date.day} {ay} {random_date.year}, {saat} {ampm}"

def generate_phone():
    return f"0{random.randint(500, 599)} {random.randint(100, 999)} {random.randint(10, 99)} {random.randint(10, 99)}"

def generate_student_data(num_students):
    data = []
    existing_usernames = set()
    
    for i in range(1, num_students + 1):
        # Ülke ve ders saati seçimi
        ulke = random.choice(list(schedule_options.keys()))
        ders_saati = random.choice(schedule_options[ulke])
        
        # Lastname bir kez seçilir ve hem öğrenci hem veli için kullanılır
        lastname = random.choice(soyad)
        
        student = {
            'username': generate_username(existing_usernames),
            'password': generate_password(),
            'email': generate_email(i),
            'firstname': random.choice(ad),
            'lastname': lastname,
            'city': random.choice(sehir),
            'profile_field_ulke': ulke,
            'profile_field_derssaat': ders_saati,
            'profile_field_DT': generate_random_date(),
            'profile_field_Sinif': random.randint(1, 10),
            'profile_field_veliad': f"{random.choice(ad)} {lastname}",
            'profile_field_VeliTel': generate_phone(),
            'profile_field_dilseviyesi': random.choice(dil_seviyesi),
            'profile_field_ogrenmeguc': random.choice(['var', 'yok']),
            'profile_field_foto': random.choice(['evet', 'hayir']),
            'profile_field_kamera': random.choice([0, 1])
        }
        data.append(student)
    
    return pd.DataFrame(data)

# Veri üret ve kaydet
num_students = int(input("Kaç öğrenci verisi üretmek istiyorsunuz? "))
df = generate_student_data(num_students)

# Excel dosyasına kaydet
filename = 'Kullanıcılar.xlsx'
df.to_excel(filename, index=False, engine='openpyxl')
print(f"\n{num_students} öğrenci verisi '{filename}' dosyasına kaydedildi!")
print(f"\nİlk 5 kayıt:")
print(df.head())


# In[16]:


ad

