import os
from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_required, current_user
from app import db
from app.models import User, Activity
from app.forms import UserForm
from app.utils import save_file, log_activity

users_bp = Blueprint('users', __name__)


@users_bp.route('/')
@login_required
def list_users():
    if not current_user.is_admin():
        flash('Access denied. Admin only.', 'danger')
        return redirect(url_for('dashboard.index'))

    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '')

    query = User.query
    if search:
        query = query.filter(
            User.full_name.contains(search) |
            User.email.contains(search) |
            User.username.contains(search)
        )

    query = query.order_by(User.created_at.desc())
    users = query.paginate(page=page, per_page=10, error_out=False)

    return render_template('users/list.html', users=users, search=search)


@users_bp.route('/add', methods=['GET', 'POST'])
@login_required
def add_user():
    if not current_user.is_admin():
        flash('Access denied. Admin only.', 'danger')
        return redirect(url_for('dashboard.index'))

    form = UserForm()
    if form.validate_on_submit():
        if User.query.filter_by(email=form.email.data.lower().strip()).first():
            flash('Email already registered.', 'danger')
            return render_template('users/form.html', form=form, title='Add User')

        if User.query.filter_by(username=form.username.data.strip()).first():
            flash('Username already taken.', 'danger')
            return render_template('users/form.html', form=form, title='Add User')

        user = User(
            username=form.username.data.strip(),
            email=form.email.data.lower().strip(),
            full_name=form.full_name.data.strip(),
            role=form.role.data,
            status=form.status.data,
            bio=form.bio.data,
            phone=form.phone.data
        )
        user.set_password(form.password.data or 'changeme123')

        if form.profile_image.data:
            filename = save_file(form.profile_image.data, current_app.config['UPLOAD_FOLDER'])
            if filename:
                user.profile_image = filename

        db.session.add(user)
        db.session.commit()
        log_activity(current_user.id, 'User created', f'Created user: {user.full_name}', 'user', user.id)
        flash('User created successfully!', 'success')
        return redirect(url_for('users.list_users'))

    return render_template('users/form.html', form=form, title='Add User')


@users_bp.route('/edit/<int:user_id>', methods=['GET', 'POST'])
@login_required
def edit_user(user_id):
    if not current_user.is_admin():
        flash('Access denied. Admin only.', 'danger')
        return redirect(url_for('dashboard.index'))

    user = User.query.get_or_404(user_id)
    form = UserForm(obj=user)

    if form.validate_on_submit():
        if form.email.data.lower().strip() != user.email:
            if User.query.filter_by(email=form.email.data.lower().strip()).first():
                flash('Email already registered.', 'danger')
                return render_template('users/form.html', form=form, title='Edit User', user=user)

        user.full_name = form.full_name.data.strip()
        user.email = form.email.data.lower().strip()
        user.role = form.role.data
        user.status = form.status.data
        user.bio = form.bio.data
        user.phone = form.phone.data

        if form.password.data:
            user.set_password(form.password.data)

        if form.profile_image.data:
            filename = save_file(form.profile_image.data, current_app.config['UPLOAD_FOLDER'])
            if filename:
                user.profile_image = filename

        db.session.commit()
        log_activity(current_user.id, 'User updated', f'Updated user: {user.full_name}', 'user', user.id)
        flash('User updated successfully!', 'success')
        return redirect(url_for('users.list_users'))

    form.username.data = user.username
    return render_template('users/form.html', form=form, title='Edit User', user=user)


@users_bp.route('/delete/<int:user_id>', methods=['POST'])
@login_required
def delete_user(user_id):
    if not current_user.is_admin():
        flash('Access denied. Admin only.', 'danger')
        return redirect(url_for('dashboard.index'))

    user = User.query.get_or_404(user_id)
    if user.id == current_user.id:
        flash('You cannot delete your own account.', 'danger')
        return redirect(url_for('users.list_users'))

    name = user.full_name
    db.session.delete(user)
    db.session.commit()
    log_activity(current_user.id, 'User deleted', f'Deleted user: {name}', 'user', user_id)
    flash('User deleted successfully!', 'success')
    return redirect(url_for('users.list_users'))
