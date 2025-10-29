"""
🌱 CafeFlow - Test Verisi İçe Aktarma

Örnek malzeme, ürün ve reçete oluşturur
"""

from src.database import DatabaseEngine
from src.models import Ingredient, Product, Recipe
from decimal import Decimal
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


def populate_test_data():
    """Test verisi ekle"""
    
    db = DatabaseEngine.create_session()
    
    try:
        print("=" * 60)
        print("🌱 Test Verisi Yükleniyor...")
        print("=" * 60)
        
        # ============================================================
        # MALZEME VERİSİ
        # ============================================================
        
        ingredients_data = [
            ("Kahve Çekirdeği", "g", 0.05),
            ("Su", "ml", 0.001),
            ("Şeker", "g", 0.02),
            ("Süt", "ml", 0.015),
            ("Bardak", "adet", 0.25),
            ("Peçete", "adet", 0.05),
            ("Kakaopor", "g", 0.03),
            ("Bal", "g", 0.04),
            ("Limon", "g", 0.10),
            ("Çay", "g", 0.025),
        ]
        
        ingredients = {}
        
        for name, unit, cost in ingredients_data:
            existing = db.query(Ingredient).filter(Ingredient.name == name).first()
            if not existing:
                ing = Ingredient(
                    name=name,
                    unit=unit,
                    cost_per_unit=cost,
                    quantity=1000 if unit == "g" else 5000 if unit == "ml" else 100
                )
                db.add(ing)
                db.flush()
                ingredients[name] = ing
                print(f"✓ Malzeme: {name} ({unit}) - ₺{cost}")
            else:
                ingredients[name] = existing
        
        db.commit()
        
        # ============================================================
        # ÜRÜN VERİSİ
        # ============================================================
        
        # Kahve kategorisini al
        category = db.query(__import__('src.models', fromlist=['Category']).Category).filter_by(name="Sıcak İçecekler").first()
        
        if category:
            products_data = [
                ("Sade Kahve", "KAHVE-001", 30.0, 8.0, "İnce öğütülmüş sade kahve"),
                ("Tatlılı Kahve", "KAHVE-002", 35.0, 8.0, "Şekerli sade kahve"),
                ("Sütlü Kahve", "KAHVE-003", 40.0, 8.0, "Kahve + Süt karışımı"),
                ("Türk Çayı", "ÇAY-001", 15.0, 8.0, "Sıcak türk çayı"),
                ("Limonlu Çay", "ÇAY-002", 18.0, 8.0, "Çay + Limon"),
            ]
            
            products = {}
            
            for name, code, margin, kdv, desc in products_data:
                existing = db.query(Product).filter(Product.code == code).first()
                if not existing:
                    prod = Product(
                        name=name,
                        code=code,
                        category_id=category.id,
                        price=0,
                        quantity=100,
                        min_stock_level=10,
                        profit_margin_value=Decimal(str(margin)),
                        kdv_rate=Decimal(str(kdv)),
                        description=desc
                    )
                    db.add(prod)
                    db.flush()
                    products[name] = prod
                    print(f"✓ Ürün: {name} (Kar Marjı: %{margin}, KDV: %{kdv})")
                else:
                    products[name] = existing
            
            db.commit()
            
            # ============================================================
            # REÇETE VERİSİ
            # ============================================================
            
            recipes_data = [
                ("Sade Kahve", [
                    ("Kahve Çekirdeği", 7, "g"),
                    ("Su", 150, "ml"),
                    ("Bardak", 1, "adet"),
                ]),
                ("Tatlılı Kahve", [
                    ("Kahve Çekirdeği", 7, "g"),
                    ("Su", 150, "ml"),
                    ("Şeker", 5, "g"),
                    ("Bardak", 1, "adet"),
                ]),
                ("Sütlü Kahve", [
                    ("Kahve Çekirdeği", 5, "g"),
                    ("Su", 100, "ml"),
                    ("Süt", 100, "ml"),
                    ("Şeker", 3, "g"),
                    ("Bardak", 1, "adet"),
                ]),
                ("Türk Çayı", [
                    ("Çay", 3, "g"),
                    ("Su", 250, "ml"),
                    ("Bardak", 1, "adet"),
                ]),
                ("Limonlu Çay", [
                    ("Çay", 3, "g"),
                    ("Su", 250, "ml"),
                    ("Limon", 10, "g"),
                    ("Bardak", 1, "adet"),
                ]),
            ]
            
            for product_name, recipe_items in recipes_data:
                if products.get(product_name):
                    prod = products[product_name]
                    existing_recipes = db.query(Recipe).filter_by(product_id=prod.id).count()
                    
                    if existing_recipes == 0:
                        for ing_name, qty, unit in recipe_items:
                            if ingredients.get(ing_name):
                                recipe = Recipe(
                                    product_id=prod.id,
                                    ingredient_id=ingredients[ing_name].id,
                                    quantity=qty,
                                    unit=unit
                                )
                                db.add(recipe)
                        
                        db.commit()
                        print(f"✓ Reçete: {product_name}")
        
        print("=" * 60)
        print("✓ Test verisi başarıyla yüklendi!")
        print("=" * 60)
        
        return True
        
    except Exception as e:
        print(f"✗ Hata: {str(e)}")
        db.rollback()
        return False
    finally:
        db.close()


if __name__ == "__main__":
    populate_test_data()
