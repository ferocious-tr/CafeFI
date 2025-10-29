"""
🏪 CafeFlow - Satış Yönetimi Modülü

Satış işlemleri, reçete yönetimi, fiyatlandırma ve raporlama
"""

import streamlit as st
from datetime import datetime
import pandas as pd
from sqlalchemy.orm import Session
from sqlalchemy import func
from src.database import DatabaseEngine
from src.models import Product, Sale, Ingredient, Recipe, StockMovement
from decimal import Decimal
from src.utils.locale_utils import format_currency, format_datetime


class SalesManager:
    """Satış Yönetimi İş Mantığı"""
    
    # ============================================================
    # MALZEME (İNGREDİENT) YÖNETİMİ
    # ============================================================
    
    @staticmethod
    def create_ingredient(
        db: Session,
        name: str,
        unit: str,
        cost_per_unit: float
    ) -> Ingredient:
        """Yeni malzeme oluştur"""
        if cost_per_unit <= 0:
            raise ValueError("Maliyet 0'dan büyük olmalı!")
        
        existing = db.query(Ingredient).filter(Ingredient.name == name).first()
        if existing:
            raise ValueError(f"Malzeme '{name}' zaten var!")
        
        ingredient = Ingredient(
            name=name,
            unit=unit,
            cost_per_unit=cost_per_unit,
            quantity=0
        )
        db.add(ingredient)
        db.commit()
        db.refresh(ingredient)
        
        return ingredient
    
    @staticmethod
    def get_all_ingredients(db: Session, active_only: bool = True) -> list:
        """Tüm malzemeleri al"""
        query = db.query(Ingredient)
        if active_only:
            query = query.filter(Ingredient.is_active == True)
        return query.order_by(Ingredient.name).all()
    
    @staticmethod
    def update_ingredient_stock(
        db: Session,
        ingredient_id: int,
        quantity_change: float,
        reason: str = "Elle güncelleme"
    ) -> bool:
        """Malzeme stokunu güncelle"""
        ingredient = db.query(Ingredient).filter(Ingredient.id == ingredient_id).first()
        
        if not ingredient:
            raise ValueError(f"Malzeme bulunamadı (ID: {ingredient_id})")
        
        if quantity_change > 0:
            ingredient.add_stock(quantity_change)
        elif quantity_change < 0:
            ingredient.remove_stock(-quantity_change)
        
        db.commit()
        return True
    
    # ============================================================
    # REÇETE YÖNETİMİ
    # ============================================================
    
    @staticmethod
    def add_recipe_item(
        db: Session,
        product_id: int,
        ingredient_id: int,
        quantity: float,
        unit: str
    ) -> Recipe:
        """Reçeteye malzeme ekle"""
        if quantity <= 0:
            raise ValueError("Miktar 0'dan büyük olmalı!")
        
        product = db.query(Product).filter(Product.id == product_id).first()
        if not product:
            raise ValueError(f"Ürün bulunamadı (ID: {product_id})")
        
        ingredient = db.query(Ingredient).filter(Ingredient.id == ingredient_id).first()
        if not ingredient:
            raise ValueError(f"Malzeme bulunamadı (ID: {ingredient_id})")
        
        recipe = Recipe(
            product_id=product_id,
            ingredient_id=ingredient_id,
            quantity=quantity,
            unit=unit
        )
        db.add(recipe)
        db.commit()
        db.refresh(recipe)
        
        return recipe
    
    @staticmethod
    def get_recipe(db: Session, product_id: int) -> list:
        """Ürünün reçetesini al"""
        return db.query(Recipe).filter(Recipe.product_id == product_id).all()
    
    @staticmethod
    def calculate_product_cost(db: Session, product_id: int) -> float:
        """Ürünün toplam malzeme maliyetini hesapla"""
        recipe_items = db.query(Recipe).filter(Recipe.product_id == product_id).all()
        
        total_cost = 0
        for item in recipe_items:
            if item.ingredient:
                total_cost += item.quantity * item.ingredient.cost_per_unit
        
        return total_cost
    
    # ============================================================
    # SATIŞLAR
    # ============================================================
    
    @staticmethod
    def create_sale(
        db: Session,
        product_id: int,
        quantity: int,
        payment_method: str,
        notes: str = None
    ) -> Sale:
        """Satış oluştur (Stok düşmesi otomatik)"""
        product = db.query(Product).filter(Product.id == product_id).first()
        if not product:
            raise ValueError(f"Ürün bulunamadı (ID: {product_id})")
        
        if quantity <= 0:
            raise ValueError("Miktar 0'dan büyük olmalı!")
        
        if product.quantity < quantity:
            raise ValueError(f"Yetersiz ürün stoku! Mevcut: {product.quantity}, İstenen: {quantity}")
        
        # Malzeme stok kontrolü
        recipe_items = SalesManager.get_recipe(db, product_id)
        for item in recipe_items:
            required_quantity = item.quantity * quantity
            if item.ingredient.quantity < required_quantity:
                raise ValueError(
                    f"Yetersiz malzeme stoku! "
                    f"{item.ingredient.name}: Gerekli {required_quantity}{item.unit}, "
                    f"Mevcut: {item.ingredient.quantity}{item.unit}"
                )
        
        # Fiyat hesapla
        price_info = SalesManager.calculate_sale_price(db, product_id, quantity)
        
        # Satış numarası oluştur
        last_sale = db.query(Sale).order_by(Sale.id.desc()).first()
        sale_number = f"SAT-{(last_sale.id if last_sale else 0) + 1:06d}"
        
        # Satış kaydı oluştur
        sale = Sale(
            sale_number=sale_number,
            product_id=product_id,
            quantity=quantity,
            unit_price=Decimal(str(price_info["sale_price_without_kdv"])),
            total_price=Decimal(str(price_info["sale_price_without_kdv"] * quantity)),
            sale_price_without_kdv=Decimal(str(price_info["sale_price_without_kdv"] * quantity)),
            kdv_rate=Decimal(str(price_info["kdv_rate"])),
            kdv_amount=Decimal(str(price_info["kdv_amount"] * quantity)),
            total_with_kdv=Decimal(str(price_info["total_with_kdv"] * quantity)),
            product_cost=Decimal(str(price_info["ingredient_cost"] * quantity)),
            gross_profit=Decimal(str(price_info["gross_profit"] * quantity)),
            net_profit=Decimal(str(price_info["net_profit"] * quantity)),
            payment_method=payment_method,
            notes=notes
        )
        
        # Ürün stok düş
        product.quantity -= quantity
        
        # Malzeme stok düş (birim dönüşümü ile)
        for item in recipe_items:
            required_quantity = item.quantity * quantity
            # item.unit = recipe'deki birim, ingredient.unit = malzemenin stoğunun birimi
            item.ingredient.remove_stock(required_quantity, amount_unit=item.unit)
        
        db.add(sale)
        db.commit()
        db.refresh(sale)
        
        return sale
    
    @staticmethod
    def get_sales_by_period(db: Session, start_date: datetime, end_date: datetime) -> list:
        """Tarih aralığına göre satışları al"""
        return db.query(Sale).filter(
            Sale.created_at >= start_date,
            Sale.created_at <= end_date
        ).order_by(Sale.created_at.desc()).all()
    
    @staticmethod
    def get_all_sales(db: Session) -> list:
        """Tüm satışları al"""
        return db.query(Sale).order_by(Sale.created_at.desc()).all()
    
    @staticmethod
    def calculate_sale_price(
        db: Session,
        product_id: int,
        quantity: int = 1
    ) -> dict:
        """Satış fiyatını hesapla (Seçenek A: Satış Fiyatı = product.price (doğrudan))
        
        Hesaplama:
        - Satış Fiyatı = product.price (önceden belirlenen fiyat)
        - KDV = Satış Fiyatı × %20
        - Brüt Kâr = (Satış Fiyatı - KDV) - Malzeme Maliyeti
        - Net Kâr = Brüt Kâr (KDV zaten satış fiyatından düşüldü)
        """
        product = db.query(Product).filter(Product.id == product_id).first()
        if not product:
            raise ValueError(f"Ürün bulunamadı (ID: {product_id})")
        
        # Toplam malzeme maliyeti
        total_ingredient_cost = SalesManager.calculate_product_cost(db, product_id)
        
        # Seçenek A: Satış fiyatı ürünün önceden belirlenen fiyatı
        sale_price_without_kdv = float(product.price)
        
        # KDV hesaplaması (satış fiyatı üzerinden, ürün ana verisindeki kdv_rate'i kullan)
        kdv_rate = float(product.kdv_rate) / 100
        kdv_amount = sale_price_without_kdv * kdv_rate
        total_with_kdv = sale_price_without_kdv + kdv_amount
        
        # Kar hesaplaması
        # Brüt Kâr = (Satış Fiyatı - KDV) - Malzeme Maliyeti
        gross_profit = (sale_price_without_kdv - kdv_amount) - total_ingredient_cost
        # Net Kâr = Brüt Kâr (KDV satış fiyatından düşüldüğü için)
        net_profit = gross_profit
        
        return {
            "ingredient_cost": round(total_ingredient_cost, 2),
            "sale_price_without_kdv": round(sale_price_without_kdv, 2),
            "kdv_rate": kdv_rate * 100,
            "kdv_amount": round(kdv_amount, 2),
            "total_with_kdv": round(total_with_kdv, 2),
            "gross_profit": round(gross_profit, 2),
            "net_profit": round(net_profit, 2),
            "profit_margin_percent": None  # Seçenek A'da kullanılmıyor
        }
    
    # ============================================================
    # RAPORLAR
    # ============================================================
    
    @staticmethod
    def get_sales_report(db: Session, start_date: datetime = None, end_date: datetime = None) -> dict:
        """Satış raporu"""
        query = db.query(Sale)
        
        if start_date:
            query = query.filter(Sale.created_at >= start_date)
        if end_date:
            query = query.filter(Sale.created_at <= end_date)
        
        sales = query.all()
        
        if not sales:
            return {
                "total_sales": 0,
                "total_revenue": 0,
                "total_kdv": 0,
                "total_ingredient_cost": 0,
                "total_gross_profit": 0,
                "total_net_profit": 0,
                "average_per_sale": 0
            }
        
        total_revenue = sum(float(s.total_with_kdv) for s in sales)
        total_kdv = sum(float(s.kdv_amount) for s in sales)
        total_cost = sum(float(s.product_cost) for s in sales)
        total_gross_profit = sum(float(s.gross_profit) for s in sales)
        total_net_profit = sum(float(s.net_profit) for s in sales)
        
        return {
            "total_sales": len(sales),
            "total_revenue": round(total_revenue, 2),
            "total_kdv": round(total_kdv, 2),
            "total_ingredient_cost": round(total_cost, 2),
            "total_gross_profit": round(total_gross_profit, 2),
            "total_net_profit": round(total_net_profit, 2),
            "average_per_sale": round(total_revenue / len(sales), 2) if sales else 0
        }
    
    @staticmethod
    def get_product_sales_summary(db: Session, start_date: datetime = None, end_date: datetime = None) -> dict:
        """Ürün bazlı satış özeti"""
        query = db.query(
            Sale.product_id,
            Product.name,
            func.count(Sale.id).label("count"),
            func.sum(Sale.quantity).label("total_quantity"),
            func.sum(Sale.total_with_kdv).label("total_revenue"),
            func.sum(Sale.net_profit).label("total_profit")
        ).join(Product).group_by(Sale.product_id, Product.name)
        
        if start_date:
            query = query.filter(Sale.created_at >= start_date)
        if end_date:
            query = query.filter(Sale.created_at <= end_date)
        
        results = {}
        for product_id, product_name, count, quantity, revenue, profit in query.all():
            results[product_name] = {
                "count": count,
                "quantity": quantity,
                "revenue": float(revenue) if revenue else 0,
                "profit": float(profit) if profit else 0
            }
        
        return results


# ============================================================
# STREAMLIT UI
# ============================================================

def render_sales_page():
    """Satış sayfasını oluştur"""
    
    st.title("🏪 Satış İşlemleri")
    st.markdown("---")
    
    db = DatabaseEngine.create_session()
    
    try:
        tab1, tab2, tab3 = st.tabs([
            "💳 Hızlı Satış",
            "📋 Satış Geçmişi",
            "📊 Raporlar"
        ])
        
        # ============================================================
        # TAB 1: HIZLI SATIŞLAR
        # ============================================================
        
        with tab1:
            st.subheader("Satış Yap")
            
            products = db.query(Product).filter(Product.is_active == True).order_by(Product.name).all()
            
            if not products:
                st.warning("Aktif ürün yok! Lütfen Malzeme ve Ürün Yönetimi sayfasında ürün oluşturun.")
            else:
                with st.form("sales_form"):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        product_id = st.selectbox(
                            "Ürün Seçin *",
                            options=[p.id for p in products],
                            format_func=lambda x: next((p.name for p in products if p.id == x), "")
                        )
                    
                    with col2:
                        quantity = st.number_input(
                            "Miktar *",
                            min_value=1,
                            value=1
                        )
                    
                    if product_id:
                        try:
                            # Fiyat hesapla
                            price_info = SalesManager.calculate_sale_price(db, product_id, quantity)
                            
                            st.markdown("---")
                            st.subheader("📊 Fiyat Bilgisi")
                            
                            col1, col2, col3 = st.columns(3)
                            with col1:
                                st.metric("Malzeme Maliyeti", format_currency(price_info['ingredient_cost']))
                            with col2:
                                st.metric("Satış Fiyatı (KDV -)", format_currency(price_info['sale_price_without_kdv']))
                            with col3:
                                st.metric("KDV (%8)", format_currency(price_info['kdv_amount']))
                            
                            col1, col2, col3 = st.columns(3)
                            with col1:
                                st.metric("Toplam (KDV +)", format_currency(price_info['total_with_kdv']), delta_color="off")
                            with col2:
                                st.metric("Brüt Kâr", format_currency(price_info['gross_profit']))
                            with col3:
                                st.metric("Net Kâr", format_currency(price_info['net_profit']))
                        
                        except Exception as e:
                            st.error(f"Fiyat hesaplamada hata: {str(e)}")
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        payment_method = st.selectbox(
                            "Ödeme Yöntemi *",
                            list(Sale.PAYMENT_METHODS.keys()),
                            format_func=lambda x: Sale.PAYMENT_METHODS.get(x, x)
                        )
                    
                    with col2:
                        notes = st.text_input("Not")
                    
                    submitted = st.form_submit_button("💾 Satışı Kaydet", use_container_width=True)
                    
                    if submitted:
                        try:
                            sale = SalesManager.create_sale(
                                db,
                                product_id=product_id,
                                quantity=quantity,
                                payment_method=payment_method,
                                notes=notes if notes else None
                            )
                            st.success(f"✓ Satış kaydedildi! (Satış No: {sale.sale_number})")
                            st.rerun()
                        except ValueError as e:
                            st.error(f"✗ Hata: {str(e)}")
        
        # ============================================================
        # TAB 2: SATIŞLAR GEÇMİŞİ
        # ============================================================
        
        with tab2:
            st.subheader("Satış Geçmişi")
            
            col1, col2 = st.columns(2)
            with col1:
                start_date = st.date_input("Başlangıç Tarihi", value=datetime.now().replace(day=1), key="sales_start")
            with col2:
                end_date = st.date_input("Bitiş Tarihi", value=datetime.now(), key="sales_end")
            
            sales = SalesManager.get_sales_by_period(
                db,
                datetime.combine(start_date, datetime.min.time()),
                datetime.combine(end_date, datetime.max.time())
            )
            
            if sales:
                sales_data = []
                for sale in sales:
                    sales_data.append({
                        "Satış No": sale.sale_number,
                        "Tarih": sale.created_at.strftime("%d.%m.%Y %H:%M"),
                        "Ürün": sale.product.name if sale.product else "N/A",
                        "Miktar": sale.quantity,
                        "Ürün Maliyeti": format_currency(float(sale.product_cost) / sale.quantity if sale.quantity > 0 else 0),
                        "Tutar (KDV-)": format_currency(float(sale.sale_price_without_kdv)),
                        "KDV": format_currency(float(sale.kdv_amount)),
                        "Toplam": format_currency(float(sale.total_with_kdv)),
                        "Kâr": format_currency(float(sale.net_profit))
                    })
                
                st.dataframe(pd.DataFrame(sales_data), use_container_width=True, hide_index=True)
            else:
                st.info("Satış kaydı bulunamadı")
        
        # ============================================================
        # TAB 3: RAPORLAR
        # ============================================================
        
        with tab3:
            st.subheader("📊 Satış Raporları")
            
            col1, col2 = st.columns(2)
            with col1:
                report_start = st.date_input("Rapor Başlangıcı", value=datetime.now().replace(day=1), key="rep_start")
            with col2:
                report_end = st.date_input("Rapor Sonu", value=datetime.now(), key="rep_end")
            
            start_dt = datetime.combine(report_start, datetime.min.time())
            end_dt = datetime.combine(report_end, datetime.max.time())
            
            report = SalesManager.get_sales_report(db, start_dt, end_dt)
            
            st.markdown("---")
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Toplam Satış", report["total_sales"])
            with col2:
                st.metric("Toplam Gelir", format_currency(report['total_revenue']))
            with col3:
                st.metric("Toplam KDV", format_currency(report['total_kdv']))
            with col4:
                st.metric("Ort. Tutar", format_currency(report['average_per_sale']))
            
            st.markdown("---")
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Malzeme Maliyeti", format_currency(report['total_ingredient_cost']))
            with col2:
                st.metric("Brüt Kâr", format_currency(report['total_gross_profit']))
            with col3:
                st.metric("Net Kâr", format_currency(report['total_net_profit']))
            
            st.markdown("---")
            st.subheader("Ürün Bazlı Satışlar")
            
            product_summary = SalesManager.get_product_sales_summary(db, start_dt, end_dt)
            
            if product_summary:
                summary_data = []
                for product_name, data in product_summary.items():
                    summary_data.append({
                        "Ürün": product_name,
                        "Adet": data["count"],
                        "Miktar": data["quantity"],
                        "Gelir": format_currency(data['revenue']),
                        "Kâr": format_currency(data['profit'])
                    })
                
                st.dataframe(pd.DataFrame(summary_data), use_container_width=True, hide_index=True)
            else:
                st.info("Satış kaydı yok")
    
    finally:
        db.close()
