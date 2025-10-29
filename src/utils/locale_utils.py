"""
🌍 Türkiye Locale Ayarları ve Formatting Fonksiyonları

Tarih, saat, para birimi ve sayı formatı Türkiye standardına göre.
"""

from datetime import datetime
from decimal import Decimal
from typing import Union


# Türkiye Tarih/Saat Ayarları
LOCALE_TR = "tr_TR.UTF-8"
DATE_FORMAT = "%d.%m.%Y"
TIME_FORMAT = "%H:%M:%S"
DATETIME_FORMAT = "%d.%m.%Y %H:%M:%S"

# Para Birimi
CURRENCY_SYMBOL = "₺"
CURRENCY_CODE = "TRY"


def format_currency(amount: Union[float, Decimal], symbol: str = CURRENCY_SYMBOL) -> str:
    """
    Para tutarını Türkiye formatında göster
    
    Örnek: 1234.56 -> "1.234,56 ₺"
    
    Args:
        amount: Tutar (float veya Decimal)
        symbol: Para birimi sembolü (varsayılan: ₺)
    
    Returns:
        str: Biçimlendirilmiş tutar
    """
    if isinstance(amount, Decimal):
        amount = float(amount)
    
    # Bin ayırıcı: nokta, ondalık ayırıcı: virgül
    # 1234.56 -> "1.234,56"
    formatted = f"{amount:,.2f}".replace(",", " ").replace(".", ",").replace(" ", ".")
    
    return f"{formatted} {symbol}"


def format_number(value: Union[float, Decimal], decimal_places: int = 2) -> str:
    """
    Sayıyı Türkiye formatında göster
    
    Örnek: 1234.5678 -> "1.234,57"
    
    Args:
        value: Sayı
        decimal_places: Ondalık basamak sayısı
    
    Returns:
        str: Biçimlendirilmiş sayı
    """
    if isinstance(value, Decimal):
        value = float(value)
    
    # Bin ayırıcı: nokta, ondalık ayırıcı: virgül
    format_str = f"{{:,.{decimal_places}f}}"
    formatted = format_str.format(value).replace(",", " ").replace(".", ",").replace(" ", ".")
    
    return formatted


def format_date(date_obj: datetime, fmt: str = DATE_FORMAT) -> str:
    """
    Tarihi Türkiye formatında göster
    
    Örnek: datetime(2025, 10, 29) -> "29.10.2025"
    
    Args:
        date_obj: Tarih nesnesi
        fmt: Format string (varsayılan: DD.MM.YYYY)
    
    Returns:
        str: Biçimlendirilmiş tarih
    """
    if not isinstance(date_obj, datetime):
        raise TypeError("date_obj must be a datetime object")
    
    return date_obj.strftime(fmt)


def format_time(time_obj: datetime, fmt: str = TIME_FORMAT) -> str:
    """
    Saati Türkiye formatında göster
    
    Örnek: datetime(..., 14, 30, 45) -> "14:30:45"
    
    Args:
        time_obj: Zaman nesnesi
        fmt: Format string (varsayılan: HH:MM:SS)
    
    Returns:
        str: Biçimlendirilmiş saat
    """
    if not isinstance(time_obj, datetime):
        raise TypeError("time_obj must be a datetime object")
    
    return time_obj.strftime(fmt)


def format_datetime(dt_obj: datetime, fmt: str = DATETIME_FORMAT) -> str:
    """
    Tarih ve saati Türkiye formatında göster
    
    Örnek: datetime(2025, 10, 29, 14, 30, 45) -> "29.10.2025 14:30:45"
    
    Args:
        dt_obj: Tarih-saat nesnesi
        fmt: Format string (varsayılan: DD.MM.YYYY HH:MM:SS)
    
    Returns:
        str: Biçimlendirilmiş tarih-saat
    """
    if not isinstance(dt_obj, datetime):
        raise TypeError("dt_obj must be a datetime object")
    
    return dt_obj.strftime(fmt)


def get_month_name_tr(month: int) -> str:
    """
    Ay numarasını Türkçe ay adıyla döndür
    
    Args:
        month: Ay numarası (1-12)
    
    Returns:
        str: Türkçe ay adı
    """
    months = {
        1: "Ocak", 2: "Şubat", 3: "Mart", 4: "Nisan",
        5: "Mayıs", 6: "Haziran", 7: "Temmuz", 8: "Ağustos",
        9: "Eylül", 10: "Ekim", 11: "Kasım", 12: "Aralık"
    }
    return months.get(month, "Bilinmiyor")


def get_day_name_tr(weekday: int) -> str:
    """
    Gün numarasını Türkçe gün adıyla döndür
    
    Args:
        weekday: Gün numarası (0=Pazartesi, 6=Pazar)
    
    Returns:
        str: Türkçe gün adı
    """
    days = {
        0: "Pazartesi",
        1: "Salı",
        2: "Çarşamba",
        3: "Perşembe",
        4: "Cuma",
        5: "Cumartesi",
        6: "Pazar"
    }
    return days.get(weekday, "Bilinmiyor")


if __name__ == "__main__":
    # Test
    now = datetime.now()
    
    print("Türkiye Locale Formatı Test")
    print("-" * 40)
    print(f"Para: {format_currency(1234.56)}")
    print(f"Sayı: {format_number(1234.5678)}")
    print(f"Tarih: {format_date(now)}")
    print(f"Saat: {format_time(now)}")
    print(f"Tarih-Saat: {format_datetime(now)}")
    print(f"Ay: {get_month_name_tr(now.month)}")
    print(f"Gün: {get_day_name_tr(now.weekday())}")
