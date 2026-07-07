from datetime import datetime, timezone, timedelta
from app import db
from app.models import User, Product, Sale, AIInsight
from sqlalchemy import func


class AIAnalyzer:

    def generate_insights(self):
        insights = []
        total_users = User.query.count()
        total_products = Product.query.count()
        total_sales = Sale.query.count()
        total_revenue = db.session.query(func.sum(Sale.total)).scalar() or 0

        recent_users = User.query.filter(
            User.created_at >= datetime.now(timezone.utc) - timedelta(days=7)
        ).count()

        if recent_users > 5:
            insights.append({
                'title': 'User Growth Spike',
                'content': f'User registrations have increased significantly this week with {recent_users} new users. This represents strong platform growth.',
                'confidence': 0.85,
                'type': 'growth'
            })

        low_stock = Product.query.filter(Product.stock < 10).count()
        if low_stock > 3:
            insights.append({
                'title': 'Inventory Alert',
                'content': f'{low_stock} products are running low on stock. Consider restocking to prevent lost sales.',
                'confidence': 0.92,
                'type': 'warning'
            })

        inactive_users = User.query.filter_by(status='inactive').count()
        if inactive_users > 3:
            insights.append({
                'title': 'User Engagement Opportunity',
                'content': f'{inactive_users} users have inactive accounts. A re-engagement email campaign could help reactivate them.',
                'confidence': 0.78,
                'type': 'opportunity'
            })

        if total_revenue > 0:
            monthly_revenue = db.session.query(func.sum(Sale.total)).filter(
                Sale.created_at >= datetime.now(timezone.utc) - timedelta(days=30)
            ).scalar() or 0

            avg_order = total_revenue / total_sales if total_sales > 0 else 0

            insights.append({
                'title': 'Revenue Performance',
                'content': f'Monthly revenue is ${monthly_revenue:,.2f} with an average order value of ${avg_order:.2f}. Total platform revenue: ${total_revenue:,.2f}.',
                'confidence': 0.95,
                'type': 'metric'
            })

        top_category = db.session.query(
            Product.category,
            func.sum(Sale.total).label('revenue')
        ).join(Sale).group_by(Product.category).order_by(func.sum(Sale.total).desc()).first()

        if top_category:
            insights.append({
                'title': 'Top Performing Category',
                'content': f'"{top_category.category}" is the best-selling category with ${top_category.revenue:,.2f} in revenue.',
                'confidence': 0.88,
                'type': 'insight'
            })

        saved = []
        for ins in insights[:5]:
            existing = AIInsight(
                insight_type=ins['type'],
                title=ins['title'],
                content=ins['content'],
                confidence=ins['confidence']
            )
            db.session.add(existing)
            saved.append(ins)

        db.session.commit()
        return saved

    def generate_sales_summary(self):
        total_sales = Sale.query.count()
        total_revenue = db.session.query(func.sum(Sale.total)).scalar() or 0
        avg_order = total_revenue / total_sales if total_sales > 0 else 0

        today_sales = Sale.query.filter(
            Sale.created_at >= datetime.now(timezone.utc).replace(hour=0, minute=0, second=0)
        ).count()

        return (
            f"We've processed {total_sales} total transactions generating ${total_revenue:,.2f} in revenue. "
            f"The average order value is ${avg_order:.2f}. "
            f"Today we have {today_sales} new transactions. "
            f"Platform is performing well with consistent sales activity."
        )

    def generate_report_summary(self, report_type):
        if report_type == 'users':
            total = User.query.count()
            active = User.query.filter_by(status='active').count()
            admins = User.query.filter_by(role='admin').count()
            return f"The platform has {total} registered users. {active} are currently active. There are {admins} administrators. User base has been growing steadily."
        elif report_type == 'sales':
            total = Sale.query.count()
            revenue = db.session.query(func.sum(Sale.total)).scalar() or 0
            completed = Sale.query.filter_by(status='completed').count()
            return f"There have been {total} total sales transactions. {completed} were completed successfully. Total revenue generated: ${revenue:,.2f}."
        elif report_type == 'products':
            total = Product.query.count()
            active_prods = Product.query.filter_by(status='active').count()
            low_stock = Product.query.filter(Product.stock < 10).count()
            return f"The catalog contains {total} products. {active_prods} are currently active. {low_stock} products need restocking soon."
        elif report_type == 'revenue':
            revenue = db.session.query(func.sum(Sale.total)).scalar() or 0
            monthly = db.session.query(func.sum(Sale.total)).filter(
                Sale.created_at >= datetime.now(timezone.utc) - timedelta(days=30)
            ).scalar() or 0
            return f"Total platform revenue is ${revenue:,.2f}. Monthly revenue stands at ${monthly:,.2f}. Revenue trends show positive growth."
        return "Report analysis completed."
