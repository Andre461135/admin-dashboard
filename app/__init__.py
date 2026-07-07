import os
from datetime import timedelta
from flask import Flask
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect
from app.models.models import db, User
from app.database.schema import init_db

login_manager = LoginManager()
csrf = CSRFProtect()


def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get(
        'DATABASE_URL',
        'sqlite:///' + os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'database', 'admin.db')
    )
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['UPLOAD_FOLDER'] = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads')
    app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
    app.config['REMEMBER_COOKIE_DURATION'] = timedelta(days=30)
    app.config['WTF_CSRF_TIME_LIMIT'] = None

    db.init_app(app)
    login_manager.init_app(app)
    csrf.init_app(app)

    login_manager.login_view = 'auth.login'
    login_manager.login_message_category = 'info'

    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

    from app.routes.auth import auth_bp
    from app.routes.dashboard import dashboard_bp
    from app.routes.users import users_bp
    from app.routes.products import products_bp
    from app.routes.reports import reports_bp
    from app.routes.settings import settings_bp
    from app.routes.ai import ai_bp

    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(dashboard_bp, url_prefix='/')
    app.register_blueprint(users_bp, url_prefix='/users')
    app.register_blueprint(products_bp, url_prefix='/products')
    app.register_blueprint(reports_bp, url_prefix='/reports')
    app.register_blueprint(settings_bp, url_prefix='/settings')
    app.register_blueprint(ai_bp, url_prefix='/ai')

    with app.app_context():
        init_db(app)

    return app


@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))
