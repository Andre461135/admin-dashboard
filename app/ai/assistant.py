import re
from datetime import datetime, timezone, timedelta
from app import db
from app.models import User, Product, Sale
from sqlalchemy import func


class AIAssistant:

    def chat(self, message):
        message = message.lower().strip()

        if any(word in message for word in ['hello', 'hi', 'hey', 'greetings']):
            return "Hello! I'm your AI dashboard assistant. I can help with insights, reports, user stats, sales data, and more. Try asking me about recent activity or platform performance."

        if 'user' in message:
            return self._handle_user_query(message)

        if any(word in message for word in ['sale', 'revenue', 'order', 'transaction', 'income']):
            return self._handle_sales_query(message)

        if any(word in message for word in ['product', 'inventory', 'stock', 'item']):
            return self._handle_product_query(message)

        if any(word in message for word in ['report', 'summary', 'overview']):
            return self._handle_report_query(message)

        if any(word in message for word in ['help', 'what can you do', 'commands', 'capabilities']):
            return ("I can help you with:\n"
                    "- User statistics (total users, active users, new registrations)\n"
                    "- Sales data (revenue, transactions, average order value)\n"
                    "- Product info (inventory, categories, stock levels)\n"
                    "- Report summaries (users, sales, products, revenue)\n"
                    "- Platform insights and trends\n"
                    "Try asking specific questions like 'how many users?' or 'what is the revenue?'")

        if any(word in message for word in ['trend', 'growth', 'performance', 'analytics']):
            return self._handle_trend_query()

        return ("I understand you're asking about the dashboard. I can provide insights on users, sales, products, and reports. "
                "Type 'help' to see what I can do, or ask me a specific question about your data.")

    def _handle_user_query(self, message):
        total = User.query.count()
        active = User.query.filter_by(status='active').count()
        new_this_week = User.query.filter(
            User.created_at >= datetime.now(timezone.utc) - timedelta(days=7)
        ).count()
        admins = User.query.filter_by(role='admin').count()

        if 'active' in message:
            return f"There are {active} active users out of {total} total registered users ({total - active} inactive)."
        if 'new' in message or 'recent' in message:
            return f"{new_this_week} new users have joined in the past week."
        if 'admin' in message or 'role' in message:
            return f"There are {admins} administrators on the platform."
        return f"The platform has {total} total users. {active} are active, {new_this_week} joined this week, and there are {admins} administrators."

    def _handle_sales_query(self, message):
        total_sales = Sale.query.count()
        total_revenue = db.session.query(func.sum(Sale.total)).scalar() or 0
        monthly_revenue = db.session.query(func.sum(Sale.total)).filter(
            Sale.created_at >= datetime.now(timezone.utc) - timedelta(days=30)
        ).scalar() or 0
        avg_order = total_revenue / total_sales if total_sales > 0 else 0
        pending = Sale.query.filter_by(status='pending').count()

        if 'revenue' in message:
            return f"Total revenue is ${total_revenue:,.2f}. Monthly revenue: ${monthly_revenue:,.2f}."
        if 'pending' in message:
            return f"There are {pending} pending transactions that need attention."
        if 'average' in message or 'avg' in message:
            return f"The average order value is ${avg_order:.2f}."
        return (f"We've had {total_sales} total sales generating ${total_revenue:,.2f} in revenue. "
                f"Monthly revenue is ${monthly_revenue:,.2f} with an average order of ${avg_order:.2f}. "
                f"{pending} transactions are pending.")

    def _handle_product_query(self, message):
        total = Product.query.count()
        active = Product.query.filter_by(status='active').count()
        low_stock = Product.query.filter(Product.stock < 10).count()
        categories = db.session.query(Product.category).distinct().count()

        if 'category' in message:
            cats = db.session.query(Product.category, func.count(Product.id).label('count')).group_by(Product.category).order_by(func.count(Product.id).desc()).all()
            return "Product categories: " + ", ".join([f"{c.category} ({c.count})" for c in cats])
        if 'stock' in message or 'inventory' in message:
            return f"{total} total products. {low_stock} products have low stock (less than 10 units)."
        return f"The catalog has {total} products across {categories} categories. {active} are active. {low_stock} need restocking."

    def _handle_report_query(self, message):
        return ("I can generate summaries for:\n"
                "- Users: total count, active vs inactive, new registrations\n"
                "- Sales: total transactions, revenue, average order value\n"
                "- Products: catalog size, categories, stock status\n"
                "- Revenue: totals, monthly trends, growth metrics\n"
                "Which report would you like summarized? (users, sales, products, or revenue)")

    def _handle_trend_query(self):
        monthly_revenue = db.session.query(
            func.strftime('%Y-%m', Sale.created_at).label('month'),
            func.sum(Sale.total).label('revenue')
        ).group_by('month').order_by('month').limit(3).all()

        if len(monthly_revenue) >= 2:
            trend = "up" if monthly_revenue[-1].revenue >= monthly_revenue[-2].revenue else "down"
            return (f"Revenue trend is {trend} over the last few months. "
                    f"Latest month: ${monthly_revenue[-1].revenue:,.2f}. "
                    f"Platform is showing {'positive' if trend == 'up' else 'stable'} growth.")
        return "Not enough data to determine trends. Continue using the platform to generate more analytics."
