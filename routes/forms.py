from flask import Blueprint, request, render_template, session
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
    format = fs.G("formats", document_id=format_id)
    
    # Extract field_groups from the format_data
    field_groups = format.get('field_groups', [])

    
    # Render the form with the field_groups
    return render_template('form.html', format=format,user=session['profile'])


@bp.route('/forms-table', methods=['GET', 'POST'])
@login_required
def forms_table():
    user = dict(session).get('profile', None)
    if request.method == 'POST':
        table_data = request.json['table_data']  # Handle POST data (same as before)

        # Process and save the table data (as described previously)
        for row in table_data:
            # Parse the row and save to Firebase or another DB
            pass

        return jsonify({"status": "success"})

    # Fetch the form structure dynamically from Firebase
    form_structure_ref = db.collection('formats').document('mpr_other_department_2024')
    form_structure = form_structure_ref.get().to_dict()  # Convert Firebase document to Python dict

    # Pass the form structure to the template
    return render_template('forms_table.html', form_structure=form_structure,user=session)

