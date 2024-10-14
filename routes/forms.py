from flask import Blueprint, request, render_template, session
from utils.decorators import login_required  # Import the login_required decorator
from firebase_service import FirebaseService as fs
import json


# Initialize FirebaseService
fs = fs()

# Define Blueprint for home route
bp = Blueprint('forms', __name__)

@bp.route('/forms/<format_id>', methods=['GET', 'POST'])
@login_required
def render_form(format_id):
    # Fetch the format structure from Firebase
    format = fs.G("formats", document_id=format_id)
    
    # Extract field_groups from the format_data
    field_groups = format.get('field_groups', [])

    
    # Render the form with the field_groups
    return render_template('form.html', format=json.dumps(format),user=session['profile'])

@bp.route('/tables/<format_id>', methods=['GET', 'POST'])
@login_required
def render_table(format_id):
    # Fetch the format structure from Firebase
    format = fs.G("formats", document_id=format_id)
    
    # Extract field_groups from the format_data
    field_groups = format.get('field_groups', [])

    
    # Render the form with the field_groups
    return render_template('table.html', format=json.dumps(format),user=session['profile'])


