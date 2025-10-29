"""
📦 CafeFl - Malzeme ve Ürün Yönetimi Modülü (Yeni Versiyon)

Malzeme ve ürün yönetimi + Ürün & Reçete CRUD işlemleri
"""

import streamlit as st
from datetime import datetime
import pandas as pd
from sqlalchemy.orm import Session
from decimal import Decimal
from src.database import DatabaseEngine
from src.models import Product, Ingredient, Recipe, Category
from src.utils.locale_utils import format_currency, format_date, format_datetime


class InventoryManager:
    """Malzeme ve Ürün Yönetimi"""
    
    @staticmethod
    def add_ingredient_stock(
        db: Session,
        ingredient_id: int,
        quantity: float,
        reason: str = "Giriş"
    ) -> bool:
        """Malzemeye stok ekle"""
        ingredient = db.query(Ingredient).filter(Ingredient.id == ingredient_id).first()
        if not ingredient:
            raise ValueError(f"Malzeme bulunamadı")
        
        ingredient.add_stock(quantity)
        db.commit()
        return True
    
    @staticmethod
    def remove_ingredient_stock(
        db: Session,
        ingredient_id: int,
        quantity: float,
        reason: str = "Çıkış"
    ) -> bool:
        """Malzemeden stok çıkar"""
        ingredient = db.query(Ingredient).filter(Ingredient.id == ingredient_id).first()
        if not ingredient:
            raise ValueError(f"Malzeme bulunamadı")
        
        ingredient.remove_stock(quantity)
        db.commit()
        return True
    
    @staticmethod
    def get_all_products(db: Session, category_id: int = None, active_only: bool = True):
        """Tüm ürünleri al"""
        query = db.query(Product)
        if active_only:
            query = query.filter(Product.is_active == True)
        if category_id:
            query = query.filter(Product.category_id == category_id)
        return query.order_by(Product.name).all()
    
    @staticmethod
    def create_product(
        db: Session,
        name: str,
        code: str,
        category_id: int,
        price: float,
        kdv_rate: float = 8.0,
        profit_margin: float = 30.0,
        description: str = None,
    ) -> Product:
        """Yeni ürün oluştur"""
        existing = db.query(Product).filter(Product.code == code).first()
        if existing:
            raise ValueError(f"Ürün kodu '{code}' zaten var!")
        
        product = Product(
            name=name,
            code=code,
            category_id=category_id,
            price=price,
            kdv_rate=Decimal(str(kdv_rate)),
            profit_margin_value=Decimal(str(profit_margin)),
            description=description,
            quantity=100  # Sayısal ürünler için (satış adet olarak yapılır)
        )
        db.add(product)
        db.commit()
        db.refresh(product)
        return product
    
    @staticmethod
    def update_product(db: Session, product_id: int, **kwargs) -> Product:
        """Ürünü güncelle"""
        product = db.query(Product).filter(Product.id == product_id).first()
        if not product:
            raise ValueError(f"Ürün bulunamadı")
        
        # code benzersizliği kontrolü
        if "code" in kwargs:
            existing = db.query(Product).filter(
                Product.code == kwargs["code"],
                Product.id != product_id
            ).first()
            if existing:
                raise ValueError(f"Ürün kodu zaten kullanımda!")
        
        for key, value in kwargs.items():
            if hasattr(product, key):
                if key == "profit_margin_value":
                    setattr(product, key, Decimal(str(value)))
                elif key == "kdv_rate":
                    setattr(product, key, Decimal(str(value)))
                else:
                    setattr(product, key, value)
        
        db.commit()
        db.refresh(product)
        return product
    
    @staticmethod
    def delete_product(db: Session, product_id: int) -> bool:
        """Ürünü sil (soft delete)"""
        product = db.query(Product).filter(Product.id == product_id).first()
        if not product:
            raise ValueError(f"Ürün bulunamadı")
        
        product.is_active = False
        db.commit()
        return True


# ============================================================
# STREAMLIT UI
# ============================================================

def render_inventory_page():
    """Malzeme ve Ürün Yönetimi sayfasını oluştur"""

    st.title("📦 Malzeme ve Ürün Yönetimi")
    st.markdown("---")
    
    db = DatabaseEngine.create_session()
    
    try:
        # MAIN TABS
        main_tab1, main_tab2 = st.tabs(["🧂 Malzeme Yönetimi", "📦 Ürün Yönetimi"])
        
        # ================================================================
        # BÖLÜM 1: MALZEME STOK YÖNETİMİ
        # ================================================================
        
        with main_tab1:
            st.subheader("Malzeme ve Stok Yönetimi")
            
            # Malzeme tabları
            ing_tab1, ing_tab2, ing_tab3, ing_tab4 = st.tabs([
                "📋 Malzeme Listesi",
                "➕ Stok Girişi",
                "➖ Stok Çıkışı",
                "✏️ Malzeme Düzenle"
            ])
            
            # TAB 1: MALZEME LİSTESİ
            with ing_tab1:
                st.subheader("Malzeme Yönetimi")
                
                col1, col2 = st.columns(2)
                
                # Yeni malzeme ekleme
                with col1:
                    st.subheader("➕ Yeni Malzeme Ekle")
                    with st.form("new_ingredient_form"):
                        ing_name = st.text_input("Malzeme Adı *")
                        ing_unit = st.selectbox(
                            "Birim *",
                            ["g", "ml", "adet", "kg", "l"]
                        )
                        ing_cost = st.number_input("Birim Başına Maliyet (₺) *", min_value=0.01, value=1.0)
                        
                        if st.form_submit_button("Malzeme Ekle", use_container_width=True):
                            try:
                                from src.modules.sales import SalesManager
                                SalesManager.create_ingredient(db, ing_name, ing_unit, ing_cost)
                                st.success("✓ Malzeme eklendi!")
                                st.rerun()
                            except ValueError as e:
                                st.error(f"✗ Hata: {str(e)}")
                
                # Mevcut malzemeleri göster
                with col2:
                    st.subheader("📋 Mevcut Malzemeler")
                    
                    from src.modules.sales import SalesManager
                    ingredients = SalesManager.get_all_ingredients(db)
                    
                    if ingredients:
                        ing_data = []
                        for ing in ingredients:
                            ing_data.append({
                                "Malzeme": ing.name,
                                "Birim": ing.unit,
                                "Stok": f"{ing.quantity:.2f}",
                                "Birim Maliyeti": format_currency(ing.cost_per_unit),
                                "Toplam Değeri": format_currency(ing.get_total_cost()),
                                "Durum": ing.get_stock_status()
                            })
                        
                        st.dataframe(pd.DataFrame(ing_data), use_container_width=True, hide_index=True)
                    else:
                        st.info("Malzeme yok")
            
            # TAB 2: STOK GİRİŞİ
            with ing_tab2:
                st.subheader("Malzeme Stok Girişi")
                
                with st.form("ingredient_add_stock_form"):
                    ingredients = SalesManager.get_all_ingredients(db)
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        ingredient_id = st.selectbox(
                            "Malzeme Seçin *",
                            options=[ing.id for ing in ingredients],
                            format_func=lambda x: next((ing.name for ing in ingredients if ing.id == x), "")
                        )
                    
                    with col2:
                        quantity = st.number_input("Miktar *", min_value=0.01, value=1.0)
                    
                    reason = st.text_input("Sebep", value="Giriş")
                    
                    submitted = st.form_submit_button("💾 Stok Ekle", use_container_width=True)
                    
                    if submitted:
                        try:
                            InventoryManager.add_ingredient_stock(db, ingredient_id, quantity, reason)
                            st.success("✓ Stok eklendi!")
                            st.rerun()
                        except ValueError as e:
                            st.error(f"✗ Hata: {str(e)}")
            
            # TAB 3: STOK ÇIKIŞ
            with ing_tab3:
                st.subheader("Malzeme Stok Çıkışı")
                
                with st.form("ingredient_remove_stock_form"):
                    ingredients = SalesManager.get_all_ingredients(db)
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        ingredient_id = st.selectbox(
                            "Malzeme Seçin *",
                            options=[ing.id for ing in ingredients],
                            format_func=lambda x: next((ing.name for ing in ingredients if ing.id == x), ""),
                            key="remove_ing"
                        )
                    
                    with col2:
                        quantity = st.number_input("Miktar *", min_value=0.01, value=1.0, key="remove_qty")
                    
                    reason = st.text_input("Sebep", value="Çıkış", key="remove_reason")
                    
                    submitted = st.form_submit_button("✂️ Stok Çıkar", use_container_width=True)
                    
                    if submitted:
                        try:
                            InventoryManager.remove_ingredient_stock(db, ingredient_id, quantity, reason)
                            st.success("✓ Stok çıkarıldı!")
                            st.rerun()
                        except ValueError as e:
                            st.error(f"✗ Hata: {str(e)}")
            
            # TAB 4: MALZEME DÜZENLE
            with ing_tab4:
                st.subheader("Malzeme Düzenle")
                
                ingredients = SalesManager.get_all_ingredients(db)
                
                if not ingredients:
                    st.info("Düzenlenecek malzeme yok")
                else:
                    col1, col2 = st.columns([3, 1])
                    
                    with col1:
                        selected_ing = st.selectbox(
                            "Malzeme Seçin *",
                            options=[ing.id for ing in ingredients],
                            format_func=lambda x: next((ing.name for ing in ingredients if ing.id == x), ""),
                            key="edit_ing"
                        )
                    
                    selected_ingredient = next((ing for ing in ingredients if ing.id == selected_ing), None)
                    
                    if selected_ingredient:
                        st.divider()
                        
                        col1, col2, col3 = st.columns(3)
                        
                        with col1:
                            st.metric("Mevcut Stok", f"{selected_ingredient.quantity:.2f} {selected_ingredient.unit}")
                        
                        with col2:
                            st.metric("Birim Maliyeti", format_currency(selected_ingredient.cost_per_unit))
                        
                        with col3:
                            st.metric("Toplam Değeri", format_currency(selected_ingredient.get_total_cost()))
                        
                        st.divider()
                        
                        with st.form("ingredient_edit_form"):
                            col1, col2 = st.columns(2)
                            
                            with col1:
                                new_name = st.text_input(
                                    "Malzeme Adı *",
                                    value=selected_ingredient.name
                                )
                            
                            with col2:
                                new_unit = st.selectbox(
                                    "Birim *",
                                    options=["g", "kg", "ml", "l", "adet"],
                                    index=["g", "kg", "ml", "l", "adet"].index(selected_ingredient.unit)
                                )
                            
                            col1, col2 = st.columns(2)
                            
                            with col1:
                                new_cost = st.number_input(
                                    "Birim Maliyeti (₺) *",
                                    min_value=0.0001,
                                    value=float(selected_ingredient.cost_per_unit),
                                    step=0.0001,
                                    format="%.4f"
                                )
                            
                            with col2:
                                st.metric("Tahmini Stok Toplam", format_currency(new_cost * selected_ingredient.quantity))
                            
                            st.divider()
                            
                            col1, col2, col3 = st.columns(3)
                            
                            with col1:
                                submitted = st.form_submit_button("💾 Kaydet", use_container_width=True)
                            
                            with col2:
                                # Formu dıştaki silme işlemi için hazırlama
                                st.write("")
                            
                            with col3:
                                st.write("")
                            
                            if submitted:
                                try:
                                    # Aynı isim kontrolü (kendisi hariç)
                                    dup_check = db.query(Ingredient).filter(
                                        Ingredient.name == new_name,
                                        Ingredient.id != selected_ingredient.id
                                    ).first()
                                    
                                    if dup_check:
                                        st.error("✗ Bu isimde başka bir malzeme zaten var!")
                                    else:
                                        selected_ingredient.name = new_name
                                        selected_ingredient.unit = new_unit
                                        selected_ingredient.cost_per_unit = new_cost
                                        db.commit()
                                        st.success("✓ Malzeme güncellendi!")
                                        st.rerun()
                                except Exception as e:
                                    st.error(f"✗ Hata: {str(e)}")
                        
                        # Silme butonu (form dışında)
                        st.divider()
                        
                        if st.button("🗑️ Sil", use_container_width=True, key="delete_ing_btn"):
                            try:
                                # Soft delete: is_active = False
                                selected_ingredient.is_active = False
                                db.commit()
                                st.success("✓ Malzeme silindi!")
                                st.rerun()
                            except Exception as e:
                                st.error(f"✗ Silme hatası: {str(e)}")
        
        # ================================================================
        # BÖLÜM 2: ÜRÜN YÖNETİMİ
        # ================================================================
        
        with main_tab2:
            st.subheader("Ürün Yönetimi")
            
            # Ürün tabları
            prod_tab1, prod_tab2, prod_tab3, prod_tab4 = st.tabs([
                "📋 Ürünler",
                "➕ Yeni Ürün",
                "✏️ Düzenle",
                "📝 Reçete"
            ])
            
            # TAB 1: ÜRÜN LİSTESİ
            with prod_tab1:
                st.subheader("Ürün Listesi")
                
                categories = db.query(Category).filter(Category.is_active == True).all()
                category_dict = {0: "Tümü"}
                category_dict.update({cat.id: cat.name for cat in categories})
                
                col1, col2 = st.columns(2)
                
                with col1:
                    selected_category = st.selectbox(
                        "Kategori Filtresi",
                        options=category_dict.keys(),
                        format_func=lambda x: category_dict[x]
                    )
                
                with col2:
                    search_query = st.text_input("Ürün Ara")
                
                products = InventoryManager.get_all_products(
                    db,
                    category_id=selected_category if selected_category != 0 else None
                )
                
                if search_query:
                    products = [
                        p for p in products
                        if search_query.lower() in p.name.lower() or
                        search_query.lower() in p.code.lower()
                    ]
                
                if products:
                    prod_data = []
                    for prod in products:
                        recipe_count = db.query(Recipe).filter(Recipe.product_id == prod.id).count()
                        prod_data.append({
                            "Ürün": prod.name,
                            "Kod": prod.code,
                            "Kategori": prod.category.name if prod.category else "N/A",
                            "Fiyat": format_currency(prod.price),
                            "Kar %": f"{prod.profit_margin:.1f}%",
                            "KDV": f"{prod.kdv_rate:.1f}%",
                            "Reçete": f"{recipe_count} malzeme"
                        })
                    
                    st.dataframe(pd.DataFrame(prod_data), use_container_width=True, hide_index=True)
                else:
                    st.info("Ürün bulunamadı")
            
            # TAB 2: YENİ ÜRÜN
            with prod_tab2:
                st.subheader("Yeni Ürün Ekle")
                
                with st.form("new_product_form"):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        prod_name = st.text_input("Ürün Adı *")
                        prod_code = st.text_input("Ürün Kodu *", placeholder="örn: KAHVE-001")
                    
                    with col2:
                        categories = db.query(Category).filter(Category.is_active == True).all()
                        category_id = st.selectbox(
                            "Kategori *",
                            options=[cat.id for cat in categories],
                            format_func=lambda x: next((cat.name for cat in categories if cat.id == x), "")
                        )
                        prod_price = st.number_input("Satış Fiyatı (₺) *", min_value=0.01, value=10.0)
                    
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        kdv_rate = st.number_input("KDV Oranı (%)", min_value=0.0, max_value=100.0, value=8.0)
                    
                    with col2:
                        profit_margin = st.number_input("Kar Marjı (%)", min_value=0.0, max_value=100.0, value=30.0)
                    
                    with col3:
                        pass
                    
                    description = st.text_area("Açıklama")
                    
                    submitted = st.form_submit_button("➕ Ürün Ekle", use_container_width=True)
                    
                    if submitted:
                        if not prod_name or not prod_code:
                            st.error("✗ Ürün adı ve kodu zorunludur!")
                        else:
                            try:
                                InventoryManager.create_product(
                                    db,
                                    prod_name,
                                    prod_code,
                                    category_id,
                                    prod_price,
                                    kdv_rate,
                                    profit_margin,
                                    description if description else None
                                )
                                st.success("✓ Ürün eklendi!")
                                st.rerun()
                            except ValueError as e:
                                st.error(f"✗ Hata: {str(e)}")
            
            # TAB 3: DÜZENLE/SİL
            with prod_tab3:
                st.subheader("Ürün Düzenle / Sil")
                
                products = InventoryManager.get_all_products(db)
                
                if products:
                    selected_product = st.selectbox(
                        "Ürün Seçin",
                        options=[p.id for p in products],
                        format_func=lambda x: next((p.name for p in products if p.id == x), "")
                    )
                    
                    prod = next((p for p in products if p.id == selected_product), None)
                    
                    if prod:
                        with st.form("edit_product_form"):
                            col1, col2 = st.columns(2)
                            
                            with col1:
                                new_name = st.text_input("Ürün Adı", value=prod.name)
                                new_code = st.text_input("Ürün Kodu", value=prod.code)
                            
                            with col2:
                                new_price = st.number_input("Satış Fiyatı (₺)", value=float(prod.price))
                                new_kdv = st.number_input("KDV (%)", value=float(prod.kdv_rate))
                            
                            new_margin = st.number_input("Kar Marjı (%)", value=float(prod.profit_margin))
                            new_description = st.text_area("Açıklama", value=prod.description or "")
                            
                            col1, col2, col3 = st.columns(3)
                            
                            with col1:
                                update_btn = st.form_submit_button("✏️ Güncelle", use_container_width=True)
                            
                            with col2:
                                pass
                            
                            with col3:
                                delete_btn = st.form_submit_button("🗑️ Sil", use_container_width=True)
                            
                            if update_btn:
                                try:
                                    InventoryManager.update_product(
                                        db,
                                        prod.id,
                                        name=new_name,
                                        code=new_code,
                                        price=new_price,
                                        kdv_rate=new_kdv,
                                        profit_margin_value=new_margin,
                                        description=new_description
                                    )
                                    st.success("✓ Ürün güncellendi!")
                                    st.rerun()
                                except ValueError as e:
                                    st.error(f"✗ Hata: {str(e)}")
                            
                            if delete_btn:
                                try:
                                    InventoryManager.delete_product(db, prod.id)
                                    st.success("✓ Ürün silindi!")
                                    st.rerun()
                                except ValueError as e:
                                    st.error(f"✗ Hata: {str(e)}")
                else:
                    st.info("Ürün yok")
            
            # TAB 4: REÇETE YÖNETIMI
            with prod_tab4:
                st.subheader("Reçete Yönetimi")
                
                products = InventoryManager.get_all_products(db)
                
                if products:
                    selected_product = st.selectbox(
                        "Ürün Seçin",
                        options=[p.id for p in products],
                        format_func=lambda x: next((p.name for p in products if p.id == x), ""),
                        key="recipe_product"
                    )
                    
                    prod = next((p for p in products if p.id == selected_product), None)
                    
                    if prod:
                        st.markdown("---")
                        st.write(f"**Ürün:** {prod.name} ({prod.code})")
                        
                        # Mevcut Reçete
                        recipes = db.query(Recipe).filter(Recipe.product_id == prod.id).all()
                        
                        if recipes:
                            st.subheader("Mevcut Malzemeler")
                            
                            recipe_data = []
                            for recipe in recipes:
                                recipe_data.append({
                                    "Malzeme": recipe.ingredient.name if recipe.ingredient else "N/A",
                                    "Miktar": f"{recipe.quantity}",
                                    "Birim": recipe.unit,
                                    "Birim Maliyeti": format_currency(recipe.ingredient.cost_per_unit) if recipe.ingredient else "N/A",
                                    "Toplam": format_currency(recipe.ingredient_cost)
                                })
                            
                            st.dataframe(pd.DataFrame(recipe_data), use_container_width=True, hide_index=True)
                            
                            st.write(f"**Toplam Malzeme Maliyeti:** {format_currency(sum(r.ingredient_cost for r in recipes))}")
                        else:
                            st.info("Henüz malzeme eklenmedi")
                        
                        st.markdown("---")
                        st.subheader("Yeni Malzeme Ekle")
                        
                        with st.form("add_recipe_item_form"):
                            ingredients = SalesManager.get_all_ingredients(db)
                            
                            col1, col2 = st.columns(2)
                            
                            with col1:
                                ingredient_id = st.selectbox(
                                    "Malzeme Seçin *",
                                    options=[ing.id for ing in ingredients],
                                    format_func=lambda x: next((ing.name for ing in ingredients if ing.id == x), ""),
                                    key="recipe_ingredient"
                                )
                            
                            with col2:
                                quantity = st.number_input("Miktar *", min_value=0.01, value=1.0, key="recipe_qty")
                            
                            selected_ing = next((ing for ing in ingredients if ing.id == ingredient_id), None)
                            unit = st.selectbox(
                                "Birim *",
                                options=["g", "ml", "adet", "kg", "l"],
                                index=0 if not selected_ing else ["g", "ml", "adet", "kg", "l"].index(selected_ing.unit)
                            )
                            
                            submitted = st.form_submit_button("➕ Malzeme Ekle", use_container_width=True)
                            
                            if submitted:
                                try:
                                    SalesManager.add_recipe_item(db, prod.id, ingredient_id, quantity, unit)
                                    st.success("✓ Malzeme eklendi!")
                                    st.rerun()
                                except ValueError as e:
                                    st.error(f"✗ Hata: {str(e)}")
                        
                        # Mevcut malzemeleri silme
                        if recipes:
                            st.markdown("---")
                            st.subheader("Malzeme Kaldır")
                            
                            for recipe in recipes:
                                col1, col2 = st.columns([4, 1])
                                
                                with col1:
                                    st.text(f"• {recipe.ingredient.name} ({recipe.quantity}{recipe.unit})")
                                
                                with col2:
                                    if st.button("❌", key=f"delete_recipe_{recipe.id}", use_container_width=True):
                                        db.delete(recipe)
                                        db.commit()
                                        st.success("✓ Malzeme kaldırıldı!")
                                        st.rerun()
                else:
                    st.info("Ürün yok")
    
    finally:
        db.close()
