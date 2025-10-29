"""
💰 CafeFlow - Masraf Takibi Modülü

Sabit ve değişken masrafları takip eder, CRUD işlemleri ve raporlama
"""

import streamlit as st
from datetime import datetime, timedelta
import pandas as pd
from sqlalchemy.orm import Session
from sqlalchemy import func
from src.database import DatabaseEngine
from src.models import Expense, ExpenseCategory
from src.utils.locale_utils import format_currency, format_datetime


def load_expense_categories(db: Session) -> dict:
    """Return mapping of expense category code -> display name.

    Falls back to Expense.EXPENSE_CATEGORIES if DB table is empty.
    """
    try:
        rows = db.query(ExpenseCategory).order_by(ExpenseCategory.display_order, ExpenseCategory.name).all()
        if rows:
            return {r.code: r.name for r in rows}
    except Exception:
        # If table doesn't exist or any error, fallback to static dict
        pass

    return Expense.EXPENSE_CATEGORIES


class ExpenseManager:
    """Masraf Takibi İş Mantığı"""
    
    @staticmethod
    def create_expense(
        db: Session,
        description: str,
        category: str,
        amount: float,
        payment_method: str,
        reference_number: str = None,
        is_recurring: bool = False,
        recurring_type: str = None,
        notes: str = None,
    ) -> Expense:
        """
        Yeni masraf ekle
        
        Args:
            db: Veritabanı oturumu
            description: Masraf açıklaması
            category: Kategori
            amount: Tutar
            payment_method: Ödeme yöntemi
            reference_number: Referans numarası
            is_recurring: Tekrarlayan mı?
            recurring_type: Tekrarlama türü
            notes: Notlar
            
        Returns:
            Expense: Oluşturulan masraf nesnesi
        """
        expense = Expense(
            description=description,
            category=category,
            amount=amount,
            payment_method=payment_method,
            reference_number=reference_number,
            is_recurring=is_recurring,
            recurring_type=recurring_type,
            notes=notes
        )
        
        db.add(expense)
        db.commit()
        db.refresh(expense)
        
        return expense
    
    @staticmethod
    def get_all_expenses(db: Session) -> list:
        """
        Tüm masrafları al
        
        Args:
            db: Veritabanı oturumu
            
        Returns:
            list: Masraf listesi
        """
        return db.query(Expense).order_by(Expense.created_at.desc()).all()
    
    @staticmethod
    def get_expenses_by_date_range(
        db: Session,
        start_date: datetime,
        end_date: datetime
    ) -> list:
        """
        Tarih aralığına göre masrafları al
        
        Args:
            db: Veritabanı oturumu
            start_date: Başlangıç tarihi
            end_date: Bitiş tarihi
            
        Returns:
            list: Masraf listesi
        """
        return db.query(Expense).filter(
            Expense.created_at >= start_date,
            Expense.created_at <= end_date
        ).order_by(Expense.created_at.desc()).all()
    
    @staticmethod
    def get_expenses_by_category(
        db: Session,
        category: str,
        start_date: datetime = None,
        end_date: datetime = None
    ) -> list:
        """
        Kategoriye göre masrafları al
        
        Args:
            db: Veritabanı oturumu
            category: Kategori
            start_date: Başlangıç tarihi (isteğe bağlı)
            end_date: Bitiş tarihi (isteğe bağlı)
            
        Returns:
            list: Masraf listesi
        """
        query = db.query(Expense).filter(Expense.category == category)
        
        if start_date:
            query = query.filter(Expense.created_at >= start_date)
        if end_date:
            query = query.filter(Expense.created_at <= end_date)
        
        return query.order_by(Expense.created_at.desc()).all()
    
    @staticmethod
    def update_expense(db: Session, expense_id: int, **kwargs) -> Expense:
        """
        Masrafı güncelle
        
        Args:
            db: Veritabanı oturumu
            expense_id: Masraf ID'si
            **kwargs: Güncellenecek alanlar
            
        Returns:
            Expense: Güncellenen masraf nesnesi
        """
        expense = db.query(Expense).filter(Expense.id == expense_id).first()
        
        if not expense:
            raise ValueError(f"Masraf bulunamadı (ID: {expense_id})")
        
        for key, value in kwargs.items():
            if hasattr(expense, key):
                setattr(expense, key, value)
        
        db.commit()
        db.refresh(expense)
        
        return expense
    
    @staticmethod
    def delete_expense(db: Session, expense_id: int) -> bool:
        """
        Masrafı sil
        
        Args:
            db: Veritabanı oturumu
            expense_id: Masraf ID'si
            
        Returns:
            bool: İşlem başarılı mı?
        """
        expense = db.query(Expense).filter(Expense.id == expense_id).first()
        
        if not expense:
            raise ValueError(f"Masraf bulunamadı (ID: {expense_id})")
        
        db.delete(expense)
        db.commit()
        
        return True
    
    @staticmethod
    def get_total_expenses(
        db: Session,
        start_date: datetime = None,
        end_date: datetime = None
    ) -> float:
        """
        Toplam masrafı hesapla
        
        Args:
            db: Veritabanı oturumu
            start_date: Başlangıç tarihi (isteğe bağlı)
            end_date: Bitiş tarihi (isteğe bağlı)
            
        Returns:
            float: Toplam masraf
        """
        query = db.query(func.sum(Expense.amount))
        
        if start_date:
            query = query.filter(Expense.created_at >= start_date)
        if end_date:
            query = query.filter(Expense.created_at <= end_date)
        
        result = query.scalar()
        return float(result) if result else 0.0
    
    @staticmethod
    def get_expenses_by_category_sum(
        db: Session,
        start_date: datetime = None,
        end_date: datetime = None
    ) -> dict:
        """
        Kategoriye göre masrafları topla
        
        Args:
            db: Veritabanı oturumu
            start_date: Başlangıç tarihi (isteğe bağlı)
            end_date: Bitiş tarihi (isteğe bağlı)
            
        Returns:
            dict: Kategori bazlı masraf toplamı
        """
        query = db.query(
            Expense.category,
            func.sum(Expense.amount).label("total")
        )
        
        if start_date:
            query = query.filter(Expense.created_at >= start_date)
        if end_date:
            query = query.filter(Expense.created_at <= end_date)
        
        query = query.group_by(Expense.category).order_by(func.sum(Expense.amount).desc())
        
        # Load dynamic expense categories (fallback to static mapping)
        cats = load_expense_categories(db)

        result = {}
        for category, total in query.all():
            result[cats.get(category, category)] = float(total)
        
        return result
    
    @staticmethod
    def get_monthly_expenses(db: Session, year: int = None) -> dict:
        """
        Aylık masrafları al
        
        Args:
            db: Veritabanı oturumu
            year: Yıl (isteğe bağlı, varsayılan: cari yıl)
            
        Returns:
            dict: Aylık masraf toplamı
        """
        if not year:
            year = datetime.now().year
        
        query = db.query(
            func.strftime('%m', Expense.created_at).label("month"),
            func.sum(Expense.amount).label("total")
        ).filter(
            func.strftime('%Y', Expense.created_at) == str(year)
        ).group_by(
            func.strftime('%m', Expense.created_at)
        ).order_by("month")
        
        months = {
            "01": "Ocak", "02": "Şubat", "03": "Mart", "04": "Nisan",
            "05": "Mayıs", "06": "Haziran", "07": "Temmuz", "08": "Ağustos",
            "09": "Eylül", "10": "Ekim", "11": "Kasım", "12": "Aralık"
        }
        
        result = {}
        for month_num, total in query.all():
            month_name = months.get(month_num, month_num)
            result[month_name] = float(total)
        
        return result
    
    @staticmethod
    def get_expense_summary(
        db: Session,
        start_date: datetime = None,
        end_date: datetime = None
    ) -> dict:
        """
        Masraf özeti
        
        Args:
            db: Veritabanı oturumu
            start_date: Başlangıç tarihi (isteğe bağlı)
            end_date: Bitiş tarihi (isteğe bağlı)
            
        Returns:
            dict: Masraf özeti
        """
        query = db.query(Expense)
        
        if start_date:
            query = query.filter(Expense.created_at >= start_date)
        if end_date:
            query = query.filter(Expense.created_at <= end_date)
        
        expenses = query.all()
        
        total_amount = sum(float(e.amount) for e in expenses)
        recurring_count = len([e for e in expenses if e.is_recurring])
        non_recurring_count = len([e for e in expenses if not e.is_recurring])
        
        category_summary = ExpenseManager.get_expenses_by_category_sum(db, start_date, end_date)
        
        return {
            "total_count": len(expenses),
            "total_amount": total_amount,
            "recurring_count": recurring_count,
            "non_recurring_count": non_recurring_count,
            "category_summary": category_summary,
            "average_per_day": total_amount / (end_date - start_date).days if end_date and start_date else 0
        }


# ============================================================
# STREAMLIT UI
# ============================================================

def render_expenses_page():
    """Masraf Takibi sayfasını oluştur"""
    
    st.title("💰 Masraf Takibi")
    st.markdown("---")
    
    db = DatabaseEngine.create_session()
    
    try:
        # Tab'lar
        tab1, tab2, tab3, tab4 = st.tabs([
            "📋 Masraf Listesi",
            "➕ Yeni Masraf",
            "📊 Raporlar",
            "✏️ Düzenle/Sil"
        ])
        
        # ============================================================
        # TAB 1: MASRAF LİSTESİ
        # ============================================================
        
        with tab1:
            st.subheader("Masraf Listesi")
            
            # Filtreler
            col1, col2, col3 = st.columns(3)
            
            # Load expense categories (DB-backed if available)
            cats = load_expense_categories(db)

            with col1:
                category_filter = st.selectbox(
                    "Kategori Filtresi",
                    ["Tümü"] + list(cats.values())
                )
            
            with col2:
                payment_filter = st.selectbox(
                    "Ödeme Yöntemi Filtresi",
                    ["Tümü"] + list(Expense.PAYMENT_METHODS.values())
                )
            
            with col3:
                recurring_filter = st.selectbox(
                    "Masraf Türü",
                    ["Tümü", "Tek Seferlik", "Tekrarlayan"]
                )
            
            # Tarih filtresi
            col1, col2 = st.columns(2)
            with col1:
                start_date = st.date_input("Başlangıç Tarihi", value=datetime.now().replace(day=1))
            with col2:
                end_date = st.date_input("Bitiş Tarihi", value=datetime.now())
            
            st.markdown("---")
            
            # Masrafları al
            expenses = ExpenseManager.get_expenses_by_date_range(
                db,
                datetime.combine(start_date, datetime.min.time()),
                datetime.combine(end_date, datetime.max.time())
            )
            
            # Filtrele
            if category_filter != "Tümü":
                category_key = next(
                    (k for k, v in cats.items() if v == category_filter),
                    None
                )
                expenses = [e for e in expenses if e.category == category_key]
            
            if payment_filter != "Tümü":
                payment_key = next(
                    (k for k, v in Expense.PAYMENT_METHODS.items() if v == payment_filter),
                    None
                )
                expenses = [e for e in expenses if e.payment_method == payment_key]
            
            if recurring_filter == "Tekrarlayan":
                expenses = [e for e in expenses if e.is_recurring]
            elif recurring_filter == "Tek Seferlik":
                expenses = [e for e in expenses if not e.is_recurring]
            
            if expenses:
                # Veri tablosu
                expense_data = []
                for expense in expenses:
                    expense_data.append({
                        "ID": expense.id,
                        "Tarih": expense.created_at.strftime("%d.%m.%Y %H:%M"),
                        "Açıklama": expense.description,
                        "Kategori": expense.category_display,
                        "Tutar": format_currency(float(expense.amount)),
                        "Ödeme": expense.payment_method_display,
                        "Referans": expense.reference_number or "-",
                        "Tür": expense.recurring_type_display,
                    })
                
                df = pd.DataFrame(expense_data)
                st.dataframe(df, use_container_width=True, hide_index=True)
                
                # İstatistikler
                st.markdown("---")
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.metric("Toplam Masraf", len(expenses))
                
                with col2:
                    total = sum(float(e.amount) for e in expenses)
                    st.metric("Toplam Tutar", format_currency(total))
                
                with col3:
                    recurring = len([e for e in expenses if e.is_recurring])
                    st.metric("Tekrarlayan", recurring)
                
                with col4:
                    avg = sum(float(e.amount) for e in expenses) / len(expenses)
                    st.metric("Ort. Masraf", format_currency(avg))
            else:
                st.info("Masraf kaydı bulunamadı")
        
        # ============================================================
        # TAB 2: YENİ MASRAF
        # ============================================================
        
        with tab2:
            st.subheader("Yeni Masraf Ekle")
            
            with st.form("new_expense_form"):
                col1, col2 = st.columns(2)
                
                with col1:
                    expense_desc = st.text_input(
                        "Masraf Açıklaması *",
                        placeholder="Örn: Aylık Kira Ödemesi"
                    )
                
                with col2:
                    expense_category = st.selectbox(
                        "Kategori *",
                        list(cats.keys()),
                        format_func=lambda x: cats.get(x, x)
                    )
                
                col1, col2 = st.columns(2)
                
                with col1:
                    expense_amount = st.number_input(
                        "Tutar (₺) *",
                        min_value=0.01,
                        value=1000.00
                    )
                
                with col2:
                    expense_payment = st.selectbox(
                        "Ödeme Yöntemi *",
                        list(Expense.PAYMENT_METHODS.keys()),
                        format_func=lambda x: Expense.PAYMENT_METHODS.get(x, x)
                    )
                
                col1, col2 = st.columns(2)
                
                with col1:
                    expense_reference = st.text_input(
                        "Referans No (Fatura, vb.)",
                        placeholder="Örn: FATURA-2025-001"
                    )
                
                with col2:
                    is_recurring = st.checkbox("Tekrarlayan Masraf mı?")
                
                if is_recurring:
                    col1, col2 = st.columns(2)
                    with col1:
                        recurring_type = st.selectbox(
                            "Tekrarlama Sıklığı",
                            list(Expense.RECURRING_TYPES.keys()),
                            format_func=lambda x: Expense.RECURRING_TYPES.get(x, x)
                        )
                    with col2:
                        st.info("(Sistem hatırlatma gönderecek)")
                else:
                    recurring_type = None
                
                expense_notes = st.text_area(
                    "Notlar",
                    placeholder="Ek bilgiler...",
                    height=100
                )
                
                submitted = st.form_submit_button("➕ Masraf Ekle", use_container_width=True)
                
                if submitted:
                    if not expense_desc or expense_amount <= 0:
                        st.error("Açıklama ve tutar zorunludur!")
                    else:
                        try:
                            ExpenseManager.create_expense(
                                db,
                                description=expense_desc,
                                category=expense_category,
                                amount=expense_amount,
                                payment_method=expense_payment,
                                reference_number=expense_reference if expense_reference else None,
                                is_recurring=is_recurring,
                                recurring_type=recurring_type,
                                notes=expense_notes if expense_notes else None
                            )
                            st.success("✓ Masraf başarıyla eklendi!")
                            st.rerun()
                        except ValueError as e:
                            st.error(f"✗ Hata: {str(e)}")
        
        # ============================================================
        # TAB 3: RAPORLAR
        # ============================================================
        
        with tab3:
            st.subheader("Masraf Raporları")
            
            # Tarih seçimi
            col1, col2 = st.columns(2)
            with col1:
                report_start_date = st.date_input(
                    "Rapor Başlangıç Tarihi",
                    value=datetime.now().replace(day=1),
                    key="report_start"
                )
            with col2:
                report_end_date = st.date_input(
                    "Rapor Bitiş Tarihi",
                    value=datetime.now(),
                    key="report_end"
                )
            
            start_dt = datetime.combine(report_start_date, datetime.min.time())
            end_dt = datetime.combine(report_end_date, datetime.max.time())
            
            st.markdown("---")
            
            # Özet metrikler
            summary = ExpenseManager.get_expense_summary(db, start_dt, end_dt)
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Toplam Masraf", summary["total_count"])
            
            with col2:
                st.metric("Toplam Tutar", format_currency(summary['total_amount']))
            
            with col3:
                st.metric("Tekrarlayan", summary["recurring_count"])
            
            with col4:
                st.metric("Günlük Ort.", format_currency(summary['average_per_day']))
            
            st.markdown("---")
            
            # Kategori bazlı grafik
            st.subheader("Kategori Bazlı Masraflar")
            
            category_data = summary["category_summary"]
            
            if category_data:
                # Tablo
                category_df = pd.DataFrame(
                    list(category_data.items()),
                    columns=["Kategori", "Tutar"]
                )
                category_df["Tutar"] = category_df["Tutar"].apply(lambda x: format_currency(x))
                
                st.dataframe(category_df, use_container_width=True, hide_index=True)
                
                # Grafik
                import matplotlib.pyplot as plt
                
                fig, ax = plt.subplots(figsize=(10, 6))
                categories = list(category_data.keys())
                amounts = list(category_data.values())
                
                colors = plt.cm.Set3(range(len(categories)))
                ax.barh(categories, amounts, color=colors)
                ax.set_xlabel("Tutar (₺)")
                ax.set_title("Kategori Bazlı Masraf Dağılımı")
                
                # Değerleri barların sonuna ekle
                for i, v in enumerate(amounts):
                    ax.text(v, i, f"  ₺{v:.2f}", va="center")
                
                st.pyplot(fig)
            else:
                st.info("Bu dönemde masraf kaydı yok")
            
            st.markdown("---")
            
            # Ödeme yöntemi bazlı
            st.subheader("Ödeme Yöntemi Bazlı Masraflar")
            
            payment_query = db.query(
                Expense.payment_method,
                func.sum(Expense.amount).label("total"),
                func.count(Expense.id).label("count")
            ).filter(
                Expense.created_at >= start_dt,
                Expense.created_at <= end_dt
            ).group_by(Expense.payment_method)
            
            payment_data = []
            for payment_method, total, count in payment_query.all():
                payment_data.append({
                    "Ödeme Yöntemi": Expense.PAYMENT_METHODS.get(payment_method, payment_method),
                    "Toplam Tutar": format_currency(float(total)),
                    "İşlem Sayısı": count
                })
            
            if payment_data:
                st.dataframe(
                    pd.DataFrame(payment_data),
                    use_container_width=True,
                    hide_index=True
                )
            else:
                st.info("Masraf kaydı yok")
        
        # ============================================================
        # TAB 4: DÜZENLE/SİL
        # ============================================================
        
        with tab4:
            st.subheader("Masraf Düzenle / Sil")
            
            # Masraf seç
            all_expenses = ExpenseManager.get_all_expenses(db)
            
            if all_expenses:
                selected_expense_id = st.selectbox(
                    "Masraf Seç",
                    options=[e.id for e in all_expenses],
                    format_func=lambda x: next(
                        (f"{e.created_at.strftime('%d.%m.%Y')} - {e.description} (₺{e.amount})" for e in all_expenses if e.id == x),
                        ""
                    )
                )
                
                selected_expense = next((e for e in all_expenses if e.id == selected_expense_id), None)
                
                if selected_expense:
                    st.markdown("---")
                    
                    col1, col2 = st.columns([2, 1])
                    
                    with col1:
                        st.subheader("Masraf Bilgileri")
                        
                        with st.form("edit_expense_form"):
                            col1, col2 = st.columns(2)
                            
                            with col1:
                                new_desc = st.text_input(
                                    "Açıklama",
                                    value=selected_expense.description
                                )
                            
                            with col2:
                                category_keys = list(Expense.EXPENSE_CATEGORIES.keys())
                                current_category_index = 0
                                if selected_expense.category in category_keys:
                                    current_category_index = category_keys.index(selected_expense.category)
                                
                                new_category = st.selectbox(
                                    "Kategori",
                                    category_keys,
                                    index=current_category_index,
                                    format_func=lambda x: Expense.EXPENSE_CATEGORIES.get(x, x)
                                )
                            
                            col1, col2 = st.columns(2)
                            
                            with col1:
                                new_amount = st.number_input(
                                    "Tutar (₺)",
                                    value=float(selected_expense.amount)
                                )
                            
                            with col2:
                                payment_keys = list(Expense.PAYMENT_METHODS.keys())
                                current_payment_index = 0
                                if selected_expense.payment_method in payment_keys:
                                    current_payment_index = payment_keys.index(selected_expense.payment_method)
                                
                                new_payment = st.selectbox(
                                    "Ödeme Yöntemi",
                                    payment_keys,
                                    index=current_payment_index,
                                    format_func=lambda x: Expense.PAYMENT_METHODS.get(x, x)
                                )
                            
                            new_reference = st.text_input(
                                "Referans No",
                                value=selected_expense.reference_number or ""
                            )
                            
                            new_notes = st.text_area(
                                "Notlar",
                                value=selected_expense.notes or "",
                                height=80
                            )
                            
                            submitted = st.form_submit_button("💾 Güncelle", use_container_width=True)
                            
                            if submitted:
                                try:
                                    ExpenseManager.update_expense(
                                        db,
                                        selected_expense_id,
                                        description=new_desc,
                                        category=new_category,
                                        amount=new_amount,
                                        payment_method=new_payment,
                                        reference_number=new_reference if new_reference else None,
                                        notes=new_notes if new_notes else None
                                    )
                                    st.success("✓ Masraf güncellendi!")
                                    st.rerun()
                                except ValueError as e:
                                    st.error(f"✗ Hata: {str(e)}")
                    
                    st.markdown("---")
                    
                    if st.button("🗑️ Masrafı Sil", use_container_width=True, key="delete_expense"):
                        try:
                            ExpenseManager.delete_expense(db, selected_expense_id)
                            st.success("✓ Masraf silindi!")
                            st.rerun()
                        except ValueError as e:
                            st.error(f"✗ Hata: {str(e)}")
            else:
                st.info("Masraf kaydı yok")
    
    finally:
        db.close()
