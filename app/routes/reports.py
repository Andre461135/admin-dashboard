import csv
import io
from datetime import datetime, timezone
from flask import Blueprint, render_template, request, Response, flash
from flask_login import login_required, current_user
from app import db
from app.models import User, Product, Sale
from app.utils import log_activity
from sqlalchemy import func

reports_bp = Blueprint('reports', __name__)


@reports_bp.route('/')
@login_required
def index():
    return render_template('reports/index.html')


@reports_bp.route('/users')
@login_required
def users_report():
    users = User.query.order_by(User.created_at.desc()).all()
    return render_template('reports/view.html',
        title='Users Report',
        headers=['ID', 'Username', 'Email', 'Full Name', 'Role', 'Status', 'Created'],
        rows=[[u.id, u.username, u.email, u.full_name, u.role, u.status, u.created_at.strftime('%Y-%m-%d') if u.created_at else ''] for u in users],
        report_type='users')


@reports_bp.route('/sales')
@login_required
def sales_report():
    sales = Sale.query.order_by(Sale.created_at.desc()).all()
    return render_template('reports/view.html',
        title='Sales Report',
        headers=['ID', 'Product', 'Buyer', 'Quantity', 'Total', 'Status', 'Date'],
        rows=[[s.id, s.product.name if s.product else 'N/A', s.buyer.full_name if s.buyer else 'N/A',
               s.quantity, f'${s.total:.2f}', s.status, s.created_at.strftime('%Y-%m-%d') if s.created_at else ''] for s in sales],
        report_type='sales')


@reports_bp.route('/products')
@login_required
def products_report():
    products = Product.query.order_by(Product.created_at.desc()).all()
    return render_template('reports/view.html',
        title='Products Report',
        headers=['ID', 'Name', 'Category', 'Price', 'Stock', 'SKU', 'Status'],
        rows=[[p.id, p.name, p.category, f'${p.price:.2f}', p.stock, p.sku, p.status] for p in products],
        report_type='products')


@reports_bp.route('/revenue')
@login_required
def revenue_report():
    data = db.session.query(
        func.strftime('%Y-%m', Sale.created_at).label('month'),
        func.count(Sale.id).label('transactions'),
        func.sum(Sale.total).label('revenue')
    ).group_by('month').order_by('month').all()

    headers = ['Month', 'Transactions', 'Revenue']
    rows = [[d.month, d.transactions, f'${d.revenue:.2f}'] for d in data]
    return render_template('reports/view.html',
        title='Revenue Report', headers=headers, rows=rows, report_type='revenue')


@reports_bp.route('/export/csv/<report_type>')
@login_required
def export_csv(report_type):
    log_activity(current_user.id, 'Report exported', f'Exported {report_type} report as CSV', 'report')

    if report_type == 'users':
        data = User.query.all()
        headers = ['ID', 'Username', 'Email', 'Full Name', 'Role', 'Status', 'Created']
        rows = [[u.id, u.username, u.email, u.full_name, u.role, u.status,
                 u.created_at.strftime('%Y-%m-%d') if u.created_at else ''] for u in data]
    elif report_type == 'sales':
        data = Sale.query.all()
        headers = ['ID', 'Product', 'Buyer', 'Quantity', 'Total', 'Status', 'Date']
        rows = [[s.id, s.product.name if s.product else 'N/A', s.buyer.full_name if s.buyer else 'N/A',
                 s.quantity, s.total, s.status, s.created_at.strftime('%Y-%m-%d') if s.created_at else ''] for s in data]
    elif report_type == 'products':
        data = Product.query.all()
        headers = ['ID', 'Name', 'Category', 'Price', 'Stock', 'SKU', 'Status']
        rows = [[p.id, p.name, p.category, p.price, p.stock, p.sku, p.status] for p in data]
    elif report_type == 'revenue':
        data = db.session.query(
            func.strftime('%Y-%m', Sale.created_at).label('month'),
            func.count(Sale.id).label('transactions'),
            func.sum(Sale.total).label('revenue')
        ).group_by('month').order_by('month').all()
        headers = ['Month', 'Transactions', 'Revenue']
        rows = [[d.month, d.transactions, d.revenue] for d in data]
    else:
        flash('Invalid report type.', 'danger')
        return render_template('reports/index.html')

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(headers)
    writer.writerows(rows)

    return Response(
        output.getvalue(),
        mimetype='text/csv',
        headers={'Content-Disposition': f'attachment;filename={report_type}_report.csv'}
    )


@reports_bp.route('/export/pdf/<report_type>')
@login_required
def export_pdf(report_type):
    log_activity(current_user.id, 'Report exported', f'Exported {report_type} report as PDF', 'report')

    from reportlab.lib.pagesizes import letter, landscape
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
    from reportlab.lib import colors
    from reportlab.lib.styles import getSampleStyleSheet
    from reportlab.lib.units import inch

    buffer = io.BytesIO()

    if report_type == 'users':
        data = User.query.all()
        headers = ['ID', 'Username', 'Email', 'Full Name', 'Role', 'Status']
        rows = [[u.id, u.username, u.email, u.full_name, u.role, u.status] for u in data]
    elif report_type == 'sales':
        data = Sale.query.all()
        headers = ['ID', 'Product', 'Buyer', 'Qty', 'Total', 'Status']
        rows = [[s.id, s.product.name[:20] if s.product else 'N/A', s.buyer.full_name[:20] if s.buyer else 'N/A',
                 s.quantity, f'${s.total:.2f}', s.status] for s in data]
    elif report_type == 'products':
        data = Product.query.all()
        headers = ['ID', 'Name', 'Category', 'Price', 'Stock', 'Status']
        rows = [[p.id, p.name[:25], p.category, f'${p.price:.2f}', p.stock, p.status] for p in data]
    elif report_type == 'revenue':
        data = db.session.query(
            func.strftime('%Y-%m', Sale.created_at).label('month'),
            func.count(Sale.id).label('transactions'),
            func.sum(Sale.total).label('revenue')
        ).group_by('month').order_by('month').all()
        headers = ['Month', 'Transactions', 'Revenue']
        rows = [[d.month, d.transactions, f'${d.revenue:.2f}'] for d in data]
    else:
        flash('Invalid report type.', 'danger')
        return render_template('reports/index.html')

    doc = SimpleDocTemplate(buffer, pagesize=landscape(letter))
    elements = []
    styles = getSampleStyleSheet()

    title = f'{report_type.title()} Report'
    elements.append(Paragraph(title, styles['Title']))
    elements.append(Spacer(1, 0.25 * inch))
    elements.append(Paragraph(f'Generated: {datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")}', styles['Normal']))
    elements.append(Spacer(1, 0.25 * inch))

    table_data = [headers] + rows
    table = Table(table_data, repeatRows=1)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#4361ee')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('FONTSIZE', (0, 1), (-1, -1), 9),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('TOPPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f8f9fa')),
        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#dee2e6')),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.HexColor('#ffffff'), colors.HexColor('#f1f3f5')]),
    ]))
    elements.append(table)

    doc.build(elements)
    buffer.seek(0)

    return Response(
        buffer.getvalue(),
        mimetype='application/pdf',
        headers={'Content-Disposition': f'attachment;filename={report_type}_report.pdf'}
    )
