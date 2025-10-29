"""
⚙️ Ayarlar Modülü - Kategori Yönetimi & Kullanıcı Ayarları
"""

import streamlit as st
import pandas as pd
from src.database import DatabaseEngine
from src.models import Category, Expense, Product, ExpenseCategory


def render_settings_page():
    """Ayarlar sayfasını oluştur"""
    
    st.title("⚙️ Ayarlar")
    st.markdown("---")
    
    db = DatabaseEngine.create_session()
    
    try:
        # Main tabs
        tab1, tab2, tab3 = st.tabs([
            "👤 Kullanıcı Ayarları",
            "🏷️ Ürün Kategorileri",
            "💰 Masraf Kategorileri"
        ])
        
        # ============================================================
        # TAB 1: KULLANICI AYARLARI
        # ============================================================
        with tab1:
            st.subheader("Kullanıcı Ayarları")
            
            col1, col2 = st.columns([1, 1], gap="large")
            
            with col1:
                st.subheader("🔐 Şifre Değiştir")
                
                with st.form("change_password_form"):
                    current_password = st.text_input(
                        "Mevcut Şifre *",
                        type="password",
                        placeholder="••••••••"
                    )
                    
                    new_password = st.text_input(
                        "Yeni Şifre *",
                        type="password",
                        placeholder="••••••••"
                    )
                    
                    confirm_password = st.text_input(
                        "Yeni Şifre (Tekrar) *",
                        type="password",
                        placeholder="••••••••"
                    )
                    
                    submitted = st.form_submit_button("🔄 Şifre Değiştir", use_container_width=True)
                    
                    if submitted:
                        # Basit kontrol: admin kullanıcısı için kontrol
                        if current_password == "admin123":
                            if new_password == confirm_password and len(new_password) >= 6:
                                st.success("✓ Şifre başarıyla değiştirildi! (Henüz veritabanında tutulmadığı için demo amaçlıdır)")
                                st.info("💡 Veya kullanıcıların kaydedildiği bir sistem için veritabanı bağlantısı eklenebilir.")
                            elif new_password != confirm_password:
                                st.error("✗ Şifreler eşleşmiyor!")
                            else:
                                st.error("✗ Yeni şifre en az 6 karakter olmalıdır!")
                        else:
                            st.error("✗ Mevcut şifre yanlış!")
            
            with col2:
                st.subheader("ℹ️ Hesap Bilgileri")
                st.info(f"📛 **Kullanıcı Adı:** {st.session_state.get('username', 'admin')}")
                st.info("📅 **Son Giriş:** Bugün")
                st.info("🔑 **Varsayılan Şifre:** admin123")
        
        # ============================================================
        # TAB 2: ÜRÜN KATEGORİLERİ
        # ============================================================
        with tab2:
            st.subheader("Ürün Kategorileri CRUD")
            
            col1, col2 = st.columns([1, 1], gap="large")
            
            with col1:
                st.subheader("➕ Yeni Kategori Ekle")
                
                with st.form("new_product_category_form"):
                    cat_name = st.text_input("Kategori Adı *", placeholder="ör: Kahveler")
                    cat_code = st.text_input("Kategori Kodu *", placeholder="ör: COFFEE (max 10 harf)", max_chars=10).upper()
                    cat_desc = st.text_area("Açıklama", placeholder="Kategori açıklaması", height=80)
                    
                    submitted = st.form_submit_button("Kategori Ekle", use_container_width=True)
                    
                    if submitted and cat_name and cat_code:
                        try:
                            # Benzersizlik kontrolü
                            existing_name = db.query(Category).filter(Category.name == cat_name).first()
                            existing_code = db.query(Category).filter(Category.code == cat_code).first()
                            
                            if existing_name:
                                st.error(f"✗ '{cat_name}' kategorisi zaten var!")
                            elif existing_code:
                                st.error(f"✗ '{cat_code}' kodu zaten kullanılıyor!")
                            else:
                                new_cat = Category(
                                    name=cat_name,
                                    code=cat_code,
                                    description=cat_desc if cat_desc else None
                                )
                                db.add(new_cat)
                                db.commit()
                                st.success(f"✓ '{cat_name}' kategorisi eklendi!")
                                st.rerun()
                        except Exception as e:
                            st.error(f"✗ Hata: {str(e)}")
                    elif submitted and not cat_name:
                        st.error("✗ Kategori adı zorunludur!")
                    elif submitted and not cat_code:
                        st.error("✗ Kategori kodu zorunludur!")
            
            with col2:
                st.subheader("📋 Mevcut Kategoriler")
                
                categories = db.query(Category).order_by(Category.name).all()
                
                if categories:
                    cat_data = []
                    for cat in categories:
                        cat_data.append({
                            "ID": cat.id,
                            "Kategori": cat.name,
                            "Açıklama": cat.description or "-",
                        })
                    
                    st.dataframe(pd.DataFrame(cat_data), use_container_width=True, hide_index=True)
                    
                    st.markdown("---")
                    st.subheader("✏️ Kategori Düzenle / ❌ Sil")
                    
                    selected_cat = st.selectbox(
                        "Düzenlemek için kategori seçin",
                        options=[c.id for c in categories],
                        format_func=lambda x: next((c.name for c in categories if c.id == x), "")
                    )
                    
                    if selected_cat:
                        selected = next((c for c in categories if c.id == selected_cat), None)
                        
                        col_edit, col_delete = st.columns(2)
                        
                        with col_edit:
                            with st.form("edit_product_category_form"):
                                new_name = st.text_input("Yeni Kategori Adı", value=selected.name)
                                new_desc = st.text_area("Yeni Açıklama", value=selected.description or "", height=80)
                                
                                if st.form_submit_button("✓ Kaydet", use_container_width=True):
                                    try:
                                        selected.name = new_name
                                        selected.description = new_desc if new_desc else None
                                        db.commit()
                                        st.success("✓ Kategori güncellendi!")
                                        st.rerun()
                                    except Exception as e:
                                        st.error(f"✗ Hata: {str(e)}")
                        
                        with col_delete:
                            if st.button("❌ Sil", use_container_width=True, key="del_prod_cat"):
                                try:
                                    # Kontrol: Kategoriye ait ürün var mı?
                                    prod_count = db.query(Product).filter(Product.category_id == selected.id).count()
                                    if prod_count > 0:
                                        st.error(f"✗ Bu kategoriye ait {prod_count} ürün var! Önce ürünleri silin.")
                                    else:
                                        db.delete(selected)
                                        db.commit()
                                        st.success("✓ Kategori silindi!")
                                        st.rerun()
                                except Exception as e:
                                    st.error(f"✗ Hata: {str(e)}")
                else:
                    st.info("Kategori yok")
        
        # ============================================================
        # TAB 3: MASRAF KATEGORİLERİ
        # ============================================================
        with tab3:
            st.subheader("Masraf Kategorileri Yönetimi")

            col1, col2 = st.columns([1, 1], gap="large")

            # Left: list + edit/delete
            with col1:
                st.subheader("📋 Mevcut Masraf Kategorileri")

                expense_cats = db.query(ExpenseCategory).order_by(ExpenseCategory.display_order, ExpenseCategory.name).all()

                if expense_cats:
                    cat_rows = []
                    for c in expense_cats:
                        cat_rows.append({
                            "ID": c.id,
                            "Kod": c.code,
                            "Kategori": c.name,
                            "Açıklama": c.description or "-",
                            "Aktif": "Evet" if c.is_active else "Hayır"
                        })

                    st.dataframe(pd.DataFrame(cat_rows), use_container_width=True, hide_index=True)

                    st.markdown("---")
                    st.subheader("✏️ Düzenle / ❌ Sil")

                    sel = st.selectbox(
                        "Düzenlemek için kategori seçin",
                        options=[c.id for c in expense_cats],
                        format_func=lambda x: next((c.name for c in expense_cats if c.id == x), "")
                    )

                    if sel:
                        selected = next((c for c in expense_cats if c.id == sel), None)
                        if selected:
                            col_e, col_d = st.columns(2)
                            with col_e:
                                with st.form("edit_expense_cat_form"):
                                    new_name = st.text_input("Kategori Adı", value=selected.name)
                                    new_code = st.text_input("Kategori Kodu", value=selected.code).upper()
                                    new_desc = st.text_area("Açıklama", value=selected.description or "", height=80)
                                    new_active = st.checkbox("Aktif", value=selected.is_active)

                                    if st.form_submit_button("✓ Kaydet", use_container_width=True):
                                        try:
                                            # Kod benzersizliği kontrolü
                                            other = db.query(ExpenseCategory).filter(ExpenseCategory.code == new_code, ExpenseCategory.id != selected.id).first()
                                            if other:
                                                st.error(f"✗ '{new_code}' kodu başka bir kategori tarafından kullanılıyor")
                                            else:
                                                selected.name = new_name
                                                selected.code = new_code
                                                selected.description = new_desc if new_desc else None
                                                selected.is_active = bool(new_active)
                                                db.commit()
                                                st.success("✓ Masraf kategorisi güncellendi!")
                                                st.rerun()
                                        except Exception as e:
                                            st.error(f"✗ Hata: {str(e)}")

                            with col_d:
                                if st.button("❌ Sil", use_container_width=True, key="del_exp_cat"):
                                    try:
                                        # Kontrol: Bu kategoriyi kullanan masraf var mı?
                                        ref_count = db.query(Expense).filter(Expense.category == selected.code).count()
                                        if ref_count > 0:
                                            st.error(f"✗ Bu kategoriye ait {ref_count} masraf kaydı var! Önce ilgili masrafları silin veya kategoriyi değiştirin.")
                                        else:
                                            db.delete(selected)
                                            db.commit()
                                            st.success("✓ Masraf kategorisi silindi")
                                            st.rerun()
                                    except Exception as e:
                                        st.error(f"✗ Hata: {str(e)}")
                else:
                    st.info("Masraf kategorisi yok")

            # Right: add new category + info
            with col2:
                st.subheader("➕ Yeni Masraf Kategorisi Ekle")
                with st.form("new_expense_category_form"):
                    name = st.text_input("Kategori Adı *", placeholder="ör: Kira")
                    code = st.text_input("Kategori Kodu *", placeholder="ör: KIRA", max_chars=50).upper()
                    desc = st.text_area("Açıklama", placeholder="Opsiyonel açıklama", height=80)
                    active = st.checkbox("Aktif", value=True)

                    submitted = st.form_submit_button("Kategori Ekle", use_container_width=True)
                    if submitted:
                        if not name or not code:
                            st.error("✗ Kategori adı ve kodu zorunludur!")
                        else:
                            try:
                                exists = db.query(ExpenseCategory).filter((ExpenseCategory.code == code) | (ExpenseCategory.name == name)).first()
                                if exists:
                                    st.error("✗ Aynı isim veya kod zaten mevcut")
                                else:
                                    newc = ExpenseCategory(name=name, code=code, description=desc if desc else None, is_active=bool(active))
                                    db.add(newc)
                                    db.commit()
                                    st.success("✓ Masraf kategorisi eklendi!")
                                    st.rerun()
                            except Exception as e:
                                st.error(f"✗ Hata: {str(e)}")

                st.markdown("---")
                st.subheader("ℹ️ Bilgi")
                st.markdown("""
                Masraf kategorileri artık veritabanında saklanıyor. Uygulamaya eklenen kategoriler buradan yönetilebilir.
                * Kod alanı, masraf kayıtlarında saklanan kısa anahtar (ör: KIRA) olmalıdır.
                """)
    
    finally:
        db.close()
