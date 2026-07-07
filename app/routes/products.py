import os
from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_required, current_user
from app import db
from app.models import Product
from app.forms import ProductForm
from app.utils import save_file, log_activity
from sqlalchemy import func

products_bp = Blueprint('products', __name__)


@products_bp.route('/')
@login_required
def list_products():
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '')
    category = request.args.get('category', '')

    query = Product.query
    if search:
        query = query.filter(
            Product.name.contains(search) |
            Product.sku.contains(search) |
            Product.category.contains(search)
        )
    if category:
        query = query.filter(Product.category == category)

    query = query.order_by(Product.created_at.desc())
    products = query.paginate(page=page, per_page=10, error_out=False)

    categories = db.session.query(Product.category).distinct().order_by(Product.category).all()
    categories = [c[0] for c in categories]

    return render_template('products/list.html', products=products, search=search, category=category, categories=categories)


@products_bp.route('/add', methods=['GET', 'POST'])
@login_required
def add_product():
    form = ProductForm()
    if form.validate_on_submit():
        product = Product(
            name=form.name.data.strip(),
            description=form.description.data,
            price=form.price.data,
            category=form.category.data.strip(),
            stock=form.stock.data or 0,
            sku=form.sku.data.strip() if form.sku.data else f"SKU-{db.session.query(func.max(Product.id)).scalar() or 0 + 10000}",
            status=form.status.data,
            user_id=current_user.id
        )

        if form.image.data:
            filename = save_file(form.image.data, current_app.config['UPLOAD_FOLDER'])
            if filename:
                product.image = filename

        db.session.add(product)
        db.session.commit()
        log_activity(current_user.id, 'Product created', f'Created product: {product.name}', 'product', product.id)
        flash('Product created successfully!', 'success')
        return redirect(url_for('products.list_products'))

    return render_template('products/form.html', form=form, title='Add Product')


@products_bp.route('/edit/<int:product_id>', methods=['GET', 'POST'])
@login_required
def edit_product(product_id):
    product = Product.query.get_or_404(product_id)
    form = ProductForm(obj=product)

    if form.validate_on_submit():
        product.name = form.name.data.strip()
        product.description = form.description.data
        product.price = form.price.data
        product.category = form.category.data.strip()
        product.stock = form.stock.data or 0
        product.status = form.status.data

        if form.sku.data:
            product.sku = form.sku.data.strip()

        if form.image.data:
            filename = save_file(form.image.data, current_app.config['UPLOAD_FOLDER'])
            if filename:
                product.image = filename

        db.session.commit()
        log_activity(current_user.id, 'Product updated', f'Updated product: {product.name}', 'product', product.id)
        flash('Product updated successfully!', 'success')
        return redirect(url_for('products.list_products'))

    return render_template('products/form.html', form=form, title='Edit Product', product=product)


@products_bp.route('/delete/<int:product_id>', methods=['POST'])
@login_required
def delete_product(product_id):
    product = Product.query.get_or_404(product_id)
    name = product.name
    db.session.delete(product)
    db.session.commit()
    log_activity(current_user.id, 'Product deleted', f'Deleted product: {name}', 'product', product_id)
    flash('Product deleted successfully!', 'success')
    return redirect(url_for('products.list_products'))
