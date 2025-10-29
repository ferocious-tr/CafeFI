"""
⚙️ Türkiye Locale Ayarları Kurulum Dosyası

Uygulama başlatıldığında Türkiye locale ayarlarını yapılandırır.
"""

import locale as locale_lib
import os
from datetime import datetime
from src.utils.locale_utils import (
    DATE_FORMAT, TIME_FORMAT, DATETIME_FORMAT,
    CURRENCY_SYMBOL, CURRENCY_CODE
)


def configure_tr_locale():
    """
    Türkiye locale ayarlarını yapılandır
    
    Sistem locale'i Türkiye'ye ayarlar (mümkünse).
    Başarısız olursa İngilizce fallback yapar.
    """
    try:
        # Türkiye locale ayarları
        locale_lib.setlocale(locale_lib.LC_ALL, "tr_TR.UTF-8")
        return True
    except Exception:
        try:
            # Windows için alternatif
            locale_lib.setlocale(locale_lib.LC_ALL, "Turkish_Turkey.1254")
            return True
        except Exception:
            try:
                # Fallback: C locale
                locale_lib.setlocale(locale_lib.LC_ALL, "C")
                return False
            except Exception:
                return False


def log_locale_info():
    """Mevcut locale bilgilerini logla"""
    try:
        current_locale = locale_lib.getlocale()
        print(f"📍 Mevcut Locale: {current_locale}")
        print(f"📅 Tarih Formatı: {DATE_FORMAT}")
        print(f"🕐 Saat Formatı: {TIME_FORMAT}")
        print(f"💱 Para Birimi: {CURRENCY_CODE} ({CURRENCY_SYMBOL})")
        print(f"📝 Örnek Para: 1.234,56 {CURRENCY_SYMBOL}")
    except Exception as e:
        print(f"Locale info error: {e}")


if __name__ == "__main__":
    success = configure_tr_locale()
    log_locale_info()
    
    if success:
        print("\n✓ Türkiye locale ayarları başarıyla uygulandı")
    else:
        print("\n⚠️ Türkiye locale ayarlanamamış. İngilizce kullanılacak.")
