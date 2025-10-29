"""
📋 CafeFlow - Masraf Modeli

Sabit ve değişken masrafları takip eder
"""

from sqlalchemy import Column, String, Numeric, Text, Boolean
from src.models.base import BaseModel


class Expense(BaseModel):
    """
    Masraf Modeli
    
    Özellikler:
        - description: Masraf açıklaması
        - category: Masraf kategorisi
        - amount: Tutar
        - is_recurring: Tekrarlayan mı?
        - payment_method: Ödeme yöntemi
    """
    
    __tablename__ = "expenses"
    
    # Masraf bilgisi
    description = Column(String(200), nullable=False)
    category = Column(String(50), nullable=False, index=True)
    amount = Column(Numeric(10, 2), nullable=False)
    
    # Ödeme bilgisi
    payment_method = Column(String(20), nullable=False)  # NAKİT, BANKA, KART, vb.
    reference_number = Column(String(100), nullable=True)  # Fatura, receit, vb.
    
    # Tekrarlayan masraflar
    is_recurring = Column(Boolean, default=False, nullable=False)
    recurring_type = Column(String(20), nullable=True)  # GÜNLÜK, HAFTALIK, AYLIK, YILLIK
    
    # Notlar
    notes = Column(Text, nullable=True)
    
    EXPENSE_CATEGORIES = {
        "KİRA": "Kira",
        "ELEKTRİK": "Elektrik",
        "SU": "Su",
        "DOĞALGAZ": "Doğal Gaz",
        "İNTERNET": "İnternet",
        "TELEFON": "Telefon",
        "MALZEMELERİ": "Malzemeleri",
        "PERSONELİ": "Personeli",
        "MARKETİNG": "Pazarlama",
        "SİGORTA": "Sigorta",
        "DİĞER": "Diğer",
    }
    
    PAYMENT_METHODS = {
        "NAKİT": "Nakit",
        "BANKA": "Banka Transferi",
        "KART": "Kredi Kartı",
        "ÇEK": "Çek",
        "DİĞER": "Diğer",
    }
    
    RECURRING_TYPES = {
        "GÜNLÜK": "Günlük",
        "HAFTALIK": "Haftalık",
        "AYLIK": "Aylık",
        "YILLIK": "Yıllık",
    }
    
    def __str__(self) -> str:
        """Masraf açıklaması"""
        return f"{self.category} - ₺{float(self.amount):.2f}"
    
    @property
    def category_display(self) -> str:
        """Kategoriyi Türkçe göster"""
        return self.EXPENSE_CATEGORIES.get(self.category, self.category)
    
    @property
    def payment_method_display(self) -> str:
        """Ödeme yöntemini Türkçe göster"""
        return self.PAYMENT_METHODS.get(self.payment_method, self.payment_method)
    
    @property
    def recurring_type_display(self) -> str:
        """Tekrarlama türünü Türkçe göster"""
        if not self.is_recurring:
            return "Tek Seferlik"
        return self.RECURRING_TYPES.get(self.recurring_type, self.recurring_type)
