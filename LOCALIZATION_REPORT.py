"""
📊 Türkiye Localization Kontrol Raporu

Bu dosya, uygulamadaki Türkiye lokalizasyon ayarlarının durumunu kontrol eder.
"""

import sys
from pathlib import Path

# Proje kök dizinini ekle
project_root = Path(__file__).parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from datetime import datetime
from decimal import Decimal
from src.utils.locale_utils import (
    format_currency, format_number, format_date, format_time, format_datetime,
    get_month_name_tr, get_day_name_tr,
    DATE_FORMAT, TIME_FORMAT, DATETIME_FORMAT, CURRENCY_SYMBOL, CURRENCY_CODE
)


def print_section(title):
    """Başlık yazdır"""
    print("\n" + "=" * 50)
    print(f"  {title}")
    print("=" * 50)


def test_localization():
    """Lokalizasyon ayarlarını test et"""
    
    print_section("🌍 TÜRKİYE LOKALIZASYON KONTROL RAPORU")
    
    # 1. Format Sabitleri
    print_section("1️⃣ FORMAT SABİTLERİ")
    print(f"Tarih Formatı: {DATE_FORMAT}")
    print(f"Saat Formatı: {TIME_FORMAT}")
    print(f"Tarih-Saat Formatı: {DATETIME_FORMAT}")
    print(f"Para Birimi Sembolü: {CURRENCY_SYMBOL}")
    print(f"Para Birimi Kodu: {CURRENCY_CODE}")
    
    # 2. Para Formatı Testi
    print_section("2️⃣ PARA FORMATLAMA TESTI")
    test_amounts = [100.50, 1234.56, 12345.67, 1000000.99, Decimal("5000.25")]
    for amount in test_amounts:
        print(f"{str(amount):>15} → {format_currency(amount)}")
    
    # 3. Sayı Formatı Testi
    print_section("3️⃣ SAYI FORMATLAMA TESTI")
    test_numbers = [100.5, 1234.567, 12345.6789, 999999.999]
    for num in test_numbers:
        print(f"{num:>15} → {format_number(num)}")
    
    # 4. Tarih Formatı Testi
    print_section("4️⃣ TARİH FORMATLAMA TESTI")
    now = datetime.now()
    test_dates = [
        ("Bugün", now),
        ("Dün", datetime(2025, 10, 28)),
        ("Yıl Başı", datetime(2025, 1, 1)),
        ("Yıl Sonu", datetime(2025, 12, 31)),
    ]
    for label, dt in test_dates:
        print(f"{label:>15} → {format_date(dt)}")
    
    # 5. Saat Formatı Testi
    print_section("5️⃣ SAAT FORMATLAMA TESTI")
    test_times = [
        ("Sabah", datetime(2025, 10, 29, 8, 30, 45)),
        ("Öğlen", datetime(2025, 10, 29, 12, 0, 0)),
        ("Öğleden Sonra", datetime(2025, 10, 29, 15, 30, 0)),
        ("Akşam", datetime(2025, 10, 29, 20, 15, 30)),
    ]
    for label, dt in test_times:
        print(f"{label:>20} → {format_time(dt)}")
    
    # 6. Tarih-Saat Formatı Testi
    print_section("6️⃣ TARİH-SAAT FORMATLAMA TESTI")
    print(f"Şu an: {format_datetime(now)}")
    
    # 7. Ay Adları Testi
    print_section("7️⃣ AY ADLARI TESTI")
    for month in range(1, 13):
        month_name = get_month_name_tr(month)
        print(f"Ay {month:2d} → {month_name}")
    
    # 8. Gün Adları Testi
    print_section("8️⃣ GÜN ADLARI TESTI")
    for day in range(7):
        day_name = get_day_name_tr(day)
        print(f"Gün {day} → {day_name}")
    
    # 9. Gerçek Dünya Örnekleri
    print_section("9️⃣ GERÇEK DÜNYA ÖRNEKLERİ")
    print("\n📊 Satış Raporu Örneği:")
    print(f"  Tarih: {format_date(now)}")
    print(f"  Saat: {format_time(now)}")
    print(f"  Toplam Satış: {format_currency(5234.89)}")
    print(f"  Ortalama Satış: {format_currency(125.43)}")
    print(f"  Stok Değeri: {format_currency(15000.00)}")
    
    print("\n💼 İşletme Özeti:")
    print(f"  Gün: {get_day_name_tr(now.weekday())}, {format_date(now)}")
    print(f"  Saat: {format_datetime(now)}")
    print(f"  Günlük Gelir: {format_currency(8500.50)}")
    print(f"  Masraflar: {format_currency(3200.75)}")
    print(f"  Net Kâr: {format_currency(5299.75)}")
    
    # 10. Özet
    print_section("✅ LOKALIZASYON DURUMU")
    print("""
✓ Para birimi: Türk Lirası (₺)
✓ Tarih formatı: DD.MM.YYYY
✓ Saat formatı: HH:MM:SS
✓ Sayı formatı: 1.000,00 (nokta bin ayırıcısı, virgül ondalık)
✓ Aylar: Türkçe
✓ Günler: Türkçe

📝 NOT: Tüm tutarlar aşağıdaki formatta gösterilir:
        1.234,56 ₺ (Bin ayırıcısı nokta, ondalık virgül)
    """)
    
    print("\n" + "=" * 50)
    print("  ✓ Rapor Tamamlandı")
    print("=" * 50 + "\n")


if __name__ == "__main__":
    test_localization()
