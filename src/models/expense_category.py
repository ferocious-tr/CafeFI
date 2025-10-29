"""
🏷️ Masraf Kategori Modeli

Masraf kategorilerini veritabanında saklamak için ayrı model.
"""

from sqlalchemy import Column, String, Text, Integer, Boolean
from src.models.base import BaseModel


class ExpenseCategory(BaseModel):
    """Masraf kategorisi"""

    __tablename__ = "expense_categories"

    name = Column(String(100), unique=True, nullable=False, index=True)
    code = Column(String(50), unique=True, nullable=False, index=True)
    description = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    display_order = Column(Integer, default=0)

    def __str__(self) -> str:
        return self.name
