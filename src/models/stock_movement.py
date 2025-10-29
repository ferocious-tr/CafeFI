"""
📊 CafeFlow - Stok Hareketi Modeli

Stok girişi, çıkışı ve ayarlamalarını takip eder
"""

from sqlalchemy import Column, String, Integer, Text, ForeignKey, Numeric
from sqlalchemy.orm import relationship
from src.models.base import BaseModel


class StockMovement(BaseModel):
    """
    Stok Hareketi Modeli
    
    Özellikler:
        - product_id: Ürün ID'si
        - movement_type: Hareket türü (GİRİŞ, ÇIKIŞ, AYARLAMA)
        - quantity: Miktar
        - reason: Hareket sebebi
        - notes: Notlar
    """
    
    __tablename__ = "stock_movements"
    
    # Ürün ilişkisi
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False, index=True)
    product = relationship("Product", back_populates="stock_movements")
    
    # Hareket bilgisi
    movement_type = Column(String(20), nullable=False)  # GİRİŞ, ÇIKIŞ, AYARLAMA
    quantity = Column(Integer, nullable=False)
    reason = Column(String(200), nullable=True)
    notes = Column(Text, nullable=True)
    
    # Referans
    reference_number = Column(String(50), nullable=True, index=True)  # Fatura, satış numarası, vb.
    
    MOVEMENT_TYPES = {
        "GİRİŞ": "Stok Girişi",
        "ÇIKIŞ": "Stok Çıkışı",
        "AYARLAMA": "Stok Ayarlaması",
        "SAYIM": "Envanter Sayımı",
    }
    
    def __str__(self) -> str:
        """Hareket açıklaması"""
        return f"{self.movement_type} - {self.quantity} adet ({self.reason})"
    
    @property
    def movement_type_display(self) -> str:
        """Hareket türünü Türkçe göster"""
        return self.MOVEMENT_TYPES.get(self.movement_type, self.movement_type)
    
    def get_sign(self) -> int:
        """
        Hareket işaretini döndür (+ veya -)
        
        Returns:
            int: +1 (giriş), -1 (çıkış)
        """
        if self.movement_type in ["GİRİŞ", "AYARLAMA"]:
            return 1
        else:
            return -1
