import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect
from flask_migrate import Migrate
from config import Config

db = SQLAlchemy()
login_manager = LoginManager()
csrf = CSRFProtect()
migrate = Migrate()

login_manager.login_view = 'auth.login'
login_manager.login_message_category = 'info'


def create_app(config_class=Config):
    flask_app = Flask(__name__)
    flask_app.config.from_object(config_class)

    db.init_app(flask_app)
    login_manager.init_app(flask_app)
    csrf.init_app(flask_app)
    migrate.init_app(flask_app, db)

    from app.routes.auth import auth_bp
    from app.routes.dashboard import dashboard_bp
    from app.routes.users import users_bp
    from app.routes.products import products_bp
    from app.routes.reports import reports_bp
    from app.routes.settings import settings_bp
    from app.routes.api import api_bp

    flask_app.register_blueprint(auth_bp, url_prefix='/auth')
    flask_app.register_blueprint(dashboard_bp, url_prefix='/')
    flask_app.register_blueprint(users_bp, url_prefix='/users')
    flask_app.register_blueprint(products_bp, url_prefix='/products')
    flask_app.register_blueprint(reports_bp, url_prefix='/reports')
    flask_app.register_blueprint(settings_bp, url_prefix='/settings')
    flask_app.register_blueprint(api_bp, url_prefix='/api')

    os.makedirs(flask_app.config['UPLOAD_FOLDER'], exist_ok=True)

    with flask_app.app_context():
        from app import models as app_models
        db.create_all()
        from app.utils import seed_database
        seed_database(flask_app)

    return flask_app
