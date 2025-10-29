"""
🏷️ CafeFlow - Kategori Modeli

Ürün kategorileri (İçecekler, Yiyecekler, Atıştırmalıklar, vb.)
"""

from sqlalchemy import Column, String, Text, Integer, Boolean
from sqlalchemy.orm import relationship
from src.models.base import BaseModel


class Category(BaseModel):
    """
    Ürün Kategorisi Modeli
    
    Özellikler:
        - name: Kategori adı
        - description: Açıklama
        - code: Kategori kodu
        - is_active: Aktif mi?
    """
    
    __tablename__ = "categories"
    
    name = Column(String(100), unique=True, nullable=False, index=True)
    description = Column(Text, nullable=True)
    code = Column(String(10), unique=True, nullable=False, index=True)
    is_active = Column(Boolean, default=True, nullable=False)
    display_order = Column(Integer, default=0)
    
    # Relationship
    products = relationship("Product", back_populates="category", lazy="select")
    
    def __str__(self) -> str:
        """Kategori adını döndür"""
        return self.name
    
    @classmethod
    def create_default_categories(cls, db_session):
        """
        Varsayılan kategorileri oluştur
        
        Args:
            db_session: Veritabanı oturumu
        """
        default_categories = [
            {
                "name": "Sıcak İçecekler",
                "code": "HOT_DRINK",
                "description": "Kahve, çay, sıcak çikolata vb.",
                "display_order": 1
            },
            {
                "name": "Soğuk İçecekler",
                "code": "COLD_DRINK",
                "description": "Su, limonata, buzlu kahve vb.",
                "display_order": 2
            },
            {
                "name": "Pastalar",
                "code": "PASTRY",
                "description": "Pasta, kek, hamur işleri vb.",
                "display_order": 3
            },
            {
                "name": "Yemekler",
                "code": "FOOD",
                "description": "Savoury yemekler",
                "display_order": 4
            },
            {
                "name": "Atıştırmalıklar",
                "code": "SNACK",
                "description": "Bisküvi, çips, kuruyemiş vb.",
                "display_order": 5
            },
        ]
        
        for cat_data in default_categories:
            # Zaten var mı kontrol et
            existing = db_session.query(cls).filter_by(code=cat_data["code"]).first()
            if not existing:
                category = cls(**cat_data)
                db_session.add(category)
        
        db_session.commit()
