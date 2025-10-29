# 🌍 Türkiye Lokalizasyon Ayarları

CafeFlow uygulaması **Türkiye** standardına göre yapılandırılmıştır.

## 📊 Mevcut Ayarlar

| Ayar | Değer | Örnek |
|------|-------|-------|
| **Para Birimi** | Türk Lirası (₺) | 1.234,56 ₺ |
| **Tarih Formatı** | DD.MM.YYYY | 29.10.2025 |
| **Saat Formatı** | HH:MM:SS | 14:30:45 |
| **Sayı Formatı** | Bin: nokta, Ondalık: virgül | 1.000,00 |
| **Aylar** | Türkçe | Ocak, Şubat, ... |
| **Günler** | Türkçe | Pazartesi, Salı, ... |

## 📁 İlgili Dosyalar

### Locale Utilities (`src/utils/locale_utils.py`)
- `format_currency(amount)` - Para formatı: 1.234,56 ₺
- `format_number(value)` - Sayı formatı: 1.234,56
- `format_date(date_obj)` - Tarih formatı: 29.10.2025
- `format_time(time_obj)` - Saat formatı: 14:30:45
- `format_datetime(dt_obj)` - Tarih-Saat: 29.10.2025 14:30:45
- `get_month_name_tr(month)` - Ay adı: "Ocak"
- `get_day_name_tr(weekday)` - Gün adı: "Pazartesi"

### Locale Konfigürasyon (`src/config/locale_config.py`)
- `configure_tr_locale()` - Sistem locale ayarlarını Türkiye'ye çevir
- `log_locale_info()` - Mevcut locale bilgilerini logla

## 🔧 Kullanım Örneği

```python
from src.utils.locale_utils import format_currency, format_datetime

# Para formatı
amount = 5234.89
print(format_currency(amount))  # Çıktı: 5.234,89 ₺

# Tarih-Saat formatı
from datetime import datetime
dt = datetime.now()
print(format_datetime(dt))  # Çıktı: 29.10.2025 14:30:45
```

## 📋 Test Raporu

Lokalizasyon ayarlarını test etmek için:

```bash
python LOCALIZATION_REPORT.py
```

Bu komut, tüm format fonksiyonlarının çalışıp çalışmadığını kontrol eder ve detaylı bir rapor oluşturur.

## ✅ Kontrol Edilen Alanlar

- ✓ **Dashboard**: Tarih ve saat gösterimi
- ✓ **Satış**: Para tutarları (1.234,56 ₺ formatında)
- ✓ **Masraflar**: Para tutarları ve tarihler
- ✓ **Raporlar**: Tüm sayısal veriler Türkiye formatında
- ✓ **Envanter**: Maliyet ve tutar gösterimleri

## 🚀 Uygulamada Kullanım

Tüm yeni para/tarih gösterimlerinde utility fonksiyonları kullanın:

```python
# ❌ Eski (kaçılması gereken)
f"₺{amount:.2f}"
dt.strftime("%d.%m.%Y")

# ✅ Yeni (önerilir)
format_currency(amount)
format_date(dt)
```

## 📝 Notlar

- Para birimi sembolü: **₺** (Türk Lirası)
- Virgül (`,`) = Ondalık ayırıcısı
- Nokta (`.`) = Bin ayırıcısı
- Örnek: 1.234.567,89 ₺ = Bir milyon iki yüz otuz dört bin beş yüz altmış yedi lira seksen dokuz kuruş
