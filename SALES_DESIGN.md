# 📋 Satış Modülü - Tasarım Dökümanı

**Tarih:** 28 Ekim 2025  
**Versiyon:** 1.0  
**Durum:** 📐 Tasarım Onaylandı

---

## 🎯 Genel Mimarı

```
MALZEME (Ingredients)
├─ ID, Adı, Birim (g, ml, adet)
├─ Maliyet (birim başına)
├─ Stok (miktar)
└─ Hareketler (GİRİŞ/ÇIKIŞ)

↓↓↓ (REÇETE BAĞLANTISI) ↓↓↓

ÜRÜN (Products) 
├─ ID, Adı, Açıklama
├─ Malzeme Listesi (reçete)
│  └─ Malzeme_ID: Miktar (gr/ml/adet)
├─ AYARLAR:
│  ├─ KDV Oranı (%)
│  ├─ Kar Marjı (%)
│  └─ Satış Fiyatı (elle editlenebilir)
├─ HESAPLAMALAR (OTOMATİK):
│  ├─ Toplam Malzeme Maliyeti = Σ(Malzeme Maliyet)
│  ├─ Satış Fiyatı = (Maliyet / (1 - Kar Marjı%)) * (1 + KDV%)
│  ├─ KDV Tutarı = Satış Fiyatı * KDV%
│  └─ Net Kâr = Satış Fiyatı - KDV - Maliyet
└─ Stok (adet)

↓↓↓ (SATIŞTA) ↓↓↓

SATIŞLAR (Sales)
├─ ID, Tarih
├─ Ürün_ID, Miktar
├─ Fiyat Hesaplaması:
│  ├─ Satış Fiyatı (KDV hariç)
│  ├─ KDV Tutarı
│  ├─ Toplam (KDV dahil)
│  ├─ Ürün Maliyeti
│  ├─ Brüt Kâr (KDV hariç)
│  └─ Net Kâr (KDV dahil)
├─ Ödeme Yöntemi
└─ Not

↓↓↓ (STOk DÜŞMESI) ↓↓↓

STOK HAREKETLERI (Stock Movements)
├─ Malzeme_ID (ÇIKIŞ)
├─ Miktar (Reçete * Satış Miktarı)
├─ Referans (Sale_ID)
└─ Tarih
```

---

## 📊 Veritabanı Şeması (YENİ)

### **1. Recipe Tablosu** (YENI)
```sql
recipes (
    id INTEGER PRIMARY KEY
    product_id FOREIGN KEY (products.id)
    ingredient_id FOREIGN KEY (products/ingredients) -- malzeme
    quantity DECIMAL -- gr, ml, adet
    unit VARCHAR -- "g", "ml", "adet"
    created_at TIMESTAMP
)
```

### **2. Products Tablosu** (GÜNCELLENECEK)
```sql
products (
    -- Mevcut alanlar...
    
    -- YENİ ALANLAR:
    kdv_rate DECIMAL DEFAULT 0.08  -- %8
    profit_margin DECIMAL DEFAULT 0.30  -- %30
    recipe_id FOREIGN KEY (recipes.id)  -- Ana reçete
    
    -- HESAPLANAN ALANLAR (view veya property):
    total_ingredient_cost DECIMAL  -- Σ malzeme maliyeti
    sale_price DECIMAL  -- Elle editlenebilir
    kdv_amount DECIMAL  -- Otomatik
    gross_profit DECIMAL  -- Otomatik
)
```

### **3. Ingredients Tablosu** (YENI)
```sql
ingredients (
    id INTEGER PRIMARY KEY
    name VARCHAR UNIQUE
    unit VARCHAR  -- "g", "ml", "adet"
    cost_per_unit DECIMAL
    quantity INTEGER  -- Mevcut stok
    is_active BOOLEAN
    created_at TIMESTAMP
    updated_at TIMESTAMP
)
```

### **4. Sales Tablosu** (GÜNCELLENECEK)
```sql
sales (
    id INTEGER PRIMARY KEY
    sale_number VARCHAR UNIQUE
    product_id FOREIGN KEY (products.id)
    quantity INTEGER
    
    -- FİYAT ALANLAR:
    sale_price DECIMAL  -- KDV hariç
    kdv_rate DECIMAL
    kdv_amount DECIMAL
    total_price DECIMAL  -- KDV dahil
    product_cost DECIMAL
    gross_profit DECIMAL  -- Fiyat - Maliyet
    net_profit DECIMAL  -- Gross - KDV
    
    payment_method VARCHAR
    notes TEXT
    created_at TIMESTAMP
)
```

---

## 🧮 Fiyatlandırma Formülleri

### **Ürün Ana Verilerinde:**
```
1. Malzeme Maliyeti (Otomatik):
   Total Cost = Σ(Ingredient_Cost * Recipe_Quantity)

2. KDV Hariç Satış Fiyatı:
   Sale_Price = Total_Cost / (1 - Profit_Margin%)
   
   Örnek:
   Total_Cost = ₺10
   Profit_Margin = %30
   Sale_Price = 10 / (1 - 0.30) = 10 / 0.70 = ₺14.29

3. KDV Tutarı:
   KDV_Amount = Sale_Price * KDV_Rate%
   
   Örnek:
   Sale_Price = ₺14.29
   KDV_Rate = %8
   KDV_Amount = 14.29 * 0.08 = ₺1.14

4. Toplam (KDV dahil):
   Total = Sale_Price + KDV_Amount
   = ₺14.29 + ₺1.14 = ₺15.43
```

### **Satış İşleminde:**
```
1. Ürün seçildi → Fiyatlar otomatik çekiliyor
2. Ödeme hesaplaması:
   ├─ KDV Hariç: ₺14.29
   ├─ KDV: ₺1.14
   └─ Toplam: ₺15.43

3. Kâr Analizi:
   ├─ Brüt Kâr (KDV hariç): ₺14.29 - ₺10 = ₺4.29
   ├─ KDV Tutarı: ₺1.14
   └─ Net Kâr (KDV dahil): ₺4.29 - ₺1.14 = ₺3.15
```

---

## 📱 Streamlit UI - 5 TAB

### **TAB 1: Hızlı Satış (POS Form)**
```
┌─────────────────────────────────────┐
│  Satış Yap                          │
├─────────────────────────────────────┤
│                                     │
│  Ürün Seçimi:                       │
│  [Dropdown: Sade Kahve ▼]           │
│  Miktar: [3] adet                   │
│                                     │
│  ─────────────────────────────────  │
│  FİYAT BİLGİSİ:                     │
│  Ürün Maliyeti:    ₺30.00           │
│  Satış Fiyatı:     ₺42.87 (KDV -)  │
│  KDV (%8):         ₺3.43            │
│  Toplam (KDV +):   ₺46.30           │
│  ─────────────────────────────────  │
│  Net Kâr:          ₺9.45            │
│                                     │
│  Ödeme Yöntemi: [Nakit ▼]           │
│                                     │
│  Not: [________________]            │
│                                     │
│  [💾 Satışı Kaydet] [❌ İptal]     │
│                                     │
└─────────────────────────────────────┘
```

### **TAB 2: Satış Geçmişi**
```
Tarih Filtresi:    [📅 Bugün ▼]
Ödeme Filtresi:    [Tümü ▼]
Arama:             [__________]

┌──────────────────────────────────────────────────────┐
│ Tarih    │ Ürün        │ Miktar │ Tutar   │ Ödeme  │
├──────────────────────────────────────────────────────┤
│ 10:30    │ Sade Kahve  │ 2      │ ₺30.86  │ Nakit  │
│ 10:45    │ Tatlılı K.  │ 1      │ ₺25.43  │ Kart   │
│ 11:00    │ Çay         │ 3      │ ₺18.21  │ Nakit  │
└──────────────────────────────────────────────────────┘

Seçilen Satış Detayları:
├─ Ürün: Sade Kahve
├─ Miktar: 2
├─ Malzeme Maliyeti: ₺20.00
├─ Satış Fiyatı: ₺28.57
├─ KDV: ₺2.29
├─ Toplam: ₺30.86
├─ Brüt Kâr: ₺8.57
└─ Net Kâr: ₺6.28
```

### **TAB 3: Ürün Yönetimi**
```
┌─ Yeni Ürün Ekle ─────────────────────┐
│                                      │
│ Ürün Adı:        [_________________] │
│ Açıklama:        [_________________] │
│                                      │
│ KDV Oranı (%):   [8]                │
│ Kar Marjı (%):   [30]               │
│                                      │
│ Reçete Ekle:                         │
│ ┌─────────────────────────────────┐ │
│ │ Malzeme    │ Miktar │ Birim    │ │
│ ├─────────────────────────────────┤ │
│ │ Kahve      │ [50]   │ [g ▼]    │ │
│ │ Su         │ [150]  │ [ml ▼]   │ │
│ │ Şeker      │ [10]   │ [g ▼]    │ │
│ │ [+ Ekle]                       │ │
│ └─────────────────────────────────┘ │
│                                      │
│ [💾 Kaydet] [❌ İptal]              │
│                                      │
└──────────────────────────────────────┘

Mevcut Ürünler:
┌──────────────────────────────────────┐
│ Ürün        │ Maliyeti │ Fiyatı │ St│
├──────────────────────────────────────┤
│ Sade Kahve  │ ₺10.00   │ ₺15.43 │25 │
│ Tatlılı K.  │ ₺15.00   │ ₺21.87 │15 │
└──────────────────────────────────────┘
```

### **TAB 4: Malzeme Yönetimi**
```
Yeni Malzeme Ekle:
├─ Adı:          [__________________]
├─ Birim:        [g/ml/adet ▼]
├─ Maliyet:      [________]  ₺/birim
└─ Stok:         [________]  (miktar)
    [✓ Ekle]

Mevcut Malzemeler:
┌──────────────────────────────────────┐
│ Malzeme    │ Stok  │ Birim │ Maliyet│
├──────────────────────────────────────┤
│ Kahve      │ 5000  │ g     │ ₺0.10  │
│ Su         │ 20000 │ ml    │ ₺0.01  │
│ Şeker      │ 3000  │ g     │ ₺0.02  │
│ Bardak     │ 500   │ adet  │ ₺0.50  │
└──────────────────────────────────────┘
```

### **TAB 5: Raporlar**
```
📊 Satış Raporları
Tarih Aralığı: [📅 Bugün ▼] [📅 ... ▼]

┌─ SATIŞLAR ─────────────────────────────┐
│ Toplam Satış:        ₺1,500.00         │
│ Toplam KDV:          ₺120.00           │
│ Ortalama Tutar:      ₺50.00            │
│ Satış Adedi:         30                │
└─────────────────────────────────────────┘

┌─ KÂR ANALİZİ ─────────────────────────┐
│ Toplam Maliyet:      ₺900.00           │
│ Toplam Gelir:        ₺1,500.00         │
│ Brüt Kâr:            ₺600.00           │
│ KDV Tutarı:          ₺120.00           │
│ Net Kâr:             ₺480.00           │
└─────────────────────────────────────────┘

📦 MALZEME HAREKETLERI:
┌──────────────────────────────────────┐
│ Tarih    │ Malzeme │ Çıkış  │ Ref   │
├──────────────────────────────────────┤
│ 10:30    │ Kahve   │ 50g    │ Sat-1 │
│ 10:45    │ Su      │ 150ml  │ Sat-1 │
│ 11:00    │ Şeker   │ 10g    │ Sat-1 │
└──────────────────────────────────────┘

📈 ÜRÜN SATIŞLARI:
┌──────────────────────────────────────┐
│ Ürün        │ Adet │ Tutar    │ Kâr  │
├──────────────────────────────────────┤
│ Sade Kahve  │ 15   │ ₺231.45  │ ₺94.5│
│ Tatlılı K.  │ 10   │ ₺218.70  │ ₺63.0│
│ Çay         │ 5    │ ₺91.05   │ ₺18.6│
└──────────────────────────────────────┘
```

---

## 🔧 Python Kod Yapısı

### **SalesManager Sınıfı - 15+ Metod**

```python
class SalesManager:
    # ÜRÜN YÖNETİMİ
    - create_product(name, kdv_rate, profit_margin)
    - get_product(product_id)
    - update_product_price(product_id, sale_price)  # Elle editlenebilir
    - get_all_products()
    
    # REÇETE YÖNETİMİ
    - add_recipe_item(product_id, ingredient_id, quantity, unit)
    - calculate_product_cost(product_id)  # Toplam malzeme maliyeti
    - get_recipe(product_id)
    
    # MALZEME YÖNETİMİ
    - create_ingredient(name, unit, cost_per_unit, quantity)
    - update_ingredient_stock(ingredient_id, quantity_change)
    - get_all_ingredients()
    
    # SATIŞLAR
    - create_sale(product_id, quantity, payment_method, notes)
        → Stok kontrol
        → Fiyat hesaplama
        → Malzeme hareketleri
    - get_sales_by_period(start_date, end_date)
    - get_sales_by_product(product_id)
    
    # FİYAT HESAPLAMA
    - calculate_sale_price(product_id, quantity)
        → Malzeme maliyeti
        → KDV hesaplama
        → Kâr hesaplama
    
    # RAPORLAR
    - get_sales_report(start_date, end_date)
    - get_ingredient_movements(start_date, end_date)
    - get_profit_analysis(start_date, end_date)
    - get_product_sales_summary(start_date, end_date)
```

---

## 📋 İş Akışı (Step by Step)

### **Satış Yapma:**
```
1. [TAB 1] Ürün seç (Sade Kahve)
   ↓
2. Ürün bilgilerini yükle:
   - Product_ID, KDV, Kar Marjı
   - Reçete (Kahve 50g, Su 150ml, Şeker 10g)
   - Malzeme maliyetleri (Kahve ₺5, Su ₺1.50, Şeker ₺0.20)
   ↓
3. Toplam malzeme maliyeti hesapla: ₺6.70
   ↓
4. Satış fiyatını hesapla:
   - KDV hariç: 6.70 / (1-0.30) = ₺9.57
   - KDV: 9.57 * 0.08 = ₺0.77
   - Toplam: ₺10.34
   ↓
5. Miktar gir (2 adet)
   - Toplam tutar: ₺10.34 * 2 = ₺20.68
   ↓
6. Ödeme yöntemi seç (Nakit)
   ↓
7. [Kaydet] butonuna tıkla
   ↓
8. OTOMATIK YAPILACAK İŞLEMLER:
   a) Sale kaydı oluştur
   b) Ürün stok düş (Product.quantity -= 2)
   c) Malzeme stok düş:
      - Kahve: -100g
      - Su: -300ml
      - Şeker: -20g
   d) Stok hareketi kayıt:
      - Type: ÇIKIŞ
      - Reference: Sale_ID
   ↓
9. Başarı mesajı: "✓ Satış kaydedildi!"
```

### **Malzeme Stok Kontrolü:**
```
Satış öncesi check:
├─ Ürün stoku var mı? (quantity >= request)
│  └─ HAYIR → "❌ Stok yok, satış yapılamaz"
│
└─ Malzeme stokları var mı?
   ├─ Kahve 100g var mı?
   ├─ Su 300ml var mı?
   ├─ Şeker 20g var mı?
   └─ Birisi eksik → "❌ Malzeme yetersiz"
```

---

## 🗄️ Yeni Veritabanı Tabloları

1. **ingredients** (YENI)
2. **recipes** (YENI)  
3. **products** (GÜNCELLENECEK - kdv_rate, profit_margin, recipe_id ekle)
4. **sales** (GÜNCELLENECEK - fiyat alanlarını ekle)

---

## ✅ Checklist

- [ ] `Ingredient` ORM modeli oluştur
- [ ] `Recipe` ORM modeli oluştur
- [ ] `Product` modelini güncelle
- [ ] `Sale` modelini güncelle
- [ ] `src/modules/sales.py` oluştur
- [ ] `render_sales_page()` (5 Tab UI)
- [ ] Test verilerini ekle
- [ ] Raporları test et

---

**Status: ✅ ONAYLANDI - Kod yazımına hazırım!**
