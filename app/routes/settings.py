import os
from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_required, current_user
from app import db
from app.models import User
from app.forms import ProfileForm, ChangePasswordForm, SettingsForm
from app.utils import save_file, log_activity

settings_bp = Blueprint('settings', __name__)


@settings_bp.route('/', methods=['GET', 'POST'])
@login_required
def index():
    return render_template('settings/index.html',
        active_tab=request.args.get('tab', 'profile'))


@settings_bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    form = ProfileForm(obj=current_user)
    if form.validate_on_submit():
        if form.email.data.lower().strip() != current_user.email:
            if User.query.filter_by(email=form.email.data.lower().strip()).first():
                flash('Email already in use.', 'danger')
                return render_template('settings/profile.html', form=form)

        current_user.full_name = form.full_name.data.strip()
        current_user.email = form.email.data.lower().strip()
        current_user.bio = form.bio.data
        current_user.phone = form.phone.data

        if form.profile_image.data:
            filename = save_file(form.profile_image.data, current_app.config['UPLOAD_FOLDER'])
            if filename:
                current_user.profile_image = filename

        db.session.commit()
        log_activity(current_user.id, 'Profile updated', 'Updated profile information')
        flash('Profile updated successfully!', 'success')
        return redirect(url_for('settings.profile'))

    return render_template('settings/profile.html', form=form)


@settings_bp.route('/password', methods=['GET', 'POST'])
@login_required
def password():
    form = ChangePasswordForm()
    if form.validate_on_submit():
        if not current_user.check_password(form.current_password.data):
            flash('Current password is incorrect.', 'danger')
            return render_template('settings/password.html', form=form)

        current_user.set_password(form.new_password.data)
        db.session.commit()
        log_activity(current_user.id, 'Password changed', 'Changed account password')
        flash('Password updated successfully!', 'success')
        return redirect(url_for('settings.password'))

    return render_template('settings/password.html', form=form)


@settings_bp.route('/theme', methods=['POST'])
@login_required
def toggle_theme():
    theme = request.form.get('theme', 'light')
    if theme in ['light', 'dark']:
        current_user.theme = theme
        db.session.commit()
    return redirect(request.referrer or url_for('settings.index'))


@settings_bp.route('/notifications', methods=['GET', 'POST'])
@login_required
def notifications():
    form = SettingsForm(obj=current_user)
    if form.validate_on_submit():
        current_user.theme = form.theme.data
        current_user.notifications_enabled = form.notifications_enabled.data
        current_user.email_notifications = form.email_notifications.data
        db.session.commit()
        log_activity(current_user.id, 'Settings updated', 'Updated notification settings')
        flash('Settings saved successfully!', 'success')
        return redirect(url_for('settings.notifications'))

    return render_template('settings/notifications.html', form=form)


@settings_bp.route('/appearance', methods=['GET', 'POST'])
@login_required
def appearance():
    return render_template('settings/appearance.html')
