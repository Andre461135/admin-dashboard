import os
from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from flask_login import login_required, current_user
from app.models.models import db, Product, Activity
from app.utilities.helpers import save_file, paginate

products_bp = Blueprint('products', __name__)


@products_bp.route('/')
@login_required
def list_products():
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '').strip()
    category_filter = request.args.get('category', '').strip()

    query = Product.query
    if search:
        query = query.filter(
            db.or_(Product.name.ilike(f'%{search}%'), Product.description.ilike(f'%{search}%'))
        )
    if category_filter:
        query = query.filter_by(category=category_filter)

    query = query.order_by(Product.created_at.desc())
    result = paginate(query, page, per_page=10)

    categories = [c[0] for c in db.session.query(Product.category).distinct().all()]

    return render_template('products.html',
                           products=result['items'],
                           page=result['page'],
                           total_pages=result['total_pages'],
                           total=result['total'],
                           search=search,
                           category_filter=category_filter,
                           categories=categories)


@products_bp.route('/add', methods=['GET', 'POST'])
@login_required
def add_product():
    categories = [c[0] for c in db.session.query(Product.category).distinct().all()]

    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        description = request.form.get('description', '').strip()
        price = request.form.get('price', 0, type=float)
        category = request.form.get('category', 'Uncategorized').strip()
        stock = request.form.get('stock', 0, type=int)
        status = request.form.get('status', 'active')

        if not name or price <= 0:
            flash('Product name and valid price are required.', 'danger')
            return render_template('product_form.html', product=None, categories=categories)

        product = Product(name=name, description=description, price=price,
                          category=category, stock=stock, status=status)

        if 'image' in request.files:
            file = request.files['image']
            if file.filename:
                filename = save_file(file)
                if filename:
                    product.image = filename

        db.session.add(product)
        activity = Activity(user_id=current_user.id, action='Product added',
                            details=f'Added product {name}')
        db.session.add(activity)
        db.session.commit()

        flash(f'Product {name} created successfully!', 'success')
        return redirect(url_for('products.list_products'))

    return render_template('product_form.html', product=None, categories=categories)


@products_bp.route('/edit/<int:product_id>', methods=['GET', 'POST'])
@login_required
def edit_product(product_id):
    product = db.session.get(Product, product_id)
    if not product:
        flash('Product not found.', 'danger')
        return redirect(url_for('products.list_products'))

    categories = [c[0] for c in db.session.query(Product.category).distinct().all()]

    if request.method == 'POST':
        product.name = request.form.get('name', '').strip()
        product.description = request.form.get('description', '').strip()
        product.price = request.form.get('price', 0, type=float)
        product.category = request.form.get('category', 'Uncategorized').strip()
        product.stock = request.form.get('stock', 0, type=int)
        product.status = request.form.get('status', 'active')

        if not product.name or product.price <= 0:
            flash('Product name and valid price are required.', 'danger')
            return render_template('product_form.html', product=product, categories=categories)

        if 'image' in request.files:
            file = request.files['image']
            if file.filename:
                filename = save_file(file)
                if filename:
                    if product.image and product.image != 'default-product.png':
                        old_path = os.path.join(current_app.config['UPLOAD_FOLDER'], product.image)
                        if os.path.exists(old_path):
                            os.remove(old_path)
                    product.image = filename

        activity = Activity(user_id=current_user.id, action='Product updated',
                            details=f'Updated product {product.name}')
        db.session.add(activity)
        db.session.commit()

        flash(f'Product {product.name} updated successfully!', 'success')
        return redirect(url_for('products.list_products'))

    return render_template('product_form.html', product=product, categories=categories)


@products_bp.route('/delete/<int:product_id>', methods=['POST'])
@login_required
def delete_product(product_id):
    product = db.session.get(Product, product_id)
    if not product:
        flash('Product not found.', 'danger')
        return redirect(url_for('products.list_products'))

    db.session.delete(product)
    activity = Activity(user_id=current_user.id, action='Product deleted',
                        details=f'Deleted product {product.name}')
    db.session.add(activity)
    db.session.commit()

    flash(f'Product {product.name} deleted successfully.', 'success')
    return redirect(url_for('products.list_products'))
