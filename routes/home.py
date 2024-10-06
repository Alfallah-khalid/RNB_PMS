# routes/home.py
from flask import Blueprint, render_template, session
from firebase_service import FirebaseService as fs

fs = fs()

# Define Blueprint for home route
bp = Blueprint('home', __name__)

@bp.route('/')
def home():
    user = dict(session).get('profile', None)
    print(session)  # Print session to debug if it's holding the profile data correctly
    if user is not None:
        fs.CU(path="Users", document_id=user["email"], data=user)
    return render_template('index.html', user=user)