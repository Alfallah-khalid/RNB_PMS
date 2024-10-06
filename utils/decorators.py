from functools import wraps
from flask import session, redirect, url_for, request

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Check if the user is logged in by checking if 'profile' exists in session
        if 'profile' not in session:
            # Store the original URL the user is trying to access
            session['next'] = request.url  # Save the full URL of the original request
            print(session['next'])
            return redirect(url_for('auth.login'))  # Redirect to the login route
        return f(*args, **kwargs)
    return decorated_function