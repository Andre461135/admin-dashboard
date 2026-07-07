from datetime import datetime, timedelta
from flask import Blueprint, render_template
from flask_login import login_required, current_user
from app.models.models import db, User, Product, Transaction, Activity, Notification
from app.utilities.ai_helpers import AIAssistant

dashboard_bp = Blueprint('dashboard', __name__)


@dashboard_bp.route('/')
@dashboard_bp.route('/dashboard')
@login_required
def index():
    user_count = User.query.count()
    product_count = Product.query.count()
    total_revenue = db.session.query(db.func.sum(Transaction.amount)).filter(
        Transaction.status == 'completed'
    ).scalar() or 0
    transaction_count = Transaction.query.filter_by(status='completed').count()

    active_users = User.query.filter_by(status='active').count()
    low_stock = Product.query.filter(Product.stock < 20).count()
    pending_orders = Transaction.query.filter_by(status='pending').count()
    recent_activities = Activity.query.order_by(Activity.created_at.desc()).limit(10).all()
    notifications = Notification.query.filter_by(is_read=False).order_by(
        Notification.created_at.desc()
    ).limit(5).all()

    recent_users = User.query.order_by(User.created_at.desc()).limit(5).all()
    recent_transactions = Transaction.query.order_by(Transaction.created_at.desc()).limit(5).all()

    revenue_data = _get_revenue_chart_data()
    insights = AIAssistant.dashboard_insights()

    return render_template('dashboard.html',
                           user_count=user_count,
                           product_count=product_count,
                           total_revenue=total_revenue,
                           transaction_count=transaction_count,
                           active_users=active_users,
                           low_stock=low_stock,
                           pending_orders=pending_orders,
                           recent_activities=recent_activities,
                           notifications=notifications,
                           recent_users=recent_users,
                           recent_transactions=recent_transactions,
                           revenue_data=revenue_data,
                           insights=insights)


def _get_revenue_chart_data():
    labels = []
    values = []
    for i in range(6, -1, -1):
        day = datetime.utcnow() - timedelta(days=i)
        label = day.strftime('%a')
        day_start = datetime(day.year, day.month, day.day)
        day_end = day_start + timedelta(days=1)
        total = db.session.query(db.func.sum(Transaction.amount)).filter(
            Transaction.status == 'completed',
            Transaction.created_at >= day_start,
            Transaction.created_at < day_end
        ).scalar() or 0
        labels.append(label)
        values.append(round(total, 2))
    return {'labels': labels, 'values': values}
