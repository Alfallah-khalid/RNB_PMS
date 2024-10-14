from functools import wraps
from flask import session, render_template, request

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Check if the user is logged in by checking if 'profile' exists in session
        if 'profile' not in session:
            # Store the original URL the user is trying to access (optional, if needed later)
            session['next'] = request.url  # Save the full URL of the original request
            print(session['next'])
            # Render the 'index.html' template instead of redirecting
            return render_template('index.html')
        return f(*args, **kwargs)
    return decorated_function
