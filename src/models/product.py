"""
📦 CafeFlow - Ürün Modeli

Cafe ürünleri (Kahve, Kahvaltılık, vb.)
"""

from sqlalchemy import Column, String, Float, Integer, Boolean, Text, ForeignKey, Numeric
from sqlalchemy.orm import relationship
from decimal import Decimal
from src.models.base import BaseModel


class Product(BaseModel):
    """
    Ürün Modeli
    
    Özellikler:
        - name: Ürün adı
        - code: Ürün kodu (SKU)
        - category_id: Kategori ID'si
        - price: Satış fiyatı
        - cost_price: Maliyet fiyatı
        - quantity: Stok miktarı
        - unit: Birim (adet, kg, litre, vb.)
        - is_active: Aktif mi?
    """
    
    __tablename__ = "products"
    
    name = Column(String(200), nullable=False, index=True)
    code = Column(String(50), unique=True, nullable=False, index=True)
    description = Column(Text, nullable=True)
    
    # Kategori ilişkisi
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=False, index=True)
    category = relationship("Category", back_populates="products")
    
    # Fiyat bilgisi
    price = Column(Numeric(10, 2), nullable=False)  # Satış fiyatı
    cost_price = Column(Numeric(10, 2), nullable=True)  # Maliyet fiyatı
    
    # YENİ: Satış Modülü için alanlar
    kdv_rate = Column(Numeric(5, 2), default=8.0, nullable=False)  # KDV oranı (%)
    profit_margin_value = Column(Numeric(5, 2), default=30.0, nullable=False)  # Kar marjı (%)
    
    # Stok bilgisi
    quantity = Column(Integer, default=0, nullable=False)
    unit = Column(String(20), default="adet", nullable=False)  # adet, kg, litre, vb.
    
    # Minimum stok seviyesi (uyarı için)
    min_stock_level = Column(Integer, default=5, nullable=False)
    
    # Statü
    is_active = Column(Boolean, default=True, nullable=False)
    
    # Relationships
    stock_movements = relationship("StockMovement", back_populates="product", lazy="select")
    sales = relationship("Sale", back_populates="product", lazy="select")
    recipe_items = relationship("Recipe", back_populates="product", lazy="select", cascade="all, delete-orphan")
    
    def __str__(self) -> str:
        """Ürün adını döndür"""
        return self.name
    
    @property
    def profit_margin(self) -> float:
        """
        Kar marjını döndür
        
        Returns:
            float: Kar marjı yüzdesi
        """
        return float(self.profit_margin_value)
    
    @property
    def is_low_stock(self) -> bool:
        """
        Stok düşük mü?
        
        Returns:
            bool: Stok minimum seviyenin altında mı?
        """
        return self.quantity <= self.min_stock_level
    
    def get_stock_status(self) -> str:
        """
        Stok durumunu metin olarak döndür
        
        Returns:
            str: Stok durumu ("OK", "DÜŞÜK", "TÜKENMİŞ")
        """
        if self.quantity == 0:
            return "TÜKENMİŞ"
        elif self.quantity <= self.min_stock_level:
            return "DÜŞÜK"
        else:
            return "OK"
    
    def add_stock(self, quantity: int, reason: str = "Manuel ekleme", db_session=None):
        """
        Stoğa ürün ekle
        
        Args:
            quantity: Eklenecek miktar
            reason: Ekleme sebebi
            db_session: Veritabanı oturumu (isteğe bağlı)
        """
        from src.models.stock_movement import StockMovement
        
        self.quantity += quantity
        
        if db_session:
            # Stok hareketini kaydet
            movement = StockMovement(
                product_id=self.id,
                movement_type="GİRİŞ",
                quantity=quantity,
                reason=reason
            )
            db_session.add(movement)
    
    def remove_stock(self, quantity: int, reason: str = "Satış", db_session=None) -> bool:
        """
        Stoktan ürün çıkar
        
        Args:
            quantity: Çıkarılacak miktar
            reason: Çıkarma sebebi
            db_session: Veritabanı oturumu (isteğe bağlı)
            
        Returns:
            bool: İşlem başarılı mı?
        """
        from src.models.stock_movement import StockMovement
        
        if self.quantity < quantity:
            return False  # Yeterli stok yok
        
        self.quantity -= quantity
        
        if db_session:
            # Stok hareketini kaydet
            movement = StockMovement(
                product_id=self.id,
                movement_type="ÇIKIŞ",
                quantity=quantity,
                reason=reason
            )
            db_session.add(movement)
        
        return True
