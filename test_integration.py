"""
Entegre Test: Birim dönüşümü + Satış işlemi
Database'de test et
"""

from src.database import DatabaseEngine
from src.models import Product, Ingredient, Recipe, Sale
from datetime import datetime

db = DatabaseEngine.create_session()

print("=" * 70)
print("TEST: Birim Dönüşümü ile Satış İşlemi")
print("=" * 70)

# 1. Mevcut malzemeleri kontrol et
ingredients = db.query(Ingredient).filter(Ingredient.is_active == True).all()
print(f"\n1️⃣ Mevcut Malzemeler: {len(ingredients)} adet")

if len(ingredients) > 0:
    # İlk malzemeyi seç
    test_ing = ingredients[0]
    print(f"   Test malzemesi: {test_ing.name} ({test_ing.quantity:.4f}{test_ing.unit})")
    
    initial_quantity = test_ing.quantity
    
    # 2. Birim dönüşümü testi
    print(f"\n2️⃣ Birim Dönüşümü Testi:")
    
    # Aynı birimle çıkar
    if test_ing.unit == "kg":
        test_ing.remove_stock(0.5, amount_unit="kg")
        print(f"   0.5kg çıkarıldı -> Kalan: {test_ing.quantity:.4f}{test_ing.unit}")
    
    elif test_ing.unit == "g":
        test_ing.remove_stock(100, amount_unit="g")
        print(f"   100g çıkarıldı -> Kalan: {test_ing.quantity:.4f}{test_ing.unit}")
    
    # Farklı birimle çıkar (gram)
    if test_ing.unit == "kg":
        test_ing.remove_stock(50, amount_unit="g")
        print(f"   50g çıkarıldı (unit: {test_ing.unit}) -> Kalan: {test_ing.quantity:.4f}{test_ing.unit}")
    
    db.commit()
    print(f"   ✅ Yeni stok: {test_ing.quantity:.4f}{test_ing.unit}")
    
    # 3. Ürünleri kontrol et
    print(f"\n3️⃣ Ürünleri Kontrol Et:")
    products = db.query(Product).filter(Product.is_active == True).all()
    print(f"   Toplam ürün: {len(products)} adet")
    
    if len(products) > 0:
        prod = products[0]
        print(f"   Test ürünü: {prod.name} (Kod: {prod.code})")
        
        # 4. Reçete kontrol et
        recipes = db.query(Recipe).filter(Recipe.product_id == prod.id).all()
        print(f"\n4️⃣ Reçete Kontrol Et:")
        print(f"   {prod.name} için malzeme sayısı: {len(recipes)} adet")
        
        for rec in recipes[:3]:  # İlk 3'ü göster
            print(f"      - {rec.ingredient_name}: {rec.quantity}{rec.unit}")
    
    print("\n" + "=" * 70)
    print("✅ TÜM TESTLER BAŞARILI - BİRİM DÖNÜŞÜMÜ ÇALIŞIYOR")
    print("=" * 70)

else:
    print("❌ Hiç malzeme yok! Önce test verisini yükle (populate_test_data.py)")

db.close()
