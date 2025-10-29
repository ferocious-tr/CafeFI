"""
📊 Raporlama Modülü - Satış, Masraf, Kâr Analitiği
Gelişmiş raporlama ve analiz işlemleri
"""

from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from datetime import datetime, timedelta
from decimal import Decimal
from src.models import Sale, Expense, Product, Category, Ingredient, Recipe
import pandas as pd


class ReportsManager:
    """Raporlama Yönetimi - Analitiği"""
    
    # ================================================================
    # SATIŞ ANALİTİĞİ
    # ================================================================
    
    @staticmethod
    def get_sales_trend(db: Session, days: int = 30) -> dict:
        """Son N günün satış trendi (günlük satış sayısı)"""
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        # SQL: Günlük satış sayısı
        daily_sales = db.query(
            func.date(Sale.created_at).label('date'),
            func.count(Sale.id).label('count'),
            func.sum(Sale.total_with_kdv).label('revenue')
        ).filter(
            Sale.created_at >= start_date,
            Sale.created_at <= end_date
        ).group_by(
            func.date(Sale.created_at)
        ).order_by('date').all()
        
        result = {}
        for date, count, revenue in daily_sales:
            result[str(date)] = {
                'count': count or 0,
                'revenue': float(revenue or 0)
            }
        
        return result
    
    @staticmethod
    def get_top_products(db: Session, limit: int = 10) -> list:
        """En çok satılan ürünler"""
        top_products = db.query(
            Product.name,
            func.count(Sale.id).label('sale_count'),
            func.sum(Sale.total_with_kdv).label('total_revenue')
        ).join(
            Sale, Sale.product_id == Product.id
        ).group_by(
            Product.id
        ).order_by(
            desc('sale_count')
        ).limit(limit).all()
        
        result = []
        for name, count, revenue in top_products:
            result.append({
                'name': name,
                'count': count or 0,
                'revenue': float(revenue or 0)
            })
        
        return result
    
    @staticmethod
    def get_category_sales(db: Session) -> dict:
        """Kategoriye göre satış dağılımı"""
        category_sales = db.query(
            Category.name,
            func.count(Sale.id).label('sale_count'),
            func.sum(Sale.total_with_kdv).label('total_revenue')
        ).join(
            Product, Product.category_id == Category.id
        ).join(
            Sale, Sale.product_id == Product.id
        ).group_by(
            Category.id
        ).all()
        
        result = {}
        for name, count, revenue in category_sales:
            result[name] = {
                'count': count or 0,
                'revenue': float(revenue or 0)
            }
        
        return result
    
    @staticmethod
    def get_hourly_sales(db: Session, date: datetime = None) -> dict:
        """Saatlik satış dağılımı"""
        if date is None:
            date = datetime.now().date()
        
        start_dt = datetime.combine(date, datetime.min.time())
        end_dt = datetime.combine(date, datetime.max.time())
        
        hourly_sales = db.query(
            func.strftime('%H', Sale.created_at).label('hour'),
            func.count(Sale.id).label('count')
        ).filter(
            Sale.created_at >= start_dt,
            Sale.created_at <= end_dt
        ).group_by('hour').order_by('hour').all()
        
        result = {}
        for hour, count in hourly_sales:
            result[f"{hour}:00"] = count or 0
        
        return result
    
    @staticmethod
    def get_payment_method_breakdown(db: Session, days: int = 30) -> dict:
        """Ödeme yöntemine göre satışlar"""
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        payment_sales = db.query(
            Sale.payment_method,
            func.count(Sale.id).label('count'),
            func.sum(Sale.total_with_kdv).label('revenue')
        ).filter(
            Sale.created_at >= start_date,
            Sale.created_at <= end_date
        ).group_by(
            Sale.payment_method
        ).all()
        
        result = {}
        for method, count, revenue in payment_sales:
            result[method or "Belirtilmedi"] = {
                'count': count or 0,
                'revenue': float(revenue or 0)
            }
        
        return result
    
    # ================================================================
    # MASRAF ANALİTİĞİ
    # ================================================================
    
    @staticmethod
    def get_expense_breakdown(db: Session, days: int = 30) -> dict:
        """Masraf kategorisine göre dağılım"""
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        expense_data = db.query(
            Expense.category,
            func.sum(Expense.amount).label('total_amount'),
            func.count(Expense.id).label('count')
        ).filter(
            Expense.created_at >= start_date,
            Expense.created_at <= end_date
        ).group_by(
            Expense.category
        ).all()
        
        result = {}
        for category, total, count in expense_data:
            result[category or "Kategorisiz"] = {
                'amount': float(total or 0),
                'count': count or 0
            }
        
        return result
    
    @staticmethod
    def get_expense_trend(db: Session, days: int = 30) -> dict:
        """Masraf trendi (günlük masraflar)"""
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        daily_expenses = db.query(
            func.date(Expense.created_at).label('date'),
            func.sum(Expense.amount).label('total_amount')
        ).filter(
            Expense.created_at >= start_date,
            Expense.created_at <= end_date
        ).group_by(
            func.date(Expense.created_at)
        ).order_by('date').all()
        
        result = {}
        for date, amount in daily_expenses:
            result[str(date)] = float(amount or 0)
        
        return result
    
    # ================================================================
    # KÂR ANALİTİĞİ
    # ================================================================
    
    @staticmethod
    def get_profit_analysis(db: Session, days: int = 30) -> dict:
        """Kâr/Zarar analizi"""
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        # Toplam gelir (satışlar)
        total_revenue_query = db.query(
            func.sum(Sale.total_with_kdv)
        ).filter(
            Sale.created_at >= start_date,
            Sale.created_at <= end_date
        ).scalar()
        total_revenue = float(total_revenue_query or 0)
        
        # Toplam maliyet (ingredient costs)
        total_cost_query = db.query(
            func.sum(Sale.product_cost)
        ).filter(
            Sale.created_at >= start_date,
            Sale.created_at <= end_date
        ).scalar()
        total_cost = float(total_cost_query or 0)
        
        # Toplam masraf
        total_expenses_query = db.query(
            func.sum(Expense.amount)
        ).filter(
            Expense.created_at >= start_date,
            Expense.created_at <= end_date
        ).scalar()
        total_expenses = float(total_expenses_query or 0)
        
        # Hesaplamalar
        gross_profit = total_revenue - total_cost
        net_profit = gross_profit - total_expenses
        profit_margin = (gross_profit / total_revenue * 100) if total_revenue > 0 else 0
        
        return {
            'total_revenue': total_revenue,
            'total_cost': total_cost,
            'total_expenses': total_expenses,
            'gross_profit': gross_profit,
            'net_profit': net_profit,
            'profit_margin': round(profit_margin, 2)
        }
    
    @staticmethod
    def get_daily_profit(db: Session, days: int = 30) -> dict:
        """Günlük kâr"""
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        # Günlük satış ve maliyetler
        daily_data = db.query(
            func.date(Sale.created_at).label('date'),
            func.sum(Sale.total_with_kdv).label('revenue'),
            func.sum(Sale.product_cost).label('cost')
        ).filter(
            Sale.created_at >= start_date,
            Sale.created_at <= end_date
        ).group_by(
            func.date(Sale.created_at)
        ).all()
        
        result = {}
        for date, revenue, cost in daily_data:
            gross_profit = float(revenue or 0) - float(cost or 0)
            result[str(date)] = gross_profit
        
        return result
    
    # ================================================================
    # STOK ANALİTİĞİ
    # ================================================================
    
    @staticmethod
    def get_stock_value(db: Session) -> dict:
        """Toplam stok değeri (malzeme bazında)"""
        ingredients = db.query(Ingredient).filter(
            Ingredient.is_active == True
        ).all()
        
        result = {}
        for ing in ingredients:
            total_value = ing.quantity * ing.cost_per_unit
            result[ing.name] = {
                'quantity': ing.quantity,
                'unit': ing.unit,
                'cost_per_unit': float(ing.cost_per_unit),
                'total_value': float(total_value)
            }
        
        return result
    
    @staticmethod
    def get_stock_value_total(db: Session) -> float:
        """Toplam stok değeri (tek sayı)"""
        total = db.query(
            func.sum(Ingredient.quantity * Ingredient.cost_per_unit)
        ).filter(
            Ingredient.is_active == True
        ).scalar()
        
        return float(total or 0)
    
    @staticmethod
    def get_low_stock_items(db: Session, threshold: float = 100) -> list:
        """Düşük stok malzemeleri"""
        low_items = db.query(Ingredient).filter(
            Ingredient.quantity < threshold,
            Ingredient.is_active == True
        ).order_by(Ingredient.quantity).all()
        
        result = []
        for ing in low_items:
            result.append({
                'name': ing.name,
                'quantity': ing.quantity,
                'unit': ing.unit,
                'threshold': threshold,
                'status': '⚠️ Kritik' if ing.quantity < threshold * 0.5 else '⚠️ Düşük'
            })
        
        return result
    
    # ================================================================
    # GENEL METRİKLER
    # ================================================================
    
    @staticmethod
    def get_summary_metrics(db: Session, start_date: datetime, end_date: datetime) -> dict:
        """Dönem özet metrikleri"""
        # Satış sayısı ve gelir
        sales_data = db.query(
            func.count(Sale.id).label('count'),
            func.sum(Sale.total_with_kdv).label('revenue'),
            func.avg(Sale.total_with_kdv).label('avg_value')
        ).filter(
            Sale.created_at >= start_date,
            Sale.created_at <= end_date
        ).first()
        
        # Masraf toplamı
        total_expenses = db.query(
            func.sum(Expense.amount)
        ).filter(
            Expense.created_at >= start_date,
            Expense.created_at <= end_date
        ).scalar() or 0
        
        # Ürün maliyeti toplamı
        total_cost = db.query(
            func.sum(Sale.product_cost)
        ).filter(
            Sale.created_at >= start_date,
            Sale.created_at <= end_date
        ).scalar() or 0
        
        total_sales = sales_data.count or 0
        total_revenue = float(sales_data.revenue or 0)
        avg_sale = float(sales_data.avg_value or 0)
        total_expenses = float(total_expenses)
        total_cost = float(total_cost)
        gross_profit = total_revenue - total_cost
        net_profit = gross_profit - total_expenses
        
        return {
            'total_sales': total_sales,
            'total_revenue': total_revenue,
            'avg_sale_value': avg_sale,
            'total_cost': total_cost,
            'total_expenses': total_expenses,
            'gross_profit': gross_profit,
            'net_profit': net_profit,
            'profit_margin': round((gross_profit / total_revenue * 100) if total_revenue > 0 else 0, 2)
        }
    
    @staticmethod
    def get_product_profitability(db: Session, limit: int = 20) -> list:
        """Ürün kârlılık analizi"""
        product_profits = db.query(
            Product.name,
            func.count(Sale.id).label('sales_count'),
            func.sum(Sale.total_with_kdv).label('revenue'),
            func.sum(Sale.product_cost).label('cost')
        ).join(
            Sale, Sale.product_id == Product.id
        ).group_by(
            Product.id
        ).order_by(
            desc('revenue')
        ).limit(limit).all()
        
        result = []
        for name, count, revenue, cost in product_profits:
            revenue = float(revenue or 0)
            cost = float(cost or 0)
            profit = revenue - cost
            margin = (profit / revenue * 100) if revenue > 0 else 0
            
            result.append({
                'product': name,
                'sales': count or 0,
                'revenue': revenue,
                'cost': cost,
                'profit': profit,
                'margin': round(margin, 2)
            })
        
        return result
    
    @staticmethod
    def get_monthly_comparison(db: Session, months: int = 3) -> dict:
        """Aylık karşılaştırma"""
        today = datetime.now()
        result = {}
        
        for i in range(months):
            month_start = (today - timedelta(days=30*i)).replace(day=1)
            month_end = (month_start + timedelta(days=32)).replace(day=1) - timedelta(days=1)
            
            month_str = month_start.strftime('%Y-%m')
            
            # Bu ay için metrikleri al
            metrics = ReportsManager.get_summary_metrics(db, month_start, month_end)
            result[month_str] = metrics
        
        return result
    
    # ================================================================
    # ÖZELLİK: DATAFRAME DÖNÜŞTÜRME
    # ================================================================
    
    @staticmethod
    def sales_to_dataframe(db: Session, days: int = 30) -> 'pd.DataFrame':
        """Satışları DataFrame'e dönüştür"""
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        sales = db.query(
            Sale.id,
            Sale.created_at,
            Product.name.label('product'),
            Sale.quantity,
            Sale.total_with_kdv
        ).join(
            Product, Sale.product_id == Product.id
        ).filter(
            Sale.created_at >= start_date,
            Sale.created_at <= end_date
        ).order_by(desc(Sale.created_at)).all()
        
        data = {
            'ID': [s.id for s in sales],
            'Tarih': [s.created_at for s in sales],
            'Ürün': [s.product for s in sales],
            'Miktar': [s.quantity for s in sales],
            'Toplam': [f"₺{s.total_with_kdv:.2f}" for s in sales]
        }
        
        return pd.DataFrame(data)
    
    @staticmethod
    def expenses_to_dataframe(db: Session, days: int = 30) -> 'pd.DataFrame':
        """Masrafları DataFrame'e dönüştür"""
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        expenses = db.query(
            Expense.id,
            Expense.created_at,
            Category.name.label('category'),
            Expense.amount,
            Expense.notes
        ).join(
            Category, Expense.category_id == Category.id
        ).filter(
            Expense.created_at >= start_date,
            Expense.created_at <= end_date
        ).order_by(desc(Expense.created_at)).all()
        
        data = {
            'ID': [e.id for e in expenses],
            'Tarih': [e.created_at for e in expenses],
            'Kategori': [e.category for e in expenses],
            'Miktar': [f"₺{e.amount:.2f}" for e in expenses],
            'Notlar': [e.notes or "-" for e in expenses]
        }
        
        return pd.DataFrame(data)
