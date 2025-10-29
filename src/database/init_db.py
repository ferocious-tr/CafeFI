"""
🔧 CafeFlow - Veritabanı İnisiyalizasyonu

Veritabanı şemasını oluşturur ve varsayılan verilerle doldurur
"""

import logging
from src.database.db_connection import DatabaseEngine
from src.models import Base, Category, ExpenseCategory
from src.models.base import BaseModel

logger = logging.getLogger(__name__)


def init_database():
    """
    Veritabanı şemasını oluştur
    Tüm tabloları oluşturur
    """
    try:
        engine = DatabaseEngine.get_engine()
        
        # Tüm tabloları oluştur
        Base.metadata.create_all(bind=engine)
        logger.info("✓ Veritabanı şeması başarıyla oluşturuldu")
        
        return True
    except Exception as e:
        logger.error(f"✗ Veritabanı şeması oluşturulamadı: {str(e)}")
        return False


def populate_initial_data():
    """
    Veritabanını varsayılan verilerle doldur
    """
    try:
        db = DatabaseEngine.create_session()
        
        # Kategorileri oluştur
        logger.info("📝 Varsayılan kategoriler oluşturuluyor...")
        Category.create_default_categories(db)

        # Masraf kategorilerini oluştur
        logger.info("📝 Varsayılan masraf kategorileri oluşturuluyor...")
        _create_default_expense_categories(db)
        
        logger.info("✓ Varsayılan veriler başarıyla yüklendi")
        
        db.close()
        return True
    except Exception as e:
        logger.error(f"✗ Varsayılan veriler yüklenemedi: {str(e)}")
        return False


def _create_default_expense_categories(db):
    """Varsayılan masraf kategorilerini oluştur"""
    from src.models import Expense
    
    default_categories = [
        {"name": "Kira", "code": "KİRA", "description": "Dükkân kira giderleri", "order": 1},
        {"name": "Elektrik", "code": "ELEKTRİK", "description": "Elektrik faturası", "order": 2},
        {"name": "Su", "code": "SU", "description": "Su faturası", "order": 3},
        {"name": "Doğal Gaz", "code": "DOĞALGAZ", "description": "Doğal gaz faturası", "order": 4},
        {"name": "İnternet", "code": "İNTERNET", "description": "İnternet bağlantısı", "order": 5},
        {"name": "Telefon", "code": "TELEFON", "description": "Telefon hattı", "order": 6},
        {"name": "Malzemeleri", "code": "MALZEMELERİ", "description": "Gıda ve malzeme satın alımı", "order": 7},
        {"name": "Personeli", "code": "PERSONELİ", "description": "Personel ücretleri", "order": 8},
        {"name": "Pazarlama", "code": "MARKETİNG", "description": "Pazarlama ve reklam giderleri", "order": 9},
        {"name": "Sigorta", "code": "SİGORTA", "description": "Sigorta primleri", "order": 10},
        {"name": "Diğer", "code": "DİĞER", "description": "Diğer masraflar", "order": 11},
    ]
    
    for cat in default_categories:
        existing = db.query(ExpenseCategory).filter(ExpenseCategory.code == cat["code"]).first()
        if not existing:
            new_cat = ExpenseCategory(
                name=cat["name"],
                code=cat["code"],
                description=cat["description"],
                display_order=cat["order"],
                is_active=True
            )
            db.add(new_cat)
    
    db.commit()


def reset_database():
    """
    Veritabanını sıfırla (İçeriği sil, şemayı yeniden oluştur)
    ⚠️ UYARI: Tüm veriler silinecek!
    """
    try:
        engine = DatabaseEngine.get_engine()
        
        # Tüm tabloları sil
        Base.metadata.drop_all(bind=engine)
        logger.info("✓ Tüm tablolar silindi")
        
        # Şemayı yeniden oluştur
        init_database()
        
        # Varsayılan verilerle doldur
        populate_initial_data()
        
        logger.info("✓ Veritabanı başarıyla sıfırlandı")
        
        return True
    except Exception as e:
        logger.error(f"✗ Veritabanı sıfırlanırken hata: {str(e)}")
        return False


def get_database_info():
    """
    Veritabanı bilgilerini göster
    """
    from src.database.db_connection import DatabaseConfig
    
    info = {
        "database_type": DatabaseConfig.DB_TYPE,
        "database_url": DatabaseConfig.get_database_url().replace(
            DatabaseConfig.DB_PASSWORD, "****"
        ) if DatabaseConfig.DB_PASSWORD else DatabaseConfig.get_database_url(),
    }
    
    return info


if __name__ == "__main__":
    # Setup logging
    logging.basicConfig(level=logging.INFO)
    
    print("\n" + "="*60)
    print("🗄️  CafeFlow - Veritabanı İnisiyalizasyonu")
    print("="*60 + "\n")
    
    # Veritabanı bilgilerini göster
    info = get_database_info()
    print(f"📊 Veritabanı Bilgileri:")
    for key, value in info.items():
        print(f"   {key}: {value}")
    print()
    
    # Veritabanı bağlantısını test et
    from src.database.db_connection import DatabaseEngine
    print("🔗 Veritabanı bağlantısı test ediliyor...")
    if not DatabaseEngine.get_engine().connect():
        print("✗ Veritabanı bağlantısı başarısız!")
        exit(1)
    print("✓ Veritabanı bağlantısı başarılı!\n")
    
    # Veritabanı şemasını oluştur
    print("🔨 Veritabanı şeması oluşturuluyor...")
    if init_database():
        print("✓ Şema oluşturuldu\n")
        
        # Varsayılan verileri yükle
        print("📝 Varsayılan veriler yükleniyor...")
        if populate_initial_data():
            print("✓ Veriler yüklendi\n")
        else:
            print("⚠️  Varsayılan veriler yüklenemedi\n")
    else:
        print("✗ Şema oluşturulamadı\n")
    
    print("="*60)
    print("✓ İnisiyalizasyon tamamlandı!")
    print("="*60 + "\n")
