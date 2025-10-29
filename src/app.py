"""
☕ CafeFlow - Ana Streamlit Uygulaması

Cafe Muhasebe ve Operasyon Yönetim Sistemi
"""

import streamlit as st
import sys
from datetime import datetime
from pathlib import Path

# Proje kök dizinini Python path'ine ekle
project_root = Path(__file__).parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

# İçeri aktarmalar
from src.database import DatabaseEngine, init_database, populate_initial_data
from src.models import Category, Product, Sale, Expense, StockMovement, ExpenseCategory
from src.modules.inventory import render_inventory_page
from src.modules.expenses import render_expenses_page
from src.modules.sales import render_sales_page
from src.modules.reports_ui import render_reports_page
from src.modules.settings import render_settings_page
from src.utils.locale_utils import format_currency, format_datetime, format_date, format_time
from src.config.locale_config import configure_tr_locale, log_locale_info


# ============================================================
# LOCALE CONFIGURATION
# ============================================================

# Türkiye locale ayarlarını yapılandır
configure_tr_locale()

st.set_page_config(
    page_title="CafeFlow - Cafe Muhasebe Sistemi",
    page_icon="☕",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS özelleştirmesi
st.markdown("""
<style>
    [data-testid="stMetricValue"] {
        font-size: 2rem;
        color: #000000;
    }
    [data-testid="stMetricLabel"] {
        color: #000000;
    }
    .stMetric {
        background-color: #f0f2f6;
        padding: 1.5rem;
        border-radius: 0.5rem;
    }
</style>
""", unsafe_allow_html=True)


# ============================================================
# SESSION STATE INITIALIZATION
# ============================================================

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = ""


@st.cache_resource
def init_app():
    """Uygulamayı başlat"""
    # Veritabanını kontrol et ve başlat
    if not init_database():
        st.error("Veritabanı başlatılamadı!")
        return False
    
    return True


# ============================================================
# LOGIN PAGE
# ============================================================

def page_login():
    """Giriş sayfası"""
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("<h1 style='text-align: center'>☕ CafeFlow</h1>", unsafe_allow_html=True)
        st.markdown("<h3 style='text-align: center; color: #666'>Cafe Muhasebe Sistemi</h3>", unsafe_allow_html=True)
        
        st.markdown("---")
        
        st.subheader("🔐 Giriş Yap")
        
        with st.form("login_form"):
            username = st.text_input("Kullanıcı Adı", placeholder="admin")
            password = st.text_input("Şifre", type="password", placeholder="••••••••")
            
            submit = st.form_submit_button("🔓 Giriş Yap", use_container_width=True)
            
            if submit:
                if username == "admin" and password == "admin123":
                    st.session_state.logged_in = True
                    st.session_state.username = username
                    st.success("✓ Hoş geldiniz!")
                    st.rerun()
                else:
                    st.error("✗ Kullanıcı adı veya şifre yanlış!")


# ============================================================
# SIDEBAR NAVIGATION
# ============================================================

def render_sidebar():
    """Sidebar navigasyonunu oluştur"""
    st.sidebar.title("☕ CafeFlow")
    st.sidebar.markdown("---")
    
    pages = {
        "📊 Dashboard": "dashboard",
        "🏪 Satış İşlemleri": "sales",
        "📦 Malzeme/Ürün Yönetimi": "inventory",
        "💰 Masraf Takibi": "expenses",
        "📈 Raporlar": "reports",
        "⚙️ Ayarlar": "settings",
    }
    
    selected_page = st.sidebar.radio(
        "Menü",
        list(pages.keys()),
        label_visibility="collapsed"
    )
    
    st.sidebar.markdown("---")
    
    # Kullanıcı Bilgisi
    st.sidebar.subheader("👤 Kullanıcı")
    st.sidebar.text(f"Kullanıcı: {st.session_state.username}")
    
    if st.sidebar.button("🚪 Çıkış Yap", use_container_width=True):
        st.session_state.logged_in = False
        st.session_state.username = ""
        st.info("👋 Hoşça kalın!")
        st.rerun()
    
    st.sidebar.markdown("---")
    
    # Bilgi
    st.sidebar.subheader("ℹ️ Bilgi")
    db_info = {
        "Tarih": datetime.now().strftime("%d.%m.%Y"),
        "Saat": datetime.now().strftime("%H:%M:%S"),
    }
    
    for key, value in db_info.items():
        st.sidebar.text(f"{key}: {value}")
    
    return pages.get(selected_page, "dashboard")


# ============================================================
# PAGE: DASHBOARD
# ============================================================

def page_dashboard():
    """Dashboard sayfası"""
    st.title("📊 Dashboard")
    st.markdown("---")
    
    # Veritabanı oturumu al
    db = DatabaseEngine.create_session()
    
    try:
        # İstatistikleri hesapla
        total_categories = db.query(Category).count()
        total_products = db.query(Product).count()
        total_sales = db.query(Sale).count()
        total_expenses = db.query(Expense).count()
        
        # Aktif ürünler
        active_products = db.query(Product).filter(Product.is_active == True).count()
        
        # Düşük stok ürünleri
        low_stock_products = db.query(Product).filter(
            Product.quantity <= Product.min_stock_level
        ).count()
        
        # Metrikler satırı 1
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("📦 Toplam Ürün", total_products, active_products, delta_color="off")
        
        with col2:
            st.metric("🏷️ Kategoriler", total_categories, delta_color="off")
        
        with col3:
            st.metric("💰 Toplam Satış", total_sales, delta_color="off")
        
        with col4:
            st.metric("📋 Masraf", total_expenses, delta_color="off")
        
        st.markdown("---")
        
        # Düşük stok uyarısı
        if low_stock_products > 0:
            st.warning(f"⚠️ {low_stock_products} ürünün stok seviyesi düşük!", icon="⚠️")
        
        # Son satışlar
        st.subheader("📊 Son Satışlar")
        
        last_sales = db.query(Sale).order_by(Sale.created_at.desc()).limit(10).all()
        
        if last_sales:
            sales_data = []
            for sale in last_sales:
                sales_data.append({
                    "Satış No": sale.sale_number,
                    "Ürün": sale.product.name if sale.product else "N/A",
                    "Miktar": sale.quantity,
                    "Tutar": format_currency(float(sale.total_price)),
                    "Ödeme": sale.payment_method,
                    "Tarih": sale.created_at.strftime("%d.%m.%Y %H:%M"),
                })
            
            st.dataframe(
                sales_data,
                use_container_width=True,
                hide_index=True
            )
        else:
            st.info("Henüz satış kaydı yok")
        
        # Düşük stok malzemeleri
        st.subheader("⚠️ Düşük Stok Malzemeleri")
        
        from src.models import Ingredient
        low_stock_ingredients = db.query(Ingredient).filter(
            Ingredient.quantity < 100,
            Ingredient.is_active == True
        ).order_by(Ingredient.quantity).limit(10).all()
        
        if low_stock_ingredients:
            stock_data = []
            for ingredient in low_stock_ingredients:
                stock_data.append({
                    "Malzeme": ingredient.name,
                    "Mevcut": f"{ingredient.quantity:.2f} {ingredient.unit}",
                    "Eşik": "100",
                    "Durum": "⚠️ Kritik" if ingredient.quantity < 50 else "⚠️ Düşük",
                })
            
            st.dataframe(
                stock_data,
                use_container_width=True,
                hide_index=True
            )
        else:
            st.success("Tüm malzemelerin stok seviyesi iyi!")
    
    finally:
        db.close()


# ============================================================
# PAGE: SALES
# ============================================================

def page_sales():
    """Satış İşlemleri sayfası"""
    render_sales_page()


# ============================================================
# PAGE: INVENTORY
# ============================================================

def page_inventory():
    """Malzeme/Ürün Yönetimi sayfası"""
    render_inventory_page()


# ============================================================
# PAGE: EXPENSES
# ============================================================

def page_expenses():
    """Masraf Takibi sayfası"""
    render_expenses_page()


# ============================================================
# PAGE: REPORTS
# ============================================================

def page_reports():
    """Raporlar sayfası"""
    render_reports_page()


# ============================================================
# PAGE: SETTINGS
# ============================================================

def page_settings():
    """Ayarlar sayfası"""
    render_settings_page()


# ============================================================
# MAIN APP
# ============================================================

def main():
    """Ana uygulama fonksiyonu"""
    
    # Uygulamayı başlat
    if not init_app():
        st.stop()
    
    # Giriş kontrolü
    if not st.session_state.logged_in:
        page_login()
        st.stop()
    
    # Sidebar ve sayfa seçimi
    page = render_sidebar()
    
    # Sayfalara yönlendir
    pages_map = {
        "dashboard": page_dashboard,
        "sales": page_sales,
        "inventory": page_inventory,
        "expenses": page_expenses,
        "reports": page_reports,
        "settings": page_settings,
    }
    
    page_func = pages_map.get(page, page_dashboard)
    page_func()


if __name__ == "__main__":
    main()
