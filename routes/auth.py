from flask import Blueprint, redirect, url_for, session, request, render_template
from utils.oauth import google  # Import the initialized Google OAuth object from oauth.py
import datetime
from firebase_service import FirebaseService as fs

# Initialize FirebaseService instance
fs = fs()

# Define Blueprint for auth routes
bp = Blueprint('auth', __name__, url_prefix='/auth')

@bp.route('/login', methods=['GET'])
def login():
    """
    Redirects the user to Google's OAuth 2.0 login page.
    """
    # Redirect the user to the Google login page
    redirect_uri = url_for('auth.authorize', _external=True)
    return google.authorize_redirect(redirect_uri)

@bp.route('/login/callback')
def authorize():
    """
    Handles Google's OAuth 2.0 callback after login, stores the user's profile in session,
    logs the event in Firebase, and redirects the user to the original page or homepage.
    """
    # Get token and user info from Google
    token = google.authorize_access_token()  # Get the token from Google
    nonce = session.get('nonce')  # Get the nonce if you're using it (optional)
    user_info = google.parse_id_token(token, nonce=nonce)  # Parse user info from the ID token
    
    # Store the user profile and token in session
    session['profile'] = user_info
    session['token'] = token

    # Log the login event in Firebase (storing login time and action)
    DateData = {
        'login_time': datetime.datetime.now(),
        'action': 'successful_login',
        'IP-address' : request.remote_addr
    }
    fs.CU(path=f"Users", document_id=user_info["email"], data=DateData)
    fs.CU(path=f"Users/{user_info['email']}/logins", document_id=str(DateData['login_time']).replace(" ","-"), data=DateData)

    # Check if there's a 'next' URL stored in the session
    next_page = session.get('next')
    session.pop('next', None)  # Clear the 'next' value after using it

    print("Next page after login:", next_page)

    # Redirect to the original page or homepage if no 'next' page exists
    if next_page:
        return redirect(next_page)
    
    return redirect('/')  # Default to homepage if no 'next' page is set

@bp.route('/logout')
def logout():
    """
    Logs the user out by clearing the session and redirects to the homepage.
    """
    # Clear the session, logging out the user
    DateData = {
        'login_time': datetime.datetime.now(),
        'action': 'logged out',
        'IP-address' : request.remote_addr
    }
    user_info=session['profile'] 

    fs.CU(path=f"Users", document_id=user_info["email"], data=DateData)
    fs.CU(path=f"Users/{user_info['email']}/logins", document_id=str(DateData['login_time']).replace(" ","-"), data=DateData)

    session.clear()
    return redirect('/')

