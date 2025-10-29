"""
💰 CafeFlow - Satış Modeli

Günlük satış işlemleri
"""

from sqlalchemy import Column, String, Integer, Numeric, ForeignKey, Boolean, Text
from sqlalchemy.orm import relationship
from src.models.base import BaseModel


class Sale(BaseModel):
    """
    Satış Modeli
    
    Özellikler:
        - sale_number: Satış numarası (fatura no)
        - product_id: Ürün ID'si
        - quantity: Satılan miktar
        - unit_price: Satış fiyatı
        - total_price: Toplam tutar
        - payment_method: Ödeme yöntemi
        - is_refunded: İade edildi mi?
    """
    
    __tablename__ = "sales"
    
    # Satış bilgisi
    sale_number = Column(String(50), unique=True, nullable=False, index=True)
    
    # Ürün ilişkisi
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False, index=True)
    product = relationship("Product", back_populates="sales")
    
    # Satış detayları
    quantity = Column(Integer, nullable=False)
    unit_price = Column(Numeric(10, 2), nullable=False)
    total_price = Column(Numeric(10, 2), nullable=False)
    
    # YENİ: KDV ve Kâr Hesaplaması
    sale_price_without_kdv = Column(Numeric(10, 2), nullable=False)  # KDV hariç satış fiyatı
    kdv_rate = Column(Numeric(5, 2), default=8.0, nullable=False)  # KDV oranı (%)
    kdv_amount = Column(Numeric(10, 2), default=0, nullable=False)  # KDV tutarı
    total_with_kdv = Column(Numeric(10, 2), nullable=False)  # KDV dahil toplam
    product_cost = Column(Numeric(10, 2), nullable=False)  # Ürün maliyeti
    gross_profit = Column(Numeric(10, 2), default=0, nullable=False)  # Brüt kâr (KDV hariç)
    net_profit = Column(Numeric(10, 2), default=0, nullable=False)  # Net kâr (KDV dahil)
    
    # Ödeme
    payment_method = Column(String(20), nullable=False)  # NAKİT, KART, HAVAYLE, vb.
    discount_amount = Column(Numeric(10, 2), default=0, nullable=False)
    
    # Statü
    is_refunded = Column(Boolean, default=False, nullable=False)
    refund_reason = Column(Text, nullable=True)
    
    # Notlar
    notes = Column(Text, nullable=True)
    
    PAYMENT_METHODS = {
        "NAKİT": "Nakit",
        "KART": "Kart",
        "HAVAYLE": "Havale",
        "ÇEK": "Çek",
        "DİĞER": "Diğer",
    }
    
    def __str__(self) -> str:
        """Satış açıklaması"""
        return f"Satış #{self.sale_number} - {self.quantity}x {self.product.name}"
    
    @property
    def payment_method_display(self) -> str:
        """Ödeme yöntemini Türkçe göster"""
        return self.PAYMENT_METHODS.get(self.payment_method, self.payment_method)
    
    def refund(self, reason: str = "", db_session=None):
        """
        Satışı iade et (geri al)
        
        Args:
            reason: İade sebebi
            db_session: Veritabanı oturumu
        """
        from src.models.stock_movement import StockMovement
        
        if self.is_refunded:
            return False  # Zaten iade edilmiş
        
        self.is_refunded = True
        self.refund_reason = reason
        
        # Stoğu geri ekle
        if db_session and self.product:
            self.product.quantity += self.quantity
            
            # Stok hareketini kaydet
            movement = StockMovement(
                product_id=self.product_id,
                movement_type="GİRİŞ",
                quantity=self.quantity,
                reason=f"İade - {reason}",
                reference_number=self.sale_number
            )
            db_session.add(movement)
        
        return True
    
    def calculate_net_total(self) -> float:
        """
        Net tutarı hesapla (indirimli)
        
        Returns:
            float: Net tutar
        """
        return float(self.total_price) - float(self.discount_amount)
