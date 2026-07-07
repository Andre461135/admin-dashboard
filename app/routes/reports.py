import csv
import io
from datetime import datetime
from flask import Blueprint, render_template, request, Response, jsonify, flash, redirect, url_for
from flask_login import login_required, current_user
from app.models.models import db, User, Product, Transaction, Report, Activity
from app.utilities.ai_helpers import AIAssistant

try:
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import letter, landscape
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False

reports_bp = Blueprint('reports', __name__)


@reports_bp.route('/')
@login_required
def reports():
    return render_template('reports.html')


@reports_bp.route('/data')
@login_required
def report_data():
    report_type = request.args.get('type', 'users')

    if report_type == 'users':
        users = User.query.order_by(User.created_at.desc()).all()
        data = [{'id': u.id, 'username': u.username, 'email': u.email, 'role': u.role,
                 'status': u.status, 'created_at': u.created_at.strftime('%Y-%m-%d')} for u in users]
        summary = AIAssistant.report_summary('users', data)
        return jsonify({'data': data, 'summary': summary, 'type': 'users'})

    if report_type == 'sales':
        transactions = Transaction.query.order_by(Transaction.created_at.desc()).all()
        data = [{'id': t.id, 'amount': t.amount, 'status': t.status,
                 'created_at': t.created_at.strftime('%Y-%m-%d')} for t in transactions]
        summary = AIAssistant.report_summary('sales', data)
        return jsonify({'data': data, 'summary': summary, 'type': 'sales'})

    if report_type == 'products':
        products = Product.query.order_by(Product.created_at.desc()).all()
        data = [{'id': p.id, 'name': p.name, 'category': p.category, 'price': p.price,
                 'stock': p.stock, 'status': p.status} for p in products]
        summary = AIAssistant.report_summary('products', data)
        return jsonify({'data': data, 'summary': summary, 'type': 'products'})

    if report_type == 'revenue':
        transactions = Transaction.query.filter_by(status='completed').order_by(
            Transaction.created_at.desc()
        ).all()
        data = [{'id': t.id, 'amount': t.amount, 'created_at': t.created_at.strftime('%Y-%m-%d')}
                for t in transactions]
        total = sum(t.amount for t in transactions)
        summary = AIAssistant.report_summary('revenue', data)
        return jsonify({'data': data, 'summary': summary, 'total': round(total, 2), 'type': 'revenue'})

    return jsonify({'data': [], 'summary': 'No data available.'})


@reports_bp.route('/export/csv')
@login_required
def export_csv():
    report_type = request.args.get('type', 'users')
    si = io.StringIO()
    writer = csv.writer(si)

    if report_type == 'users':
        writer.writerow(['ID', 'Username', 'Email', 'Role', 'Status', 'Created At'])
        for u in User.query.order_by(User.created_at.desc()).all():
            writer.writerow([u.id, u.username, u.email, u.role, u.status, u.created_at.strftime('%Y-%m-%d')])
        filename = f'users_report_{datetime.utcnow().strftime("%Y%m%d")}.csv'

    elif report_type == 'sales':
        writer.writerow(['ID', 'Amount', 'Status', 'Date'])
        for t in Transaction.query.order_by(Transaction.created_at.desc()).all():
            writer.writerow([t.id, t.amount, t.status, t.created_at.strftime('%Y-%m-%d')])
        filename = f'sales_report_{datetime.utcnow().strftime("%Y%m%d")}.csv'

    elif report_type == 'products':
        writer.writerow(['ID', 'Name', 'Category', 'Price', 'Stock', 'Status'])
        for p in Product.query.order_by(Product.created_at.desc()).all():
            writer.writerow([p.id, p.name, p.category, p.price, p.stock, p.status])
        filename = f'products_report_{datetime.utcnow().strftime("%Y%m%d")}.csv'

    elif report_type == 'revenue':
        writer.writerow(['ID', 'Amount', 'Date'])
        for t in Transaction.query.filter_by(status='completed').order_by(Transaction.created_at.desc()).all():
            writer.writerow([t.id, t.amount, t.created_at.strftime('%Y-%m-%d')])
        filename = f'revenue_report_{datetime.utcnow().strftime("%Y%m%d")}.csv'

    else:
        flash('Invalid report type.', 'danger')
        return redirect(url_for('reports.reports'))

    output = si.getvalue()
    activity = Activity(user_id=current_user.id, action='Report exported',
                        details=f'Exported {report_type} report as CSV')
    db.session.add(activity)
    db.session.commit()

    return Response(
        output,
        mimetype='text/csv',
        headers={'Content-Disposition': f'attachment; filename={filename}'}
    )


@reports_bp.route('/export/pdf')
@login_required
def export_pdf():
    if not REPORTLAB_AVAILABLE:
        flash('PDF export requires reportlab. Install with: pip install reportlab', 'warning')
        return redirect(url_for('reports.reports'))

    report_type = request.args.get('type', 'users')
    buf = io.BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=landscape(letter), rightMargin=30, leftMargin=30, topMargin=30, bottomMargin=30)
    styles = getSampleStyleSheet()
    elements = []
    elements.append(Paragraph(f'{report_type.capitalize()} Report', styles['Title']))
    elements.append(Spacer(1, 12))
    elements.append(Paragraph(f'Generated: {datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")}', styles['Normal']))
    elements.append(Spacer(1, 20))

    if report_type == 'users':
        data = [['ID', 'Username', 'Email', 'Role', 'Status', 'Created']]
        for u in User.query.order_by(User.created_at.desc()).all():
            data.append([str(u.id), u.username, u.email, u.role, u.status, u.created_at.strftime('%Y-%m-%d')])
    elif report_type == 'sales':
        data = [['ID', 'Amount', 'Status', 'Date']]
        for t in Transaction.query.order_by(Transaction.created_at.desc()).all():
            data.append([str(t.id), f'${t.amount:.2f}', t.status, t.created_at.strftime('%Y-%m-%d')])
    elif report_type == 'products':
        data = [['ID', 'Name', 'Category', 'Price', 'Stock', 'Status']]
        for p in Product.query.order_by(Product.created_at.desc()).all():
            data.append([str(p.id), p.name, p.category, f'${p.price:.2f}', str(p.stock), p.status])
    elif report_type == 'revenue':
        data = [['ID', 'Amount', 'Date']]
        for t in Transaction.query.filter_by(status='completed').order_by(Transaction.created_at.desc()).all():
            data.append([str(t.id), f'${t.amount:.2f}', t.created_at.strftime('%Y-%m-%d')])
    else:
        flash('Invalid report type.', 'danger')
        return redirect(url_for('reports.reports'))

    table = Table(data, repeatRows=1)
    style = TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#6c5ce7')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('FONTSIZE', (0, 0), (-1, 0), 11),
        ('FONTSIZE', (0, 1), (-1, -1), 9),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e0e0e0')),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.HexColor('#f8f9fa'), colors.white]),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
    ])
    table.setStyle(style)
    elements.append(table)
    doc.build(elements)
    buf.seek(0)

    activity = Activity(user_id=current_user.id, action='Report exported',
                        details=f'Exported {report_type} report as PDF')
    db.session.add(activity)
    db.session.commit()

    return Response(
        buf.getvalue(),
        mimetype='application/pdf',
        headers={'Content-Disposition': f'attachment; filename={report_type}_report_{datetime.utcnow().strftime("%Y%m%d")}.pdf'}
    )
