# routes/data.py

from flask import Blueprint, request, render_template, jsonify
from utils.decorators import login_required  # Import the login_required decorator
import json

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


@bp.route('/process_json', methods=['GET', 'POST'])
def process_json():
    # Get the JSON object from the request
    data = request.get_json()
    
    # Parse the 'message' key into a dictionary if it's a string
    try:
        adata = json.loads(data["message"])  # Convert the 'message' from string to dictionary
    except json.JSONDecodeError:
        return jsonify({"status": "error", "message": "Invalid JSON format in 'message' field"}), 400

    if adata:
        # Log the received data
        print(f"Received JSON: {adata}")
        # Pass the parsed data to the fs.CU function
        fs.CU("formats", document_id=adata.get('format_id'), data=adata)
        # Send a success response
        return jsonify({"status": "success", "received": adata}), 200
    else:
        return jsonify({"status": "error", "message": "'message' key not found in the request"}), 400
    

@bp.route('/get_tableData', methods=['GET', 'POST'])
def get_json():
    format_id = request.args.get('format_id') or request.json.get('format_id')
    # Get the JSON object from the request
    data = fs.GC(f"tableData/{format_id}/data")
    
    # Parse the 'message' key into a dictionary if it's a string
    if data:
        return data
    else:
        return jsonify({"status": "error", "message": "Data not found"}), 400
