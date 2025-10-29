"""
Recipe Model - Reçete Yönetimi (Ürün - Malzeme İlişkisi)
"""

from sqlalchemy import Column, Integer, Float, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from src.models.base import BaseModel


class Recipe(BaseModel):
    """Reçete Modeli (Ürün + Malzeme)"""
    
    __tablename__ = "recipes"
    
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    ingredient_id = Column(Integer, ForeignKey("ingredients.id"), nullable=False)
    quantity = Column(Float, nullable=False)  # Malzeme miktarı
    unit = Column(String(20), nullable=False)  # g, ml, adet
    
    # İlişkiler (lazy loading için)
    product = relationship("Product", foreign_keys=[product_id])
    ingredient = relationship("Ingredient")
    
    def __repr__(self):
        return f"<Recipe(product_id={self.product_id}, ingredient_id={self.ingredient_id}, quantity={self.quantity}{self.unit})>"
    
    @property
    def ingredient_name(self):
        """Malzeme adını döndür"""
        return self.ingredient.name if self.ingredient else "N/A"
    
    @property
    def ingredient_cost(self):
        """Bu malzemenin toplam maliyetini hesapla"""
        if not self.ingredient:
            return 0
        return self.quantity * self.ingredient.cost_per_unit
    
    def get_ingredient_display(self):
        """Malzemeyi formatlanmış şekilde göster"""
        if self.ingredient:
            return f"{self.ingredient.name}: {self.quantity}{self.unit}"
        return f"Malzeme (ID: {self.ingredient_id}): {self.quantity}{self.unit}"
