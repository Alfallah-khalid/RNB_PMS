from flask import Flask, redirect, url_for, session
from flask import render_template
from authlib.integrations.flask_client import OAuth
import os
from dotenv import load_dotenv
from authlib.jose import jwt
import secrets
from flask_talisman import Talisman
from flask_sslify import SSLify

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


app = Flask(__name__)
SSLify =SSLify(app)
#Talisman(app, content_security_policy=csp)
app.secret_key = os.getenv("SECRET_KEY")

# Initialize OAuth
oauth = OAuth(app)
google = oauth.register(
    name='google',
    client_id=os.getenv("GOOGLE_CLIENT_ID"),
    client_secret=os.getenv("GOOGLE_CLIENT_SECRET"),
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',  # Use Google's OpenID config URL
    client_kwargs={
        'scope': 'openid email profile',
        'prompt': 'select_account'
    },
    redirect_uri="https://rbck.mashwar.in/login/callback"  # Must match with Google Cloud Console
)

@app.route('/')
def home():
    # Check if user is logged in by checking session
    user = dict(session).get('profile', None)
    #return "hello"
    return render_template('index.html', user=user)

@app.route('/login')
def login():
    # Generate a secure nonce
    nonce = secrets.token_urlsafe(16)
    session['nonce'] = nonce  # Store it in session
    
    # Redirect to Google's OAuth 2.0 server for authentication
    redirect_uri = url_for('authorize', _external=True)
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
    
    return redirect('/')

@app.route('/logout')
def logout():
    # Clear the session to log out the user
    session.clear()
    return redirect('/')

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))
