import os
import logging

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from werkzeug.middleware.proxy_fix import ProxyFix
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect

logging.basicConfig(level=logging.DEBUG)

class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)
# create the app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "morocco_accounting_secret_key")
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)  # needed for url_for to generate with https

# configure the database
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL", "sqlite:///moroccan_accounting.db")
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
}
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# initialize the app with the extension
db.init_app(app)

# Setup CSRF protection
csrf = CSRFProtect(app)

# Add custom Jinja2 filters
@app.template_filter('number_format')
def number_format_filter(value, decimals=2, decimal_point=',', thousands_separator=' '):
    """Format a number with custom thousands separator and decimal point."""
    if value is None:
        return ""
    return format(float(value), f',.{decimals}f').replace('.', decimal_point).replace(',', thousands_separator)

# Setup Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'auth.login'
login_manager.login_message = 'Veuillez vous connecter pour accéder à cette page.'
login_manager.login_message_category = 'info'

# Import models and create tables
with app.app_context():
    # Import models
    import models

    # Create all tables
    db.create_all()

    # Import and register blueprints
    from routes.auth import auth_bp, init_roles
    from routes.accounting import accounting_bp
    from routes.taxes import taxes_bp
    from routes.reports import reports_bp
    from routes.deadlines import deadlines_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(accounting_bp)
    app.register_blueprint(taxes_bp)
    app.register_blueprint(reports_bp)
    app.register_blueprint(deadlines_bp)

    # Initialize login manager
    from models import User
    
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))
        
    # Initialize roles
    init_roles()
