from flask import Flask, redirect, url_for, session
from flask import render_template
from authlib.integrations.flask_client import OAuth
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY")

# Initialize OAuth
oauth = OAuth(app)
google = oauth.register(
    name='google',
    client_id=os.getenv("GOOGLE_CLIENT_ID"),
    client_secret=os.getenv("GOOGLE_CLIENT_SECRET"),
    access_token_url='https://oauth2.googleapis.com/token',
    authorize_url='https://accounts.google.com/o/oauth2/auth',
    authorize_params=None,
    access_token_params=None,
    redirect_uri=os.getenv("REDIRECT_URI", default="http://localhost:8080/login/callback"),
    client_kwargs={
        'scope': 'openid email profile',  # Minimal scope to authenticate users and get user profile
        'prompt': 'select_account'  # Ensures user selects account when logging in
    },
)



@app.route('/')
def home2():
    client_id = os.getenv('GOOGLE_OAUTH_CLIENT_ID')
    client_secret = os.getenv('GOOGLE_OAUTH_CLIENT_SECRET')
    return f"Client ID: {client_id}, Client Secret: {client_secret}"

def home():
    # Check if user is logged in by checking session
    user = dict(session).get('profile', None)
    return render_template('index.html', user=user)

@app.route('/login')
def login():
    # Redirect to Google's OAuth 2.0 server for authentication
    redirect_uri = url_for('authorize', _external=True)
    return google.authorize_redirect(redirect_uri)

@app.route('/login/callback')
def authorize():
    # Get the authorization token and user info from Google
    token = google.authorize_access_token()  # Exchanges the authorization code for token
    user_info = google.parse_id_token(token)  # Parse ID Token for authentication
    session['profile'] = user_info  # Store user profile information in the session
    session['token'] = token
    return redirect('/')

@app.route('/logout')
def logout():
    # Clear the session to log out the user
    session.clear()
    return redirect('/')

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))
