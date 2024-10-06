from flask import Flask, redirect, url_for, session
from flask import render_template
from authlib.integrations.flask_client import OAuth
import os
from dotenv import load_dotenv
from authlib.jose import jwt
import secrets
from flask_talisman import Talisman
from werkzeug.middleware.proxy_fix import ProxyFix  # Ensure HTTPS URL generation
from firebase_service import FirebaseService as fs
import datetime

# Load environment variables from .env file
load_dotenv()

# Content Security Policy (CSP) to allow external styles and fonts
csp = {
    'default-src': '\'self\'',
    'style-src': [
        '\'self\'', 
        'https://cdnjs.cloudflare.com',  # Allow Materialize CSS
        'https://fonts.googleapis.com'   # Allow Google Fonts
    ],
    'font-src': [
        'https://fonts.gstatic.com',     # Allow Google Fonts
        'https://cdnjs.cloudflare.com'   # Allow Material Icons
    ],
    'script-src': [
        '\'self\'', 
        'https://cdnjs.cloudflare.com'   # Allow Materialize JS
    ]
}
fs = fs()
app = Flask(__name__)
Talisman(app, content_security_policy=csp)
app.secret_key = os.getenv("SECRET_KEY")

# Force Flask to use HTTPS for generating URLs
app.config['PREFERRED_URL_SCHEME'] = 'https'

# Apply ProxyFix to trust the X-Forwarded-Proto header (Cloud Run uses this header)
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

# Initialize OAuth (without the redirect_uri here)
oauth = OAuth(app)
google = oauth.register(
    name='google',
    client_id=os.getenv("GOOGLE_CLIENT_ID"),
    client_secret=os.getenv("GOOGLE_CLIENT_SECRET"),
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',  # Use Google's OpenID config URL
    client_kwargs={
        'scope': 'openid email profile',
        'prompt': 'select_account'
    }
)

@app.route('/')
def home():
    # Check if user is logged in by checking session
    user = dict(session).get('profile', None)
    if user!=None:
        fs.CU(path="Users",document_id=user["email"],data=user)
        

    return render_template('index.html', user=user)

@app.route('/login')
def login():
    # Generate a secure nonce
    nonce = secrets.token_urlsafe(16)
    session['nonce'] = nonce  # Store it in session
    
    # Now generate the redirect URI inside a valid application context
    redirect_uri = url_for('authorize', _external=True)
    app.logger.info(f"Redirect URI: {redirect_uri}")  # Log the redirect URI
    return google.authorize_redirect(redirect_uri, nonce=nonce)  # Pass the nonce

@app.route('/login/callback')
def authorize():
    # Get the authorization token and user info from Google
    token = google.authorize_access_token()  # Exchanges the authorization code for token
    
    # Retrieve the stored nonce from the session
    nonce = session.get('nonce')
    
    # Parse ID Token for authentication and validate the nonce
    user_info = google.parse_id_token(token, nonce=nonce)
    
    # Store user profile information in the session
    session['profile'] = user_info
    session['token'] = token
    DateData = {
        'login_time': datetime.datetime.now(),
        'action': 'successful_login'
        }
    print(fs.CU(path=f"Users/{user_info['email']}/logins",document_id=None,data=DateData))    
    return redirect('/')

@app.route('/logout')
def logout():
    # Clear the session to log out the user
    session.clear()
    return redirect('/')

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))
