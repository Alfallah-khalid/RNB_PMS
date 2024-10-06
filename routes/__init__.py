# routes/__init__.py

from routes.auth import bp as auth_bp
from routes.home import bp as home_bp
from routes.data import bp as data_bp
from routes.forms import bp as forms_bp

# Optional: Expose the blueprints so they can be imported easily in app.py
__all__ = ['auth_bp', 'home_bp', 'data_bp','forms_bp']