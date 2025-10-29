# 🚀 CafeFlow - Kurulum ve Ortam Hazırlığı Rehberi

## 📋 Sistem Gereksinimleri

### Yazılım Gereksinimleri
- **Python**: 3.8 veya üstü
- **Git**: Versiyon kontrolü için
- **SQLite3**: Geliştirme ortamı için (Python'da yerleşik)
- **PostgreSQL**: Production ortamı için (opsiyonel)

### İşletim Sistemi Uyumluluğu
- ✅ Windows 10/11
- ✅ macOS 10.14+
- ✅ Linux (Ubuntu 18.04+, Debian 9+)

---

## 🛠 Kurulum Adımları

### 1. Proje Klasörü Hazırlığı

```bash
# Proje klasörüne gir
cd C:\Users\Ferhat\Desktop\CafeFI

# Klasör yapısını oluştur
mkdir -p src/{modules,utils,database,models}
mkdir -p data/{backups,exports}
mkdir -p logs
mkdir -p tests
mkdir -p config
```

### 2. Python Sanal Ortamı (Virtual Environment) Kurulumu

#### Windows üzerinde:
```bash
# Sanal ortam oluştur
python -m venv venv

# Sanal ortamı etkinleştir
venv\Scripts\activate
```

#### macOS/Linux üzerinde:
```bash
# Sanal ortam oluştur
python3 -m venv venv

# Sanal ortamı etkinleştir
source venv/bin/activate
```

### 3. Bağımlılıkları Yükleme

```bash
# pip'i güncelle
pip install --upgrade pip

# requirements.txt'den tüm paketleri yükle
pip install -r requirements.txt
```

### 4. Veritabanı Hazırlığı

#### Geliştirme Ortamı (SQLite):
```bash
# Veritabanı otomatik olarak oluşturulacak
# Herhangi bir ek yapılandırma gerekmez
```

#### Production Ortamı (PostgreSQL) - İsteğe Bağlı:
```bash
# PostgreSQL kurulumundan sonra veritabanı oluştur
createdb cafeflow_db

# Kullanıcı oluştur (PostgreSQL'de)
psql -U postgres
CREATE USER cafeflow WITH PASSWORD 'secure_password';
ALTER ROLE cafeflow SET client_encoding TO 'utf8';
ALTER ROLE cafeflow SET default_transaction_isolation TO 'read committed';
GRANT ALL PRIVILEGES ON DATABASE cafeflow_db TO cafeflow;
```

### 5. Ortam Değişkenleri Ayarlaması

`config/.env` dosyası oluştur:

```env
# Uygulama Ayarları
APP_NAME=CafeFlow
ENVIRONMENT=development
DEBUG=True

# Veritabanı Ayarları
DB_TYPE=sqlite  # sqlite veya postgresql
DB_NAME=cafeflow.db
DB_USER=cafeflow
DB_PASSWORD=password
DB_HOST=localhost
DB_PORT=5432

# Güvenlik
SECRET_KEY=your-secret-key-here-change-in-production
JWT_SECRET=your-jwt-secret-key

# S3 Konfigürasyonu (Opsiyonel)
AWS_ACCESS_KEY_ID=
AWS_SECRET_ACCESS_KEY=
AWS_S3_BUCKET_NAME=cafeflow-backups
AWS_REGION=us-east-1

# Streamlit Ayarları
STREAMLIT_SERVER_PORT=8501
STREAMLIT_SERVER_ADDRESS=localhost
```

### 6. Streamlit Konfigürasyonu

`config/.streamlit/config.toml` dosyası oluştur:

```toml
[theme]
primaryColor = "#8B4513"
backgroundColor = "#F5E6D3"
secondaryBackgroundColor = "#E8D4C0"
textColor = "#1A1A1A"
font = "sans serif"

[client]
toolbarMode = "developer"
maxUploadSize = 200

[server]
port = 8501
headless = true
runOnSave = true
```

---

## ✅ Kurulum Doğrulaması

### 1. Paket Versiyonlarını Kontrol Et

```bash
pip list
```

### 2. Python Sürümünü Kontrol Et

```bash
python --version
```

### 3. İlk Çalıştırma Testi

```bash
# Streamlit'i başlat
streamlit run app.py
```

Tarayıcı otomatik olarak açılmalı ve `http://localhost:8501` adresine yönlendirilmelidir.

---

## 📂 Proje Dizin Yapısı

```
CafeFI/
├── venv/                          # Python sanal ortamı
├── src/
│   ├── app.py                     # Ana Streamlit uygulaması
│   ├── modules/
│   │   ├── dashboard.py           # Dashboard modülü
│   │   ├── sales.py               # Satış modülü
│   │   ├── inventory.py           # Stok modülü
│   │   ├── expenses.py            # Masraf modülü
│   │   ├── personnel.py           # Personel modülü
│   │   └── reports.py             # Raporlama modülü
│   ├── utils/
│   │   ├── helpers.py             # Yardımcı fonksiyonlar
│   │   ├── validators.py          # Veri validasyonu
│   │   └── formatters.py          # Veri formatı işlemleri
│   ├── database/
│   │   ├── db_connection.py       # Veritabanı bağlantısı
│   │   ├── queries.py             # SQL sorguları
│   │   └── migrations.py          # Veritabanı migrasyonları
│   └── models/
│       ├── product.py             # Ürün modeli
│       ├── category.py            # Kategori modeli
│       ├── sale.py                # Satış modeli
│       ├── expense.py             # Masraf modeli
│       └── personnel.py           # Personel modeli
├── data/
│   ├── cafeflow.db                # SQLite veritabanı (development)
│   ├── backups/                   # Veritabanı yedekleri
│   └── exports/                   # Dışa aktarılmış raporlar
├── logs/
│   └── app.log                    # Uygulama logları
├── tests/
│   ├── test_database.py           # Veritabanı testleri
│   ├── test_modules.py            # Modül testleri
│   └── test_utils.py              # Yardımcı fonksiyon testleri
├── config/
│   ├── .env                       # Ortam değişkenleri
│   └── .streamlit/
│       └── config.toml            # Streamlit konfigürasyonu
├── requirements.txt               # Python bağımlılıkları
├── SETUP.md                       # Bu dosya
├── spec.md                        # Teknik şartname
└── README.md                      # Proje README'si (oluşturulacak)
```

---

## 🔍 Sorun Giderme

### Problem: `ModuleNotFoundError: No module named 'streamlit'`
**Çözüm**: Sanal ortamın etkin olduğundan emin ol ve `pip install -r requirements.txt` komutunu çalıştır.

### Problem: `Permission denied` (Linux/macOS)
**Çözüm**: `chmod +x venv/bin/activate` komutunu çalıştır.

### Problem: PostgreSQL bağlantı hatası
**Çözüm**: PostgreSQL servisinin çalıştığından emin ol ve `.env` dosyasındaki veritabanı bilgilerini kontrol et.

### Problem: Streamlit portu zaten kullanımda
**Çözüm**: `streamlit run app.py --server.port 8502` komutunu çalıştır.

---

## 📚 Faydalı Komutlar

```bash
# Sanal ortamı etkinleştir
venv\Scripts\activate  # Windows
source venv/bin/activate  # macOS/Linux

# Sanal ortamı devre dışı bırak
deactivate

# Yeni paket yükle
pip install paket_adı

# Bağımlılıkları güncelle
pip install --upgrade -r requirements.txt

# requirements.txt'i güncelle
pip freeze > requirements.txt

# Streamlit'i başlat
streamlit run src/app.py

# Testleri çalıştır
pytest tests/

# Veritabanını yedekle
cp data/cafeflow.db data/backups/cafeflow_$(date +%Y%m%d_%H%M%S).db
```

---

## 📖 Sonraki Adımlar

1. ✅ Kurulum tamamla ve doğrula
2. 📝 Veritabanı şemasını oluştur (`models/` klasörü)
3. 🔧 Ana uygulamayı (`app.py`) oluştur
4. 📊 Dashboard modülünü geliştir
5. 🧪 Test dosyalarını yaz

---

## 📞 İletişim ve Destek

Kurulumla ilgili soruların varsa, lütfen `.md` dosyasında belirtilenleri kontrol et veya hata mesajını detaylı bir şekilde paylaş.

**Son Güncelleme**: 27 Ekim 2025

