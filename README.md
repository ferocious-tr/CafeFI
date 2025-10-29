# ☕ CafeFlow - Cafe Muhasebe Sistemi

<div align="center">

**Streamlit ve Python tabanlı, bulut destekli cafe muhasebe ve operasyon yönetim sistemi**

![Python](https://img.shields.io/badge/Python-3.8%2B-blue)
![Streamlit](https://img.shields.io/badge/Streamlit-1.41.0-red)
![License](https://img.shields.io/badge/License-MIT-green)

[Özellikler](#-özellikler) • [Kurulum](#-kurulum) • [Başlangıç](#-hızlı-başlangıç) • [Dokümantasyon](#-dokümantasyon)

</div>

---

## 🎯 Proje Hakkında

CafeFlow, küçük ve orta ölçekli kafe işletmecileri için tasarlanmış, tüm iş süreçlerini yönetmek için bir çözümdür. Stok takibi, satış kaydı, masraf yönetimi, personel takibi ve finansal raporlama gibi tüm işlemleri tek bir platform üzerinden yapabilirsiniz.

### 📊 Ana Özellikler

- ✅ **Stok Yönetimi**: Malzeme takibi, otomatik sipariş önerisi
- ✅ **Satış & Gelir**: Günlük satış kaydı, ödeme yöntemi takibi
- ✅ **Masraf Takibi**: Sabit ve değişken masrafları kategorize edin
- ✅ **Personel Yönetimi**: Çalışan kayıtları, maaş bordrosu
- ✅ **Finansal Raporlar**: Gerçek zamanlı dashboard, kar/zarar analizi
- ✅ **Excel Entegrasyonu**: Import/Export desteği
- ✅ **Kullanıcı Dostu**: Responsive web arayüzü

---

## 🛠 Teknoloji Stack

| Bileşen | Kütüphane | Versiyon |
|---------|-----------|---------|
| **Frontend** | Streamlit | 1.41.0 |
| **Backend** | Python | 3.8+ |
| **Veritabanı** | SQLite/PostgreSQL | - |
| **Veri Analizi** | Pandas, NumPy | 2.1.3, 1.26.2 |
| **Görselleştirme** | Plotly, Matplotlib | 5.18.0, 3.8.2 |
| **ORM** | SQLAlchemy | 2.0.34 |

---

## 📋 Kurulum

### Ön Gereksinimler

- Python 3.8 veya üstü
- pip (Python paket yöneticisi)
- Git

### Adım 1: Depoyu Klonla

```bash
cd C:\\Users\\Ferhat\\Desktop
git clone https://github.com/yourusername/CafeFI.git
cd CafeFI
```

### Adım 2: Sanal Ortam Oluştur

```bash
# Windows
python -m venv venv
venv\\Scripts\\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### Adım 3: Bağımlılıkları Yükle

```bash
pip install -r requirements.txt
```

### Adım 4: Ortam Değişkenlerini Ayarla

```bash
# .env.example'ı kopyala
cp .env.example .env

# .env dosyasını düzenle (gerekirse)
# nano .env  veya  code .env
```

### Adım 5: Uygulamayı Başlat

```bash
streamlit run src/app.py
```

Tarayıcınız otomatik olarak `http://localhost:8501` adresine yönlendirilecektir.

---

## 🚀 Hızlı Başlangıç

### Proje Başlatıcı Script'i Çalıştır

```bash
python init_project.py
```

Bu script otomatik olarak tüm klasörleri ve yer tutucu dosyaları oluşturacaktır.

### Örnek Veriler Yükle (Opsiyonel)

```bash
python src/database/populate_sample_data.py
```

---

## 📁 Proje Yapısı

```
CafeFI/
├── src/
│   ├── app.py                    # Ana uygulama
│   ├── modules/                  # Modüller
│   │   ├── dashboard.py
│   │   ├── sales.py
│   │   ├── inventory.py
│   │   ├── expenses.py
│   │   ├── personnel.py
│   │   └── reports.py
│   ├── utils/                    # Yardımcı araçlar
│   ├── database/                 # Veritabanı bağlantısı
│   └── models/                   # Veri modelleri
├── data/
│   ├── cafeflow.db               # SQLite veritabanı
│   ├── backups/                  # Veritabanı yedekleri
│   └── exports/                  # Dışa aktarılmış raporlar
├── tests/                        # Birim testleri
├── logs/                         # Uygulama logları
├── config/
│   ├── .env.example              # Ortam değişkenleri örneği
│   └── .streamlit/config.toml    # Streamlit konfigürasyonu
├── requirements.txt              # Python bağımlılıkları
├── SETUP.md                      # Kurulum rehberi
├── spec.md                       # Teknik şartname
└── README.md                     # Bu dosya
```

---

## 📚 Dokümantasyon

- 📖 [Kurulum Rehberi](SETUP.md) - Ayrıntılı kurulum adımları
- 📋 [Teknik Şartname](spec.md) - Proje özellikleri ve mimarisi
- 🔧 [API Dokümantasyonu](docs/API.md) - (Hazırlanacak)
- 🎓 [Geliştirici Rehberi](docs/CONTRIBUTING.md) - (Hazırlanacak)

---

## 🐛 Sorun Bildir

Bir hata veya sorun buldum mi? Lütfen [Issues](https://github.com/yourusername/CafeFI/issues) sayfasında bir sorun açın.

---

## 💡 Önerileri Gönder

Proje hakkında bir fikrin mi var? Tartışmak için [Discussions](https://github.com/yourusername/CafeFI/discussions) sekmesini kullan.

---

## 📝 Lisans

Bu proje MIT Lisansı altında yayınlanmıştır. Daha fazla bilgi için [LICENSE](LICENSE) dosyasına bakın.

---

## 👨‍💻 Katkıda Bulunanlar

- **Ferhat** - Proje Kurucusu

---

## 📞 İletişim

- 📧 Email: [email@example.com]
- 🐦 Twitter: [@yourhandle]
- 💼 LinkedIn: [Your Profile]

---

## 🙏 Teşekkürler

Bu projede kullanılan tüm açık kaynak kütüphanelerin ve framework'lerin geliştiricilerine teşekkür ederiz.

---

<div align="center">

**CafeFlow** ile cafe işletmenizi dijitalleştirin! ☕📊

Made with ❤️ by Ferhat

</div>