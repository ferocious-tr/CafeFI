# 📁 CafeFlow - Proje Yapısı

```
CafeFI/
│
├── 📄 README.md                    # Proje tanıtımı
├── 📄 SETUP.md                     # Kurulum rehberi
├── 📄 PROGRESS.md                  # Geliştirme ilerlemesi
├── 📄 RELEASE_NOTES.md             # Sürüm notları
├── 📄 spec.md                      # Teknik özellikler
│
├── 📋 requirements.txt             # Python bağımlılıkları (60+ paket)
├── 📋 init_project.py              # Proje başlatma scripti
│
├── 📁 config/                      # Konfigürasyon dosyaları
│   └── .env.example                # Çevre değişkenleri şablonu
│
├── 📁 data/                        # Veri dizini
│   ├── cafeflow.db                 # SQLite Veritabanı (~86KB)
│   ├── backups/                    # Yedek dosyaları
│   └── exports/                    # Dışa aktarılan veriler
│
├── 📁 logs/                        # Uygulama günlükleri
│   └── cafeflow.log
│
├── 📁 src/                         # Ana uygulama kodu
│   ├── __init__.py
│   ├── app.py                      # Ana Streamlit uygulaması (~363 satır)
│   │
│   ├── 📁 database/                # Veritabanı modülü
│   │   ├── __init__.py             # Engine ve fonksiyonlar
│   │   ├── db_connection.py        # Bağlantı yönetimi (~165 satır)
│   │   └── init_db.py              # Veritabanı başlatma (~200 satır)
│   │
│   ├── 📁 models/                  # Veri modelleri (ORM)
│   │   ├── __init__.py             # Model ihracları
│   │   ├── base.py                 # Temel model sınıfı (~90 satır)
│   │   ├── category.py             # Kategori modeli (~70 satır)
│   │   ├── product.py              # Ürün modeli (~180 satır)
│   │   ├── stock_movement.py       # Stok hareketi modeli (~75 satır)
│   │   ├── sale.py                 # Satış modeli (~130 satır)
│   │   └── expense.py              # Masraf modeli (~100 satır)
│   │
│   ├── 📁 modules/                 # İş mantığı modülleri
│   │   ├── __init__.py
│   │   ├── inventory.py            # Stok Yönetimi (~600 satır)
│   │   ├── expenses.py             # Masraf Takibi (~600 satır)
│   │   └── sales.py                # Satış (TODO)
│   │
│   └── 📁 utils/                   # Yardımcı fonksiyonlar
│       └── __init__.py             # Ortak fonksiyonlar
│
├── 📁 templates/                   # Streamlit şablonları (opsiyonel)
│
└── 📁 tests/                       # Test dosyaları
    ├── __init__.py
    └── test_placeholder.py         # Placeholder testler

---

## 📊 Dosya İstatistikleri

| Kategori | Sayı | Toplam KB |
|----------|------|----------|
| Python Dosyaları | 18 | ~300 KB |
| Konfigürasyon | 2 | ~10 KB |
| Veritabanı | 1 | ~86 KB |
| Döküman | 6 | ~50 KB |
| **TOPLAM** | **27** | **~450 KB** |

---

## 🔑 Ana Dosyaların Açıklaması

### **1. src/app.py** (363 satır)
**Ana Streamlit Uygulaması**
- Sayfa routing ve navigasyon
- 6 sayfalık yapı (Dashboard, Satış, Stok, Masraf, Raporlar, Ayarlar)
- Sidebar menüsü ve durum göstergesi
- Veritabanı entegrasyonu

### **2. src/modules/inventory.py** (600 satır)
**Stok Yönetimi Modülü**
- `InventoryManager` sınıfı (12 metod)
- CRUD işlemleri
- Stok hareketi takibi
- Raporlama ve analiz
- Streamlit UI (5 tab)

### **3. src/modules/expenses.py** (600 satır)
**Masraf Takibi Modülü**
- `ExpenseManager` sınıfı (12 metod)
- Masraf CRUD işlemleri
- Kategori ve ödeme yöntemi filtreleme
- Aylık ve kategori analizi
- Streamlit UI (4 tab)

### **4. src/database/db_connection.py** (165 satır)
**Veritabanı Bağlantısı**
- `DatabaseConfig` sınıfı
- `DatabaseEngine` sınıfı
- Session yönetimi
- Bağlantı havuzu (connection pooling)

### **5. src/database/init_db.py** (200 satır)
**Veritabanı İnisiyalizasyonu**
- `init_database()` - Tablo oluşturma
- `populate_initial_data()` - Varsayılan veriler
- `reset_database()` - Veritabanını sıfırla

### **6. src/models/*.py** (650+ satır toplam)
**ORM Modelleri**
- `base.py` - Temel model sınıfı
- `category.py` - 5 kategori tanımı
- `product.py` - Ürün özellikleri (fiyat, stok, kar marjı)
- `stock_movement.py` - Stok hareketleri (GİRİŞ/ÇIKIŞ/AYARLAMA)
- `sale.py` - Satış işlemleri (payment methods, refund)
- `expense.py` - Masraf takibi (kategoriler, ödemeler)

### **7. requirements.txt** (60+ paket)
**Python Bağımlılıkları**
- Web Framework: streamlit, streamlit-aggrid
- ORM: sqlalchemy, psycopg2-binary
- Veri İşleme: pandas, numpy, openpyxl
- Görselleştirme: matplotlib, plotly
- Güvenlik: bcrypt, cryptography, PyJWT
- Diğer: python-dotenv, sqlparse, vb.

---

## 🗄️ Veritabanı Yapısı

```
cafeflow.db (SQLite)
│
├── categories (5 satır)
│   ├── id (PK)
│   ├── name, code, description
│   └── is_active, display_order
│
├── products (5 satır test)
│   ├── id (PK)
│   ├── category_id (FK → categories)
│   ├── name, code, price, cost_price
│   ├── quantity, unit, min_stock_level
│   └── is_active, created_at, updated_at
│
├── stock_movements (5+ satır)
│   ├── id (PK)
│   ├── product_id (FK → products)
│   ├── movement_type (GİRİŞ/ÇIKIŞ/AYARLAMA)
│   ├── quantity, reason, reference_number
│   └── created_at, updated_at
│
├── sales (0 satır)
│   ├── id (PK)
│   ├── product_id (FK → products)
│   ├── quantity, unit_price, total_price
│   ├── payment_method, is_refunded
│   └── sale_number, created_at, updated_at
│
└── expenses (3 satır test)
    ├── id (PK)
    ├── description, category
    ├── amount, payment_method
    ├── reference_number, notes
    ├── is_recurring, recurring_type
    └── created_at, updated_at
```

---

## 🔄 Modüller Arası İlişkiler

```
dashboard (src/app.py)
├── İstatistikler (Tüm modelleri oku)
├── Düşük stok uyarıları (products query)
└── Son satışlar (sales query)

inventory module (src/modules/inventory.py)
├── CRUD → Product modeli
├── Stock Ops → StockMovement modeli
└── Reports → Pandas aggregation

expenses module (src/modules/expenses.py)
├── CRUD → Expense modeli
└── Reports → SQL aggregation

database engine (src/database/)
├── SQLAlchemy ORM
├── Session management
└── SQLite/PostgreSQL compatibility
```

---

## 📦 Paket Bağımlılıkları (Seçilmiş)

### Core
- `streamlit==1.41.0` - Web framework
- `sqlalchemy==2.0.34` - ORM
- `python-dotenv==1.0.1` - Env yönetimi

### Data
- `pandas>=2.2.0` - Veri işleme
- `numpy>=1.26.2` - Numerik işlemler
- `openpyxl>=3.1.0` - Excel support

### UI
- `streamlit-aggrid==1.1.9` - Tablo widget
- `matplotlib==3.9.3` - Grafikler

### DB
- `psycopg2-binary==2.9.12` - PostgreSQL (optional)
- `sqlparse==0.5.3` - SQL parsing

### Güvenlik
- `bcrypt==4.1.0` - Parola hash
- `cryptography==45.0.0` - Şifreleme
- `PyJWT==2.8.1` - JWT tokens

---

## 🚀 Başlatma Dosyaları

### `init_project.py`
Projeyi ilk kez başlatmak için kullanılan script.

```bash
python init_project.py
```

### `src/database/init_db.py`
Veritabanını sıfırlamak ve örnek veriler yüklemek için:

```bash
python -m src.database.init_db
```

### `src/app.py`
Ana uygulamayı çalıştırmak için:

```bash
streamlit run src/app.py
```

---

## 📋 Dosya İzinleri (Önerilen)

```
data/           - 755 (R/W)
data/cafeflow.db - 644 (R/W)
logs/           - 755 (R/W)
src/            - 755 (R)
config/         - 700 (R, hassas)
```

---

## 💾 Yedekleme Stratejisi

### Günlük Yedekleme
```bash
copy data\cafeflow.db data\backups\cafeflow.db.YYYY-MM-DD
```

### Export Komutları
```bash
# Masrafları CSV'ye aktar
# Dashboard → Masraf Raporu → Export (TODO)

# Ürünleri listele
# Dashboard → Stok Modülü → Rapor → İndir (TODO)
```

---

## 🔒 Hassas Dosyalar

- `.env` - Veritabanı şifreleri ve konfigürasyon
- `data/cafeflow.db` - Finansal veriler
- `logs/*.log` - Sistem günlükleri

**NOT:** Bunları versiyon kontrolünden hariç tutun!

---

**Son Güncelleme:** 27 Ekim 2025  
**Yapı Versiyonu:** 1.0.0
