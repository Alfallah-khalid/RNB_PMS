from flask import Flask
from flask_talisman import Talisman
from werkzeug.middleware.proxy_fix import ProxyFix
import os
from dotenv import load_dotenv
from routes import auth_bp, home_bp, data_bp, forms_bp  # Import blueprints
from utils.oauth import oauth

# Load environment variables
load_dotenv()

# Content Security Policy (CSP) to allow external styles and fonts
csp = {
    'default-src': '\'self\'',
    'style-src': [
        '\'self\'',
        'https://cdnjs.cloudflare.com',
        'https://fonts.googleapis.com',
        'https://cdn.jsdelivr.net',
        'https://bossanova.uk',
        'https://jsuites.net'
    ],
    'font-src': [
        'https://fonts.gstatic.com',
        'https://cdnjs.cloudflare.com',
        'https://fonts.googleapis.com'
    ],
    'script-src': [
        '\'self\'',
        'https://cdnjs.cloudflare.com',
        'https://unpkg.com',
        'https://cdn.jsdelivr.net',
        'https://code.jquery.com',
        'https://bossanova.uk',
        'https://jsuites.net'

    ]
}

# Initialize Flask app
app = Flask(__name__)

# Apply Flask-Talisman with HTTPS enforcement
Talisman(app, content_security_policy=csp, force_https=True)

# Ensure all URLs generated use https
app.config['PREFERRED_URL_SCHEME'] = 'https'

# Force Flask to handle the X-Forwarded-Proto header correctly if behind a proxy
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

# Set secret key and other configurations
app.secret_key = os.getenv("SECRET_KEY")

# Initialize OAuth
oauth.init_app(app)

# Register blueprints
app.register_blueprint(auth_bp)
app.register_blueprint(home_bp)
app.register_blueprint(data_bp)
app.register_blueprint(forms_bp)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))
