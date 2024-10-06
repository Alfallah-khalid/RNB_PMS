from flask import Blueprint, request, render_template
from utils.decorators import login_required  # Import the login_required decorator
from firebase_service import FirebaseService as fs

# Initialize FirebaseService
fs = fs()

# Define Blueprint for home route
bp = Blueprint('forms', __name__)

@bp.route('/forms/<format_id>', methods=['GET', 'POST'])
@login_required
def render_form(format_id):
    # Fetch the format structure from Firebase
    format_data = fs.G("formats", document_id=format_id)
    
    # Extract field_groups from the format_data
    field_groups = format_data.get('field_groups', [])

    
    # Render the form with the field_groups
    return render_template('form.html', field_groups=field_groups)
