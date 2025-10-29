"""
🗄️ CafeFlow - Veritabanı Bağlantı Modülü

Bu modül SQLite/PostgreSQL veritabanı ile bağlantı kurmayı ve
ORM (SQLAlchemy) operasyonlarını yönetir.
"""

import os
from typing import Generator
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool
from dotenv import load_dotenv
import logging

# .env dosyasını yükle
load_dotenv()

# Logger ayarla
logger = logging.getLogger(__name__)


class DatabaseConfig:
    """Veritabanı konfigürasyonu"""
    
    DB_TYPE = os.getenv("DB_TYPE", "sqlite")
    DB_NAME = os.getenv("DB_NAME", "data/cafeflow.db")
    DB_USER = os.getenv("DB_USER", "cafeflow")
    DB_PASSWORD = os.getenv("DB_PASSWORD", "password")
    DB_HOST = os.getenv("DB_HOST", "localhost")
    DB_PORT = os.getenv("DB_PORT", "5432")
    
    @staticmethod
    def get_database_url():
        """
        Veritabanı URL'sini döndür
        
        Returns:
            str: SQLAlchemy veritabanı URL'si
        """
        if DatabaseConfig.DB_TYPE == "sqlite":
            return f"sqlite:///{DatabaseConfig.DB_NAME}"
        elif DatabaseConfig.DB_TYPE == "postgresql":
            return (
                f"postgresql://{DatabaseConfig.DB_USER}:"
                f"{DatabaseConfig.DB_PASSWORD}@"
                f"{DatabaseConfig.DB_HOST}:{DatabaseConfig.DB_PORT}/"
                f"{DatabaseConfig.DB_NAME}"
            )
        else:
            raise ValueError(
                f"Bilinmeyen veritabanı tipi: {DatabaseConfig.DB_TYPE}"
            )


class DatabaseEngine:
    """Veritabanı engine yönetimi"""
    
    _engine = None
    _SessionLocal = None
    
    @classmethod
    def get_engine(cls):
        """
        SQLAlchemy engine'i al veya oluştur
        
        Returns:
            Engine: SQLAlchemy Engine nesnesi
        """
        if cls._engine is None:
            db_url = DatabaseConfig.get_database_url()
            
            # SQLite için özel ayarlar
            if DatabaseConfig.DB_TYPE == "sqlite":
                cls._engine = create_engine(
                    db_url,
                    connect_args={"check_same_thread": False},
                    poolclass=StaticPool,
                    echo=False  # SQL sorgularını yazdırmak için True yap
                )
                
                # SQLite'ta foreign key desteğini etkinleştir
                @event.listens_for(cls._engine, "connect")
                def set_sqlite_pragma(dbapi_conn, connection_record):
                    cursor = dbapi_conn.cursor()
                    cursor.execute("PRAGMA foreign_keys=ON")
                    cursor.close()
            else:
                # PostgreSQL için ayarlar
                cls._engine = create_engine(
                    db_url,
                    pool_pre_ping=True,
                    pool_size=5,
                    max_overflow=10
                )
            
            logger.info(f"✓ Veritabanı engine oluşturuldu: {DatabaseConfig.DB_TYPE}")
        
        return cls._engine
    
    @classmethod
    def get_session_factory(cls):
        """
        Oturum fabrikası al
        
        Returns:
            sessionmaker: SQLAlchemy sessionmaker nesnesi
        """
        if cls._SessionLocal is None:
            engine = cls.get_engine()
            cls._SessionLocal = sessionmaker(
                autocommit=False,
                autoflush=False,
                bind=engine
            )
        
        return cls._SessionLocal
    
    @classmethod
    def get_session(cls) -> Generator[Session, None, None]:
        """
        Yeni bir veritabanı oturumu al
        
        Returns:
            Generator[Session, None, None]: Veritabanı oturumu
            
        Yields:
            Session: Veritabanı oturumu
        """
        SessionLocal = cls.get_session_factory()
        db = SessionLocal()
        try:
            yield db
        finally:
            db.close()
    
    @classmethod
    def create_session(cls) -> Session:
        """
        Yeni bir oturum oluştur (context manager olmadan)
        
        Returns:
            Session: SQLAlchemy Session nesnesi
        """
        SessionLocal = cls.get_session_factory()
        return SessionLocal()
    
    @classmethod
    def dispose(cls):
        """Veritabanı bağlantılarını kapat"""
        if cls._engine is not None:
            cls._engine.dispose()
            cls._engine = None
            cls._SessionLocal = None
            logger.info("✓ Veritabanı bağlantıları kapatıldı")


def get_db() -> Generator[Session, None, None]:
    """
    Veritabanı oturumu almak için dependency injection
    
    Örnek kullanım (FastAPI/Streamlit):
        db = next(get_db())
        users = db.query(User).all()
    
    Yields:
        Session: Veritabanı oturumu
    """
    yield from DatabaseEngine.get_session()


# Test fonksiyonu
def test_connection():
    """Veritabanı bağlantısını test et"""
    try:
        engine = DatabaseEngine.get_engine()
        with engine.connect() as connection:
            logger.info("✓ Veritabanı bağlantısı başarılı!")
            
            # SQLite için bilgi al
            if DatabaseConfig.DB_TYPE == "sqlite":
                result = connection.execute(
                    "SELECT sqlite_version()"
                )
                version = result.fetchone()[0]
                logger.info(f"✓ SQLite Sürümü: {version}")
            
            return True
    except Exception as e:
        logger.error(f"✗ Veritabanı bağlantı hatası: {str(e)}")
        return False


if __name__ == "__main__":
    # Test et
    logging.basicConfig(level=logging.INFO)
    test_connection()
