import os
from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from flask_login import login_required, current_user
from app.models.models import db, User, Activity
from app.utilities.helpers import save_file, paginate

users_bp = Blueprint('users', __name__)


@users_bp.route('/')
@login_required
def list_users():
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '').strip()
    role_filter = request.args.get('role', '').strip()
    status_filter = request.args.get('status', '').strip()

    query = User.query
    if search:
        query = query.filter(
            db.or_(User.username.ilike(f'%{search}%'), User.email.ilike(f'%{search}%'))
        )
    if role_filter:
        query = query.filter_by(role=role_filter)
    if status_filter:
        query = query.filter_by(status=status_filter)

    query = query.order_by(User.created_at.desc())
    result = paginate(query, page, per_page=10)

    return render_template('users.html',
                           users=result['items'],
                           page=result['page'],
                           total_pages=result['total_pages'],
                           total=result['total'],
                           search=search,
                           role_filter=role_filter,
                           status_filter=status_filter)


@users_bp.route('/add', methods=['GET', 'POST'])
@login_required
def add_user():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        role = request.form.get('role', 'user')
        status = request.form.get('status', 'active')
        bio = request.form.get('bio', '').strip()

        if not username or not email or not password:
            flash('Username, email, and password are required.', 'danger')
            return render_template('user_form.html', user=None)

        if User.query.filter_by(username=username).first():
            flash('Username already exists.', 'danger')
            return render_template('user_form.html', user=None)

        if User.query.filter_by(email=email).first():
            flash('Email already exists.', 'danger')
            return render_template('user_form.html', user=None)

        user = User(username=username, email=email, role=role, status=status, bio=bio)
        user.set_password(password)

        if 'profile_image' in request.files:
            file = request.files['profile_image']
            if file.filename:
                filename = save_file(file)
                if filename:
                    user.profile_image = filename

        db.session.add(user)
        activity = Activity(user_id=current_user.id, action='User added',
                            details=f'Added user {username}')
        db.session.add(activity)
        db.session.commit()

        flash(f'User {username} created successfully!', 'success')
        return redirect(url_for('users.list_users'))

    return render_template('user_form.html', user=None)


@users_bp.route('/edit/<int:user_id>', methods=['GET', 'POST'])
@login_required
def edit_user(user_id):
    user = db.session.get(User, user_id)
    if not user:
        flash('User not found.', 'danger')
        return redirect(url_for('users.list_users'))

    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip()
        role = request.form.get('role', 'user')
        status = request.form.get('status', 'active')
        bio = request.form.get('bio', '').strip()

        if not username or not email:
            flash('Username and email are required.', 'danger')
            return render_template('user_form.html', user=user)

        existing = User.query.filter(User.username == username, User.id != user_id).first()
        if existing:
            flash('Username already taken.', 'danger')
            return render_template('user_form.html', user=user)

        existing = User.query.filter(User.email == email, User.id != user_id).first()
        if existing:
            flash('Email already taken.', 'danger')
            return render_template('user_form.html', user=user)

        user.username = username
        user.email = email
        user.role = role
        user.status = status
        user.bio = bio

        password = request.form.get('password', '')
        if password:
            user.set_password(password)

        if 'profile_image' in request.files:
            file = request.files['profile_image']
            if file.filename:
                filename = save_file(file)
                if filename:
                    if user.profile_image and user.profile_image != 'default.svg':
                        old_path = os.path.join(current_app.config['UPLOAD_FOLDER'], user.profile_image)
                        if os.path.exists(old_path):
                            os.remove(old_path)
                    user.profile_image = filename

        activity = Activity(user_id=current_user.id, action='User updated',
                            details=f'Updated user {username}')
        db.session.add(activity)
        db.session.commit()

        flash(f'User {username} updated successfully!', 'success')
        return redirect(url_for('users.list_users'))

    return render_template('user_form.html', user=user)


@users_bp.route('/delete/<int:user_id>', methods=['POST'])
@login_required
def delete_user(user_id):
    user = db.session.get(User, user_id)
    if not user:
        flash('User not found.', 'danger')
        return redirect(url_for('users.list_users'))

    if user.id == current_user.id:
        flash('You cannot delete yourself.', 'danger')
        return redirect(url_for('users.list_users'))

    db.session.delete(user)
    activity = Activity(user_id=current_user.id, action='User deleted',
                        details=f'Deleted user {user.username}')
    db.session.add(activity)
    db.session.commit()

    flash(f'User {user.username} deleted successfully.', 'success')
    return redirect(url_for('users.list_users'))
