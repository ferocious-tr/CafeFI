# 🎯 AŞAMA 9 - Gelişmiş Raporlama Modülü
**Başlangıç Tarihi:** 28 Ekim 2025  
**Tahmini Bitiş:** 3-4 saat sonra  
**Durum:** 📋 Planlama Aşaması

---

## 📊 Aşama Özeti

### Hedef
Café yönetim sisteminize kapsamlı raporlama yetenekleri eklemek:
- 📈 Satış analitiği (Grafikler, Trendler)
- 🧂 Malzeme hareketleri raporları
- 💰 Masraf dağılımı ve Kâr/Zarar analizi
- 📊 KPI göstergeleri

### Başarı Kriterleri
- ✅ 4 ana rapor sekmesi (Tab)
- ✅ En az 10 adet grafik
- ✅ Tarih aralığı seçimi (date picker)
- ✅ Gerçek verilerle test
- ✅ Streamlit entegrasyonu

---

## 🔧 Teknik Yapı

### Yeni Dosyalar

#### **1. src/modules/reports.py** (YENİ - ~400-500 satır)

```python
"""
Raporlama Modülü - Satış, Masraf, Kâr Analitiği
"""

from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timedelta
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from decimal import Decimal

class ReportsManager:
    """Raporlama Yönetimi"""
    
    # SATIŞ ANALİTİĞİ
    @staticmethod
    def get_sales_trend(db: Session, days: int = 30):
        """Son N günün satış trendi"""
        # SQL: Günlük satışları al
        # Return: {date: total_sales, ...}
    
    @staticmethod
    def get_top_products(db: Session, limit: int = 10):
        """En çok satılan ürünler"""
        # SQL: Ürün ID'ye göre GROUP BY
        # Return: [(product_name, count, revenue), ...]
    
    @staticmethod
    def get_category_sales(db: Session):
        """Kategoriye göre satış dağılımı"""
        # SQL: Category JOIN Product JOIN Sale
        # Return: {category_name: total_sales, ...}
    
    @staticmethod
    def get_hourly_sales(db: Session, date=None):
        """Saatlik satış dağılımı"""
        # SQL: HOUR(created_at) GROUP BY
        # Return: {hour: sales_count, ...}
    
    # MASRAF ANALİTİĞİ
    @staticmethod
    def get_expense_breakdown(db: Session, days: int = 30):
        """Masraf kategorisine göre dağılım"""
        # SQL: ExpenseCategory JOIN Expense
        # Return: {category_name: total_amount, ...}
    
    @staticmethod
    def get_expense_trend(db: Session, days: int = 30):
        """Masraf trendi"""
        # SQL: Günlük masraflar
        # Return: {date: total_expenses, ...}
    
    # KÂR ANALİTİĞİ
    @staticmethod
    def get_profit_analysis(db: Session, days: int = 30):
        """Kâr/Zarar analizi"""
        # Hesaplama: Revenue - Total Costs
        # Return: {
        #     'total_revenue': X,
        #     'total_cost': Y,
        #     'gross_profit': Z,
        #     'profit_margin': %P
        # }
    
    @staticmethod
    def get_daily_profit(db: Session, days: int = 30):
        """Günlük kâr"""
        # SQL: Daily revenue - daily expenses
        # Return: {date: net_profit, ...}
    
    # STOK ANALİTİĞİ
    @staticmethod
    def get_stock_value(db: Session):
        """Toplam stok değeri"""
        # Hesaplama: ΣIngredient(quantity * cost_per_unit)
        # Return: {ingredient_name: total_value, ...}
    
    @staticmethod
    def get_low_stock_items(db: Session, threshold: float = 100):
        """Düşük stok malzemeleri"""
        # SQL: quantity < threshold
        # Return: [(name, current_qty, unit), ...]
    
    # GENEL METRİKLER
    @staticmethod
    def get_summary_metrics(db: Session, start_date, end_date):
        """Dönem özet metrikleri"""
        # Return: {
        #     'total_sales': int,
        #     'total_revenue': Decimal,
        #     'total_expenses': Decimal,
        #     'net_profit': Decimal,
        #     'avg_sale_value': Decimal
        # }
    
    @staticmethod
    def get_product_profitability(db: Session):
        """Ürün kârlılık analizi"""
        # Her ürün için: Revenue - Cost
        # Return: [(product_name, revenue, cost, profit, margin%), ...]
```

### Streamlit Sayfası

#### **File: src/app.py** (GÜNCELLENMESİ)

```python
# reports_page (Yeni sayfa)
st.set_page_config(
    page_title="📈 Raporlar",
    layout="wide"
)

# Sidebar: Tarih seçici
with st.sidebar:
    report_date_range = st.date_input(
        "Rapor Tarihi",
        value=(today - timedelta(30), today)
    )
```

#### **File: src/modules/reports_ui.py** (YENİ - ~300 satır)

Streamlit arayüzü:

```python
"""
Raporlama UI - Streamlit sayfası
"""

import streamlit as st
import matplotlib.pyplot as plt
import pandas as pd
from datetime import datetime, timedelta

def render_reports_page():
    """Raporlar sayfası"""
    
    st.title("📈 Raporlar & Analitiği")
    
    # ÜSTTE: Tarih Aralığı
    col1, col2, col3 = st.columns(3)
    with col1:
        start_date = st.date_input("Başlangıç Tarihi")
    with col2:
        end_date = st.date_input("Bitiş Tarihi")
    with col3:
        if st.button("🔄 Yenile"):
            st.rerun()
    
    # ALTINDA: 4 TAB
    tab1, tab2, tab3, tab4 = st.tabs([
        "📊 Satış Analitiği",
        "🧂 Malzeme Raporları", 
        "💰 Masraf & Kâr",
        "📈 Genel Metrikler"
    ])
    
    # TAB 1: SATIŞLAR
    with tab1:
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Satış Trendi (Son 30 gün)")
            # Matplotlib Grafik
            fig, ax = plt.subplots()
            # Data plotla
            st.pyplot(fig)
        
        with col2:
            st.subheader("En Çok Satılan Ürünler")
            # Bar chart
        
        # Altında: Kategori Pie Chart
        st.subheader("Kategoriye Göre Satışlar")
        col1, col2 = st.columns([1, 2])
        with col1:
            st.dataframe(category_data)
        with col2:
            # Pie Chart
    
    # TAB 2: MALZEME
    with tab2:
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Stok Değeri")
            st.metric("Toplam Stok Değeri", f"₺{total_value:.2f}")
            st.dataframe(stock_value_df)
        
        with col2:
            st.subheader("Düşük Stok Uyarıları ⚠️")
            st.dataframe(low_stock_df)
    
    # TAB 3: MASRAF & KÂR
    with tab3:
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Masraf Dağılımı")
            # Pie Chart
        
        with col2:
            st.subheader("Masraf Trendi")
            # Line Chart
        
        # Kâr Analizi
        st.divider()
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Toplam Gelir", revenue)
        with col2:
            st.metric("Toplam Masraf", expenses)
        with col3:
            st.metric("Brüt Kâr", gross_profit)
        with col4:
            st.metric("Kâr Marjı", f"{margin_pct}%")
    
    # TAB 4: METRIKLER
    with tab4:
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Toplam Satış", total_sales)
        with col2:
            st.metric("Ortalama Satış", avg_sale)
        with col3:
            st.metric("Toplam Müşteri", total_customers)
        with col4:
            st.metric("Satışı Ol. Ürün", active_products)
```

---

## 📋 Uygulama Adımları

### Step 1: ReportsManager Sınıfı (Veritabanı Sorguları)
1. `src/modules/reports.py` oluştur
2. 12 temel metodu yaz
3. Test verileri ile test et

### Step 2: Streamlit Arayüzü
1. `src/modules/reports_ui.py` oluştur
2. 4 tab strüktürü oluştur
3. Grafikler ekle (matplotlib)

### Step 3: Ana App Entegrationu
1. `src/app.py`'de "📈 Raporlar" sayfası ekle
2. Sidebar navigasyonuna ekle
3. Routing konfigür

### Step 4: Test & Düzeltme
1. Test verileri ile raporları kontrol
2. Grafikleri doğrula
3. Performance iyileştir

---

## 🎨 Grafik Tasarımları

### Tab 1: Satış Analitiği
```
┌────────────────────────────────────────────┐
│  📊 Satış Trendi (Son 30 gün)    │  Top 10  │
│  (Line Chart)                    │  (Bars)  │
├────────────────────────────────────────────┤
│      Kategoriye Göre Satışlar               │
│      (Pie Chart + Tablo)                    │
└────────────────────────────────────────────┘
```

### Tab 3: Masraf & Kâr
```
┌────────────────────────────────────────────┐
│ Masraf Dağılımı  │  Masraf Trendi (Line)   │
│ (Pie Chart)      │                        │
├────────────────────────────────────────────┤
│ 💰 Gelir   💸 Masraf   ✅ Brüt   📊 Marjı │
│ ₺15,000   ₺3,500      ₺11,500   76.7%    │
└────────────────────────────────────────────┘
```

---

## 📊 Test Verileri

Mevcut test verileri:
- 6 Ürün
- 11 Malzeme
- 19 Reçete
- Satış yapılabilir (test için)
- Masraflar mevcut

---

## ⏱️ Tahmini Zaman

| Görev | Süre |
|-------|------|
| ReportsManager kodlama | 60 dakika |
| Streamlit UI oluştur | 45 dakika |
| Grafikleri ekle | 45 dakika |
| Test & Debugging | 30 dakika |
| **TOPLAM** | **180 dakika (3 saat)** |

---

## 📝 Checklist

- [ ] ReportsManager.py oluştur
- [ ] 12 sorgu metodu yaz
- [ ] reports_ui.py oluştur
- [ ] 4 tab arayüzü tasarla
- [ ] Matplotlib grafikleri ekle
- [ ] Tarih seçici ekle
- [ ] Test verileri ile test
- [ ] app.py'ye entegre et
- [ ] Sidebar'a ekle
- [ ] Final teste tabi tut

---

## 🎯 Başarı Kriteri

✅ Tüm 4 sekmede grafikler çalışıyor  
✅ Tarih aralığı seçimi çalışıyor  
✅ Veriler doğru hesaplanıyor  
✅ Streamlit'te hata yok  
✅ Real-time veri güncellemesi çalışıyor  

**Başarıya Hazırız! 🚀**
