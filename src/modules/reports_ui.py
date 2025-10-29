"""
Reports Module - Streamlit UI
Advanced Reporting & Analytics Dashboard
"""

import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from src.database.db_connection import get_db
from src.modules.reports import ReportsManager
from src.utils.locale_utils import format_currency


def render_reports_page():
    """Render the Reports page with 4 tabs: Sales, Ingredients, Expense&Profit, Metrics"""
    
    st.markdown("# 📊 Gelişmiş Raporlama")
    
    db = next(get_db())
    
    # Date range selector
    col1, col2 = st.columns(2)
    with col1:
        start_date = st.date_input("Başlangıç Tarihi", 
                                   value=datetime.now() - timedelta(days=30),
                                   key="start_date")
    with col2:
        end_date = st.date_input("Bitiş Tarihi", 
                                 value=datetime.now(),
                                 key="end_date")
    
    st.divider()
    
    # Create 4 tabs
    tab1, tab2, tab3, tab4 = st.tabs([
        "📊 Satış Analitiği",
        "🧂 Malzeme Raporları",
        "💰 Masraf & Kâr",
        "📈 Genel Metrikler"
    ])
    
    # ============================================================================
    # TAB 1: SALES ANALYTICS
    # ============================================================================
    with tab1:
        st.markdown("## Satış Analitiği")
        
        # Row 1: Sales Trend + Category Sales
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("📈 Satış Trendi (Son 30 gün)")
            sales_trend = ReportsManager.get_sales_trend(db, days=30)
            
            if sales_trend:
                dates = list(sales_trend.keys())
                counts = [sales_trend[d]['count'] for d in dates]
                revenues = [sales_trend[d]['revenue'] for d in dates]
                
                # Streamlit line chart
                chart_data = pd.DataFrame({
                    'Tarih': dates,
                    'Satış Sayısı': counts,
                    'Gelir (₺)': revenues
                })
                
                st.line_chart(chart_data.set_index('Tarih'))
            else:
                st.info("Bu dönemde satış verisi yok")
        
        with col2:
            st.subheader("🏷️ Kategoriye Göre Satışlar")
            category_sales = ReportsManager.get_category_sales(db)
            
            if category_sales:
                categories = list(category_sales.keys())
                revenues = [category_sales[c]['revenue'] for c in categories]
                counts = [category_sales[c]['count'] for c in categories]
                
                chart_data = pd.DataFrame({
                    'Kategori': categories,
                    'Gelir (₺)': revenues,
                    'Satış Sayısı': counts
                })
                
                st.bar_chart(chart_data.set_index('Kategori')[['Gelir (₺)']])
                
                # Show metrics
                st.markdown("### Kategori Detayları")
                for cat in categories:
                    col_a, col_b = st.columns(2)
                    with col_a:
                        st.metric(f"{cat} - Gelir", format_currency(category_sales[cat]['revenue']))
                    with col_b:
                        st.metric(f"{cat} - Satış", f"{category_sales[cat]['count']} adet")
            else:
                st.info("Kategori verisi yok")
        
        # Row 2: Top Products
        st.subheader("🏆 En Çok Satılan Ürünler (Top 10)")
        top_products = ReportsManager.get_top_products(db, limit=10)
        
        if top_products:
            products_df = pd.DataFrame(top_products)
            products_df = products_df.rename(columns={
                'name': 'Ürün Adı',
                'count': 'Satış Sayısı',
                'revenue': 'Gelir (₺)'
            })
            
            # Bar chart
            chart_data = pd.DataFrame({
                'Ürün': products_df['Ürün Adı'],
                'Satış': products_df['Satış Sayısı']
            })
            st.bar_chart(chart_data.set_index('Ürün'))
            
            # Table
            st.dataframe(products_df, use_container_width=True, hide_index=True)
        else:
            st.info("Satış verisi yok")
        
        # Row 3: Payment Method Breakdown
        st.subheader("💳 Ödeme Yöntemi Dağılımı")
        payment_breakdown = ReportsManager.get_payment_method_breakdown(db, days=30)
        
        if payment_breakdown:
            payment_df = pd.DataFrame([
                {
                    'Ödeme Yöntemi': method,
                    'Toplam (₺)': payment_breakdown[method]['revenue'],
                    'Satış Sayısı': payment_breakdown[method]['count']
                }
                for method in payment_breakdown.keys()
            ])
            
            col1, col2 = st.columns(2)
            with col1:
                st.dataframe(payment_df, use_container_width=True, hide_index=True)
            
            with col2:
                # Metrics
                for idx, row in payment_df.iterrows():
                    st.metric(
                        row['Ödeme Yöntemi'],
                        format_currency(row['Toplam (₺)']),
                        f"{row['Satış Sayısı']} adet"
                    )
    
    # ============================================================================
    # TAB 2: INGREDIENT REPORTS
    # ============================================================================
    with tab2:
        st.markdown("## Malzeme Raporları")
        
        # Row 1: Stock Value
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("📦 Toplam Stok Değeri")
            stock_value_detail = ReportsManager.get_stock_value(db)
            total_value = ReportsManager.get_stock_value_total(db)
            
            st.metric("Toplam Değer", format_currency(total_value))
            
            if stock_value_detail:
                stock_df = pd.DataFrame([
                    {
                        'Malzeme': name,
                        'Miktar': f"{data['quantity']:.2f} {data['unit']}",
                        'Birim Fiyat': format_currency(data['cost_per_unit']),
                        'Toplam': format_currency(data['total_value'])
                    }
                    for name, data in stock_value_detail.items()
                ])
                st.dataframe(stock_df, use_container_width=True, hide_index=True)
        
        with col2:
            st.subheader("⚠️ Düşük Stok Uyarıları")
            low_stock = ReportsManager.get_low_stock_items(db, threshold=100)
            
            if low_stock:
                st.warning(f"⚠️ {len(low_stock)} malzeme kritik stok seviyesinde!")
                
                low_stock_df = pd.DataFrame([
                    {
                        'Malzeme': item['name'],
                        'Mevcut': f"{item['quantity']:.2f} {item['unit']}",
                        'Eşik': f"{item['threshold']:.2f} {item['unit']}",
                        'Durum': item['status']
                    }
                    for item in low_stock
                ])
                st.dataframe(low_stock_df, use_container_width=True, hide_index=True)
            else:
                st.success("✅ Tüm malzemelerin stok seviyesi iyidir")
    
    # ============================================================================
    # TAB 3: EXPENSE & PROFIT ANALYSIS
    # ============================================================================
    with tab3:
        st.markdown("## Masraf & Kâr Analizi")
        
        # Row 1: Expense Breakdown
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("💸 Masraf Dağılımı")
            expense_breakdown = ReportsManager.get_expense_breakdown(db, days=30)
            
            if expense_breakdown:
                categories = list(expense_breakdown.keys())
                amounts = [expense_breakdown[c]['amount'] for c in categories]
                
                expense_df = pd.DataFrame({
                    'Kategori': categories,
                    'Masraf (₺)': amounts
                })
                
                st.bar_chart(expense_df.set_index('Kategori'))
                
                # Detailed table
                detail_rows = []
                for cat in categories:
                    detail_rows.append({
                        'Kategori': cat,
                        'Toplam Masraf': format_currency(expense_breakdown[cat]['amount']),
                        'İşlem Sayısı': expense_breakdown[cat]['count']
                    })
                
                st.dataframe(
                    pd.DataFrame(detail_rows),
                    use_container_width=True,
                    hide_index=True
                )
            else:
                st.info("Masraf verisi yok")
        
        with col2:
            st.subheader("📉 Masraf Trendi (Son 30 gün)")
            expense_trend = ReportsManager.get_expense_trend(db, days=30)
            
            if expense_trend:
                dates = list(expense_trend.keys())
                amounts = [expense_trend[d] for d in dates]
                
                trend_df = pd.DataFrame({
                    'Tarih': dates,
                    'Masraf (₺)': amounts
                })
                
                st.line_chart(trend_df.set_index('Tarih'))
            else:
                st.info("Masraf trendi verisi yok")
        
        # Row 2: Profit Analysis
        st.subheader("💰 Kâr Metrikleri (Son 30 gün)")
        profit_analysis = ReportsManager.get_profit_analysis(db, days=30)
        
        if profit_analysis:
            # Metrics in columns
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric(
                    "Toplam Gelir",
                    format_currency(profit_analysis['total_revenue'])
                )
            
            with col2:
                st.metric(
                    "Toplam Masraf",
                    format_currency(profit_analysis['total_expenses'])
                )
            
            with col3:
                st.metric(
                    "Net Kâr",
                    format_currency(profit_analysis['net_profit'])
                )
            
            with col4:
                st.metric(
                    "Kâr Marjı",
                    f"{profit_analysis['profit_margin']:.1f}%"
                )
        
        # Row 3: Daily Profit Trend
        st.subheader("📊 Günlük Kâr Trendi")
        daily_profit = ReportsManager.get_daily_profit(db, days=30)
        
        if daily_profit:
            dates = list(daily_profit.keys())
            profits = [daily_profit[d] for d in dates]
            
            profit_df = pd.DataFrame({
                'Tarih': dates,
                'Kâr (₺)': profits
            })
            
            st.area_chart(profit_df.set_index('Tarih'))
    
    # ============================================================================
    # TAB 4: GENERAL METRICS
    # ============================================================================
    with tab4:
        st.markdown("## Genel Metrikler & Özet")
        
        # Summary Metrics
        st.subheader("📈 Kilit Performans Göstergeleri (KPI)")
        
        summary_metrics = ReportsManager.get_summary_metrics(
            db,
            start_date=start_date,
            end_date=end_date
        )
        
        if summary_metrics:
            col1, col2, col3, col4, col5 = st.columns(5)
            
            with col1:
                st.metric(
                    "Toplam Satış",
                    f"{summary_metrics['total_sales']} adet"
                )
            
            with col2:
                st.metric(
                    "Toplam Gelir",
                    format_currency(summary_metrics['total_revenue'])
                )
            
            with col3:
                st.metric(
                    "Ort. Satış",
                    format_currency(summary_metrics['avg_sale_value'])
                )
            
            with col4:
                st.metric(
                    "Net Kâr",
                    format_currency(summary_metrics['net_profit'])
                )
            
            with col5:
                st.metric(
                    "Kâr Marjı",
                    f"{summary_metrics['profit_margin']:.1f}%"
                )
        
        # Product Profitability Analysis
        st.subheader("🎯 Ürün Kârlılık Analizi")
        profitability = ReportsManager.get_product_profitability(db, limit=20)
        
        if profitability:
            profit_df = pd.DataFrame([
                {
                    'Ürün': item['product'],
                    'Satış Sayısı': item['sales'],
                    'Toplam Gelir': format_currency(item['revenue']),
                    'Toplam Maliyeti': format_currency(item['cost']),
                    'Kâr': format_currency(item['profit']),
                    'Marj %': f"{item['margin']:.1f}%"
                }
                for item in profitability
            ])
            
            st.dataframe(profit_df, use_container_width=True, hide_index=True)
        else:
            st.info("Ürün kârlılık verisi yok")
        
        # Monthly Comparison
        st.subheader("📅 Aylık Karşılaştırma (Son 3 Ay)")
        monthly_comparison = ReportsManager.get_monthly_comparison(db, months=3)
        
        if monthly_comparison:
            monthly_data = []
            for month_str, metrics in sorted(monthly_comparison.items(), reverse=True):
                monthly_data.append({
                    'Ay': month_str,
                    'Satış Sayısı': metrics.get('total_sales', 0),
                    'Gelir': format_currency(metrics.get('total_revenue', 0)),
                    'Masraf': format_currency(metrics.get('total_expenses', 0)),
                    'Kâr': format_currency(metrics.get('net_profit', 0))
                })
            
            monthly_df = pd.DataFrame(monthly_data)
            st.dataframe(monthly_df, use_container_width=True, hide_index=True)
        else:
            st.info("Aylık karşılaştırma verisi yok")
