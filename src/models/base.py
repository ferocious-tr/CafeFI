"""
🗄️ CafeFlow - Temel Model

Tüm veritabanı modelleri için temel sınıf.
Ortak alanları (id, created_at, updated_at) ve metotları içerir.
"""

from datetime import datetime
from sqlalchemy import Column, Integer, DateTime, String, func
from sqlalchemy.orm import declarative_base
from typing import Any

# Tüm modeller için temel sınıf
Base = declarative_base()


class BaseModel(Base):
    """
    Tüm veritabanı modelleri için temel sınıf
    
    Ortak alanlar:
        - id: Birincil anahtar
        - created_at: Oluşturulma tarihi
        - updated_at: Son güncellenme tarihi
    """
    
    __abstract__ = True
    
    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
        server_default=func.now()
    )
    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
        server_default=func.now()
    )
    
    def __repr__(self) -> str:
        """Nesne temsili"""
        attrs = ", ".join(
            f"{col.name}={getattr(self, col.name)!r}"
            for col in self.__table__.columns
        )
        return f"<{self.__class__.__name__}({attrs})>"
    
    def to_dict(self) -> dict:
        """
        Modeli sözlüğe dönüştür
        
        Returns:
            dict: Nesnenin sözlük gösterimi
        """
        result = {}
        for col in self.__table__.columns:
            value = getattr(self, col.name)
            
            # DateTime nesnelerini ISO formatına dönüştür
            if isinstance(value, datetime):
                value = value.isoformat()
            
            result[col.name] = value
        
        return result
    
    def update(self, **kwargs) -> None:
        """
        Modeli güncelle
        
        Args:
            **kwargs: Güncellenecek alanlar
            
        Örnek:
            user.update(name="Yeni İsim", email="yeni@email.com")
        """
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
