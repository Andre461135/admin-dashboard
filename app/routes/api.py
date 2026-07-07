import json
from datetime import datetime, timezone, timedelta
from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user
from app import db
from app.models import User, Product, Sale, Activity, Notification, AIInsight
from app.ai.insights import AIAnalyzer
from app.ai.assistant import AIAssistant
from sqlalchemy import func

api_bp = Blueprint('api', __name__)
ai_analyzer = AIAnalyzer()
ai_assistant = AIAssistant()


@api_bp.route('/stats')
@login_required
def stats():
    now = datetime.now(timezone.utc)
    month_start = now.replace(day=1)

    total_users = User.query.count()
    total_products = Product.query.count()
    total_sales = Sale.query.count()
    total_revenue = db.session.query(func.sum(Sale.total)).scalar() or 0

    new_users = User.query.filter(User.created_at >= month_start).count()
    new_sales = Sale.query.filter(Sale.created_at >= month_start).count()
    monthly_revenue = db.session.query(func.sum(Sale.total)).filter(Sale.created_at >= month_start).scalar() or 0

    return jsonify({
        'total_users': total_users,
        'total_products': total_products,
        'total_sales': total_sales,
        'total_revenue': round(total_revenue, 2),
        'new_users': new_users,
        'new_sales': new_sales,
        'monthly_revenue': round(monthly_revenue, 2),
    })


@api_bp.route('/revenue-chart')
@login_required
def revenue_chart():
    data = db.session.query(
        func.strftime('%Y-%m', Sale.created_at).label('month'),
        func.sum(Sale.total).label('revenue')
    ).group_by('month').order_by('month').limit(12).all()

    return jsonify({
        'labels': [d.month for d in data],
        'values': [float(d.revenue) for d in data]
    })


@api_bp.route('/sales-chart')
@login_required
def sales_chart():
    data = db.session.query(
        func.strftime('%Y-%m-%d', Sale.created_at).label('date'),
        func.count(Sale.id).label('count')
    ).filter(Sale.created_at >= datetime.now(timezone.utc) - timedelta(days=30)
    ).group_by('date').order_by('date').all()

    return jsonify({
        'labels': [d.date for d in data],
        'values': [d.count for d in data]
    })


@api_bp.route('/category-chart')
@login_required
def category_chart():
    data = db.session.query(
        Product.category,
        func.count(Product.id).label('count')
    ).group_by(Product.category).order_by(func.count(Product.id).desc()).all()

    return jsonify({
        'labels': [d.category for d in data],
        'values': [d.count for d in data]
    })


@api_bp.route('/activities')
@login_required
def recent_activities():
    limit = request.args.get('limit', 10, type=int)
    activities = Activity.query.order_by(Activity.created_at.desc()).limit(limit).all()
    return jsonify([a.to_dict() for a in activities])


@api_bp.route('/notifications')
@login_required
def get_notifications():
    notifications = Notification.query.filter_by(user_id=current_user.id).order_by(Notification.created_at.desc()).limit(10).all()
    return jsonify([{
        'id': n.id,
        'title': n.title,
        'message': n.message,
        'type': n.type,
        'is_read': n.is_read,
        'created_at': n.created_at.isoformat() if n.created_at else None
    } for n in notifications])


@api_bp.route('/notifications/read/<int:notification_id>', methods=['POST'])
@login_required
def mark_read(notification_id):
    notification = Notification.query.get_or_404(notification_id)
    if notification.user_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403
    notification.is_read = True
    db.session.commit()
    return jsonify({'success': True})


@api_bp.route('/notifications/read-all', methods=['POST'])
@login_required
def mark_all_read():
    Notification.query.filter_by(user_id=current_user.id, is_read=False).update({'is_read': True})
    db.session.commit()
    return jsonify({'success': True})


@api_bp.route('/ai/insights')
@login_required
def get_insights():
    insights = ai_analyzer.generate_insights()
    return jsonify(insights)


@api_bp.route('/ai/sales-summary')
@login_required
def sales_summary():
    summary = ai_analyzer.generate_sales_summary()
    return jsonify({'summary': summary})


@api_bp.route('/ai/smart-search')
@login_required
def smart_search():
    query = request.args.get('q', '')
    if not query:
        return jsonify({'results': []})

    users = User.query.filter(
        User.full_name.contains(query) |
        User.email.contains(query) |
        User.username.contains(query)
    ).limit(3).all()

    products = Product.query.filter(
        Product.name.contains(query) |
        Product.category.contains(query) |
        Product.sku.contains(query)
    ).limit(3).all()

    results = []
    for u in users:
        results.append({'type': 'user', 'id': u.id, 'title': u.full_name, 'subtitle': u.email, 'url': f'/users/edit/{u.id}'})
    for p in products:
        results.append({'type': 'product', 'id': p.id, 'title': p.name, 'subtitle': f'${p.price:.2f} - {p.category}', 'url': f'/products/edit/{p.id}'})

    return jsonify({'results': results})


@api_bp.route('/ai/assistant', methods=['POST'])
@login_required
def assistant():
    data = request.get_json()
    message = data.get('message', '')
    response = ai_assistant.chat(message)
    return jsonify({'response': response})


@api_bp.route('/ai/report-summary', methods=['POST'])
@login_required
def report_summary():
    data = request.get_json()
    report_type = data.get('report_type', 'users')
    summary = ai_analyzer.generate_report_summary(report_type)
    return jsonify({'summary': summary})
