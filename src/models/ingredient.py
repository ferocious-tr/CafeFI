"""
Ingredients Model - Malzeme Yönetimi
"""

from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean
from datetime import datetime
from src.models.base import BaseModel


class Ingredient(BaseModel):
    """Malzeme (İçerik) Modeli"""
    
    __tablename__ = "ingredients"
    
    name = Column(String(100), unique=True, nullable=False)
    unit = Column(String(20), nullable=False)  # g, ml, adet
    cost_per_unit = Column(Float, nullable=False)  # Birim başına maliyet
    quantity = Column(Float, default=0)  # Mevcut stok
    is_active = Column(Boolean, default=True)
    
    # Sabit birim çevirimleri
    UNITS = {
        "g": "gram",
        "ml": "mililitre",
        "adet": "adet",
        "kg": "kilogram",
        "l": "litre"
    }
    
    # Birim dönüşüm tablosu (base unit'e)
    CONVERSIONS = {
        "g": 1,           # Base unit: gram
        "kg": 1000,       # 1 kg = 1000 g
        "ml": 1,          # Base unit: ml
        "l": 1000,        # 1 l = 1000 ml
        "adet": 1         # Dönüşüm yok (adet base unit)
    }
    
    def __repr__(self):
        return f"<Ingredient(id={self.id}, name='{self.name}', quantity={self.quantity}{self.unit})>"
    
    @property
    def unit_display(self):
        """Birim adını Türkçe göster"""
        return self.UNITS.get(self.unit, self.unit)
    
    @staticmethod
    def _is_convertible_unit_pair(unit1: str, unit2: str) -> bool:
        """İki birim türü uyumlu mu?"""
        # Gram-kg uyumlu, ml-l uyumlu
        gram_units = {"g", "kg"}
        ml_units = {"ml", "l"}
        adet_units = {"adet"}
        
        if unit1 in gram_units and unit2 in gram_units:
            return True
        if unit1 in ml_units and unit2 in ml_units:
            return True
        if unit1 in adet_units and unit2 in adet_units:
            return True
        return False
    
    @staticmethod
    def convert_quantity(quantity: float, from_unit: str, to_unit: str) -> float:
        """Bir birimden diğerine çevir"""
        if from_unit == to_unit:
            return quantity
        
        if not Ingredient._is_convertible_unit_pair(from_unit, to_unit):
            raise ValueError(
                f"'{from_unit}' ile '{to_unit}' uyumlu birimler değil! "
                f"(g-kg veya ml-l veya adet-adet eşleşmeleri gerekli)"
            )
        
        # Base unit'e çevir
        base_quantity = quantity * Ingredient.CONVERSIONS[from_unit]
        
        # Hedef unit'e çevir
        result = base_quantity / Ingredient.CONVERSIONS[to_unit]
        
        return result
    
    def is_low_stock(self, threshold: float = 100):
        """Stok düşük mü?"""
        return self.quantity < threshold
    
    def get_stock_status(self):
        """Stok durumunu metin olarak döndür"""
        if self.quantity == 0:
            return "❌ Tükenmiş"
        elif self.is_low_stock():
            return "⚠️ Düşük"
        else:
            return "✓ İyi"
    
    def add_stock(self, amount: float, amount_unit: str = None):
        """Stoğa ekle (birim dönüşümü ile)"""
        if amount <= 0:
            raise ValueError("Miktar 0'dan büyük olmalı!")
        
        # Eğer gelen birim farklıysa, dönüştür
        if amount_unit and amount_unit != self.unit:
            amount = self.convert_quantity(amount, amount_unit, self.unit)
        
        self.quantity += amount
    
    def remove_stock(self, amount: float, amount_unit: str = None):
        """Stoktan çıkar (birim dönüşümü ile)"""
        if amount <= 0:
            raise ValueError("Miktar 0'dan büyük olmalı!")
        
        # Eğer gelen birim farklıysa, dönüştür
        if amount_unit and amount_unit != self.unit:
            amount = self.convert_quantity(amount, amount_unit, self.unit)
        
        if self.quantity < amount:
            raise ValueError(
                f"Yetersiz stok! Mevcut: {self.quantity:.4f}{self.unit}, "
                f"İstenen: {amount:.4f}{self.unit}"
            )
        
        self.quantity -= amount
    
    def get_total_cost(self):
        """Toplam stok değerini hesapla"""
        return self.quantity * self.cost_per_unit
