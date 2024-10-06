# routes/data.py

from flask import Blueprint, request, render_template
from utils.decorators import login_required  # Import the login_required decorator

from firebase_service import FirebaseService as fs
fs=fs()

bp = Blueprint('data', __name__, url_prefix='/data')

data_format =fs.G(collection_name="formats",document_id="mpr_other_department_2024")

@bp.route('/entrx', methods=['GET', 'POST'])
@login_required  # Protect this route with the login_required decorator
def data_entry():
    if request.method == 'POST':
        captured_data = {}
        for field in data_format['fields']:
            field_name = field['Name']
            captured_data[field_name] = request.form.get(field_name)
        return render_template('data_submitted.html', data=captured_data)
    
    return render_template('data_entry.html', format=data_format)