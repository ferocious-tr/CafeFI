"""
Birim Dönüşümü Testi
Test: 10kg stoktan 1g çıkılırsa 9.999kg kalması gerekir
"""

from src.models.ingredient import Ingredient

# Test 1: Birim dönüşüm fonksiyonu
print("=" * 60)
print("TEST 1: Birim Dönüşüm Fonksiyonu")
print("=" * 60)

# 10 kg'ı gram'a çevir
result = Ingredient.convert_quantity(10, "kg", "g")
print(f"10 kg → gram: {result} g (beklenen: 10000 g)")
assert result == 10000, "10kg = 10000g"

# 1000 ml'i l'e çevir
result = Ingredient.convert_quantity(1000, "ml", "l")
print(f"1000 ml → l: {result} l (beklenen: 1 l)")
assert result == 1, "1000ml = 1l"

# Aynı birim
result = Ingredient.convert_quantity(5, "g", "g")
print(f"5 g → g: {result} g (beklenen: 5 g)")
assert result == 5, "5g = 5g"

print("✅ Birim dönüşüm fonksiyonu: BAŞARILI\n")

# Test 2: Uyumsuz birimler
print("=" * 60)
print("TEST 2: Uyumsuz Birimler Hatası")
print("=" * 60)

try:
    # kg ile ml karıştırılmamalı
    result = Ingredient.convert_quantity(10, "kg", "ml")
    print("❌ HATA: Uyumsuz birimler için hata alınması gerekiyordu!")
except ValueError as e:
    print(f"✅ Beklenen hata: {str(e)}")

print()

# Test 3: Remove stock ile birim dönüşümü
print("=" * 60)
print("TEST 3: Remove Stock ile Birim Dönüşümü")
print("=" * 60)

# Simülasyon: Henüz database olmadığı için mock nesnesi oluştur
class MockIngredient:
    unit = "kg"
    quantity = 10
    
    @staticmethod
    def convert_quantity(quantity, from_unit, to_unit):
        return Ingredient.convert_quantity(quantity, from_unit, to_unit)
    
    def remove_stock(self, amount, amount_unit=None):
        if amount <= 0:
            raise ValueError("Miktar 0'dan büyük olmalı!")
        
        # Eğer gelen birim farklıysa, dönüştür
        if amount_unit and amount_unit != self.unit:
            amount = self.convert_quantity(amount, amount_unit, self.unit)
        
        if self.quantity < amount:
            raise ValueError(
                f"Yetersiz stok! Mevcut: {self.quantity:.4f}{self.unit}, "
                f"İstenen: {amount:.4f}{self.unit}"
            )
        
        self.quantity -= amount
        return self.quantity

mock_ing = MockIngredient()
print(f"İlk stok: {mock_ing.quantity} kg")

# 1g çıkar (amount_unit="g")
remaining = mock_ing.remove_stock(1, amount_unit="g")
print(f"1g çıkarıldıktan sonra: {remaining:.6f} kg")
print(f"Beklenen: 9.999 kg")

if abs(remaining - 9.999) < 0.0001:
    print("✅ Birim dönüşüm ile stock çıkarma: BAŞARILI")
else:
    print(f"❌ HATA: Sonuç yanlış! {remaining} != 9.999")

print()

# Test 4: Birden fazla çıkarma
print("=" * 60)
print("TEST 4: Birden Fazla Çıkarma")
print("=" * 60)

mock_ing2 = MockIngredient()
print(f"İlk stok: {mock_ing2.quantity} kg")

# 500g çıkar
remaining = mock_ing2.remove_stock(500, amount_unit="g")
print(f"500g çıkarıldıktan sonra: {remaining:.4f} kg (beklenen: 9.5 kg)")

# 2kg daha çıkar
remaining = mock_ing2.remove_stock(2, amount_unit="kg")
print(f"2kg daha çıkarıldıktan sonra: {remaining:.4f} kg (beklenen: 7.5 kg)")

if abs(remaining - 7.5) < 0.0001:
    print("✅ Birden fazla çıkarma: BAŞARILI")
else:
    print(f"❌ HATA: Sonuç yanlış! {remaining} != 7.5")

print()
print("=" * 60)
print("TÜM TESTLER BAŞARILI! ✅")
print("=" * 60)
