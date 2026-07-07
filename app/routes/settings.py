import os
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, current_app
from flask_login import login_required, current_user
from app.models.models import db, User, Activity

settings_bp = Blueprint('settings', __name__)


@settings_bp.route('/')
@login_required
def settings():
    return render_template('settings.html')


@settings_bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    if request.method == 'POST':
        current_user.bio = request.form.get('bio', '').strip()

        if 'profile_image' in request.files:
            file = request.files['profile_image']
            if file.filename:
                from app.utilities.helpers import save_file
                filename = save_file(file)
                if filename:
                    if current_user.profile_image and current_user.profile_image != 'default.svg':
                        old_path = os.path.join(current_app.config['UPLOAD_FOLDER'], current_user.profile_image)
                        if os.path.exists(old_path):
                            os.remove(old_path)
                    current_user.profile_image = filename

        activity = Activity(user_id=current_user.id, action='Profile updated',
                            details=f'{current_user.username} updated profile')
        db.session.add(activity)
        db.session.commit()

        flash('Profile updated successfully!', 'success')
        return redirect(url_for('settings.profile'))

    return render_template('profile.html')


@settings_bp.route('/change-password', methods=['POST'])
@login_required
def change_password():
    current_password = request.form.get('current_password', '')
    new_password = request.form.get('new_password', '')
    confirm_password = request.form.get('confirm_password', '')

    if not current_user.check_password(current_password):
        flash('Current password is incorrect.', 'danger')
        return redirect(url_for('settings.settings'))

    if len(new_password) < 6:
        flash('New password must be at least 6 characters.', 'danger')
        return redirect(url_for('settings.settings'))

    if new_password != confirm_password:
        flash('New passwords do not match.', 'danger')
        return redirect(url_for('settings.settings'))

    current_user.set_password(new_password)
    activity = Activity(user_id=current_user.id, action='Password changed',
                        details=f'{current_user.username} changed password')
    db.session.add(activity)
    db.session.commit()

    flash('Password changed successfully!', 'success')
    return redirect(url_for('settings.settings'))


@settings_bp.route('/toggle-theme', methods=['POST'])
@login_required
def toggle_theme():
    theme = request.json.get('theme', 'dark')
    if theme not in ('dark', 'light'):
        theme = 'dark'
    current_user.theme = theme
    db.session.commit()
    return jsonify({'status': 'ok', 'theme': theme})


@settings_bp.route('/toggle-notifications', methods=['POST'])
@login_required
def toggle_notifications():
    enabled = request.json.get('enabled', True)
    current_user.notifications_enabled = enabled
    db.session.commit()
    return jsonify({'status': 'ok', 'enabled': enabled})
