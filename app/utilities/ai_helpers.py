"""
AI Assistant module for generating insights, summaries, and predictions.
Designed to be easily connected to OpenAI or any LLM API by replacing
the _call_llm method with an actual API call.
"""

import random
import re
from datetime import datetime, timedelta
from app.models.models import User, Product, Transaction, Activity, db


class AIAssistant:
    """AI-powered assistant for dashboard insights and automation.

    To connect to OpenAI, replace the _call_llm method with:
        import openai
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content
    """

    @staticmethod
    def _call_llm(prompt):
        """Mock LLM call. Replace with actual API call for real AI."""
        return None

    @staticmethod
    def dashboard_insights():
        """Generate contextual insights about the current dashboard state."""
        user_count = User.query.count()
        product_count = Product.query.count()
        total_revenue = db.session.query(db.func.sum(Transaction.amount)).filter(
            Transaction.status == 'completed'
        ).scalar() or 0
        active_users = User.query.filter_by(status='active').count()
        low_stock = Product.query.filter(Product.stock < 20).count()

        insights = []
        if total_revenue > 5000:
            insights.append("Revenue is strong this period. Consider increasing marketing spend.")
        elif total_revenue < 1000:
            insights.append("Revenue is lower than expected. A promotional campaign may help boost sales.")

        if active_users > user_count * 0.7:
            insights.append(f"User engagement is high with {active_users} active users out of {user_count} total.")
        else:
            insights.append(f"Only {active_users} out of {user_count} users are active. Consider a re-engagement campaign.")

        if low_stock > 2:
            insights.append(f"{low_stock} products have low stock levels. Restock soon to avoid lost sales.")

        if user_count > 5:
            insights.append(f"Your user base has grown to {user_count} users. Great momentum!")

        if not insights:
            insights.append("Dashboard is performing normally. All metrics are within expected ranges.")

        return insights

    @staticmethod
    def sales_summary():
        """Generate a natural-language summary of sales performance."""
        total = db.session.query(db.func.sum(Transaction.amount)).filter(
            Transaction.status == 'completed'
        ).scalar() or 0
        count = Transaction.query.filter_by(status='completed').count()
        avg = total / count if count > 0 else 0
        recent = Transaction.query.filter(
            Transaction.status == 'completed',
            Transaction.created_at >= datetime.utcnow() - timedelta(days=7)
        ).count()

        summary = f"Total revenue is ${total:.2f} across {count} completed transactions, "
        summary += f"with an average order value of ${avg:.2f}. "
        summary += f"In the last 7 days, there have been {recent} new transactions."

        if count > 0:
            top_product = db.session.query(Product.name, db.func.count(Transaction.id).label('cnt')).join(
                Transaction, Transaction.product_id == Product.id
            ).filter(Transaction.status == 'completed').group_by(Product.id).order_by(
                db.desc('cnt')
            ).first()
            if top_product:
                summary += f" Top selling product: {top_product.name}."

        return summary

    @staticmethod
    def smart_search(query):
        """Search across users, products, and transactions intelligently."""
        results = {'users': [], 'products': [], 'transactions': []}
        if not query or len(query.strip()) < 2:
            return results

        q = f"%{query}%"
        results['users'] = User.query.filter(
            db.or_(User.username.ilike(q), User.email.ilike(q))
        ).limit(5).all()

        results['products'] = Product.query.filter(
            db.or_(Product.name.ilike(q), Product.category.ilike(q))
        ).limit(5).all()

        results['transactions'] = Transaction.query.join(User).filter(
            db.or_(User.username.ilike(q), User.email.ilike(q))
        ).limit(5).all()

        return results

    @staticmethod
    def report_summary(report_type, data):
        """Generate a concise summary of report data."""
        if report_type == 'users':
            total = len(data)
            active = sum(1 for u in data if u.get('status') == 'active')
            return f"User report covers {total} users. {active} are currently active ({active/total*100:.0f}% engagement rate)." if total else "No user data available."

        if report_type == 'sales':
            total_amount = sum(float(t.get('amount', 0)) for t in data)
            count = len(data)
            return f"Sales report: {count} transactions totaling ${total_amount:.2f}." if count else "No sales data available."

        if report_type == 'products':
            total = len(data)
            categories = len(set(p.get('category') for p in data if p.get('category')))
            return f"Product catalog has {total} items across {categories} categories." if total else "No products in catalog."

        if report_type == 'revenue':
            total = sum(float(r.get('amount', 0)) for r in data)
            return f"Total revenue reported: ${total:.2f}." if data else "No revenue data available."

        return "Report summary generated successfully."

    @staticmethod
    def trend_analysis():
        """Analyze sales trends over the past 30 days."""
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        transactions = Transaction.query.filter(
            Transaction.created_at >= thirty_days_ago,
            Transaction.status == 'completed'
        ).order_by(Transaction.created_at).all()

        if not transactions:
            return "Insufficient transaction data for trend analysis in the last 30 days."

        daily_revenue = {}
        for t in transactions:
            day = t.created_at.strftime('%Y-%m-%d')
            daily_revenue[day] = daily_revenue.get(day, 0) + t.amount

        days = list(daily_revenue.keys())[-7:]
        if len(days) < 2:
            return "Not enough daily data points for trend analysis."

        recent_values = [daily_revenue[d] for d in days]
        trend = "upward" if recent_values[-1] > recent_values[0] else "downward"
        change_pct = ((recent_values[-1] - recent_values[0]) / recent_values[0] * 100) if recent_values[0] > 0 else 0

        return f"Sales show a {trend} trend over the last {len(days)} days with a {change_pct:+.1f}% change in daily revenue."

    @staticmethod
    def chatbot_response(message):
        """Simple rule-based chatbot. Replace _call_llm for AI-powered responses."""
        msg = message.lower().strip()

        if re.search(r'\b(hi|hello|hey)\b', msg):
            return "Hello! I'm your AI dashboard assistant. How can I help you today?"

        if re.search(r'\b(revenue|sales|income)\b', msg):
            total = db.session.query(db.func.sum(Transaction.amount)).filter(
                Transaction.status == 'completed'
            ).scalar() or 0
            return f"Total completed revenue is currently ${total:.2f}."

        if re.search(r'\b(user|customer)\b', msg):
            count = User.query.count()
            active = User.query.filter_by(status='active').count()
            return f"We have {count} total users, with {active} currently active."

        if re.search(r'\b(product|item|inventory)\b', msg):
            count = Product.query.count()
            low = Product.query.filter(Product.stock < 20).count()
            return f"There are {count} products in the catalog. {low} products have low stock."

        if re.search(r'\b(help|what can you do)\b', msg):
            return ("I can help with: dashboard insights, sales summaries, "
                    "trend analysis, user statistics, product information, and report generation. "
                    "Try asking about revenue, users, products, or trends!")

        if re.search(r'\b(thank|thanks)\b', msg):
            return "You're welcome! Let me know if you need anything else."

        if re.search(r'\b(trend|analytics|analys)\b', msg):
            return AIAssistant.trend_analysis()

        llm_response = AIAssistant._call_llm(message)
        if llm_response:
            return llm_response

        return ("I understand your query about '" + message + "'. To get the best results, "
                "try asking about: revenue, users, products, trends, or type 'help' to see what I can do.")
