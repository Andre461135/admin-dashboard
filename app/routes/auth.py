from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from app.models.models import db, User, Activity

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.index'))

    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        remember = request.form.get('remember') == 'on'

        if not username or not password:
            flash('Please enter both username and password.', 'danger')
            return render_template('login.html')

        user = User.query.filter_by(username=username).first()
        if not user:
            user = User.query.filter_by(email=username).first()

        if user and user.check_password(password):
            if user.status == 'suspended':
                flash('Your account has been suspended. Contact support.', 'danger')
                return render_template('login.html')

            login_user(user, remember=remember)
            activity = Activity(user_id=user.id, action='User login',
                                details=f'{user.username} logged in successfully')
            db.session.add(activity)
            db.session.commit()
            flash(f'Welcome back, {user.username}!', 'success')
            next_page = request.args.get('next')
            return redirect(next_page or url_for('dashboard.index'))

        flash('Invalid username or password.', 'danger')

    return render_template('login.html')


@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('auth.login'))


@auth_bp.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        user = User.query.filter_by(email=email).first()
        if user:
            flash('Password reset instructions have been sent to your email.', 'success')
        else:
            flash('If that email is registered, you will receive reset instructions.', 'info')
        return redirect(url_for('auth.login'))
    return render_template('forgot_password.html')
