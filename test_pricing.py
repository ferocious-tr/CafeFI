import sys
sys.stdout.reconfigure(encoding='utf-8')
from src.database import DatabaseEngine
from src.modules.sales import SalesManager

db = DatabaseEngine.create_session()

# Kahvelerden biri seçelim
from src.models import Product
products = db.query(Product).all()
print(f'Ürün sayısı: {len(products)}')

# Sade kahve satışı test et
sade_kahve = next((p for p in products if p.name == 'Sade Kahve'), None)
if sade_kahve:
    print(f'\nÜrün bulundu: {sade_kahve.name}')
    print(f'Kar Marjı: %{sade_kahve.profit_margin}')
    print(f'KDV: %{sade_kahve.kdv_rate}')
    
    # Fiyat hesapla
    price = SalesManager.calculate_sale_price(db, sade_kahve.id, 1)
    print(f'\nFiyatlandırma:')
    print(f'  Malzeme Maliyeti: {price["ingredient_cost"]:.2f} TL')
    print(f'  Satış Fiyatı (KDV-): {price["sale_price_without_kdv"]:.2f} TL')
    print(f'  KDV (%8): {price["kdv_amount"]:.2f} TL')
    print(f'  Toplam (KDV+): {price["total_with_kdv"]:.2f} TL')
    print(f'\nKâr Analizi:')
    print(f'  Brüt Kar: {price["gross_profit"]:.2f} TL')
    print(f'  Net Kar: {price["net_profit"]:.2f} TL')
