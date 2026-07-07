from datetime import datetime, timezone, timedelta
from flask import Blueprint, render_template
from flask_login import login_required, current_user
from app import db
from app.models import User, Product, Sale, Activity, Notification, AIInsight
from sqlalchemy import func

dashboard_bp = Blueprint('dashboard', __name__)


@dashboard_bp.route('/')
@dashboard_bp.route('/dashboard')
@login_required
def index():
    total_users = User.query.count()
    total_products = Product.query.count()
    total_sales = Sale.query.count()
    total_revenue = db.session.query(func.sum(Sale.total)).scalar() or 0

    active_users = User.query.filter_by(status='active').count()
    low_stock = Product.query.filter(Product.stock < 10).count()
    pending_sales = Sale.query.filter_by(status='pending').count()

    recent_users = User.query.order_by(User.created_at.desc()).limit(5).all()
    recent_activities = Activity.query.order_by(Activity.created_at.desc()).limit(8).all()
    unread_notifications = Notification.query.filter_by(user_id=current_user.id, is_read=False).count()
    recent_notifications = Notification.query.filter_by(user_id=current_user.id).order_by(Notification.created_at.desc()).limit(5).all()

    insights = AIInsight.query.order_by(AIInsight.created_at.desc()).limit(3).all()

    revenue_data = db.session.query(
        func.strftime('%Y-%m', Sale.created_at).label('month'),
        func.sum(Sale.total).label('revenue')
    ).group_by('month').order_by('month').limit(12).all()

    sales_data = db.session.query(
        func.strftime('%Y-%m-%d', Sale.created_at).label('date'),
        func.count(Sale.id).label('count')
    ).filter(Sale.created_at >= datetime.now(timezone.utc) - timedelta(days=30)
    ).group_by('date').order_by('date').all()

    category_data = db.session.query(
        Product.category,
        func.count(Product.id).label('count')
    ).group_by(Product.category).order_by(func.count(Product.id).desc()).all()

    top_products = db.session.query(
        Product.name,
        func.sum(Sale.total).label('total')
    ).join(Sale).group_by(Product.id).order_by(func.sum(Sale.total).desc()).limit(5).all()

    recent_transactions = Sale.query.order_by(Sale.created_at.desc()).limit(5).all()

    task_progress = [
        {'name': 'User Onboarding', 'progress': 85, 'color': '#4361ee'},
        {'name': 'Product Launch', 'progress': 62, 'color': '#3a0ca3'},
        {'name': 'Q2 Report', 'progress': 45, 'color': '#7209b7'},
        {'name': 'Mobile App', 'progress': 30, 'color': '#f72585'},
    ]

    return render_template('dashboard/index.html',
        total_users=total_users, total_products=total_products,
        total_sales=total_sales, total_revenue=total_revenue,
        active_users=active_users, low_stock=low_stock,
        pending_sales=pending_sales,
        recent_users=recent_users, recent_activities=recent_activities,
        unread_notifications=unread_notifications,
        recent_notifications=recent_notifications,
        insights=insights,
        revenue_data=revenue_data, sales_data=sales_data,
        category_data=category_data,
        top_products=top_products,
        recent_transactions=recent_transactions,
        task_progress=task_progress)


@dashboard_bp.route('/analytics')
@login_required
def analytics():
    return render_template('dashboard/analytics.html',
        total_users=User.query.count(),
        total_products=Product.query.count(),
        total_sales=Sale.query.count(),
        total_revenue=db.session.query(func.sum(Sale.total)).scalar() or 0)
