# routes/data.py

from flask import Blueprint, request, render_template, jsonify , Response
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
    

from flask import jsonify
import pandas as pd


@bp.route('/get_jd', methods=['GET', 'POST'])
def get_json():
    # Attempt to fetch the format_id from GET or POST data
    format_id = request.args.get('format_id')
    
    if not format_id:
        # Manually parse JSON if Content-Type is not application/json
        try:
            request_data = request.get_json(silent=True)
            if request_data:
                format_id = request_data.get('format_id')
        except Exception:
            pass  # Fallback to format_id remaining None if parsing fails
    
    if not format_id:
        return jsonify({"status": "error", "message": "Format ID not provided"}), 400
    
    # Fetch data
    data = fs.GC(f"tableData/{format_id}/data")
    
    if data:
        try:
            combined_table = pd.DataFrame()  # Initialize an empty DataFrame
            
            for item in data:
                if 'table_data' in item:
                    # Convert the `table_date` to a DataFrame
                    table_data = pd.DataFrame(item['table_data'])
                    # Append to the combined table
                    combined_table = pd.concat([combined_table, table_data], ignore_index=True)
                else:
                    return jsonify({"status": "error", "message": "Missing 'table_data' in one of the items"}), 400
            
            # Convert the final combined table to JSON
            combined_table_json = combined_table.to_dict(orient='records')
            return jsonify({"status": "success", "data": combined_table_json})
        
        except Exception as e:
            return jsonify({"status": "error", "message": str(e)}), 500
    else:
        return jsonify({"status": "error", "message": "Data not found"}), 400


from flask import jsonify, request, render_template_string
import pandas as pd



@bp.route('/get_td', methods=['GET', 'POST'])
def get_table():
    # Attempt to fetch the format_id from GET or POST data
    format_id = request.args.get('format_id')
    
    if not format_id:
        # Manually parse JSON if Content-Type is not application/json
        try:
            request_data = request.get_json(silent=True)
            if request_data:
                format_id = request_data.get('format_id')
        except Exception:
            pass  # Fallback to format_id remaining None if parsing fails
    
    if not format_id:
        return jsonify({"status": "error", "message": "Format ID not provided"}), 400
    
    # Fetch data
    data = fs.GC(f"tableData/{format_id}/data")
    
    if data:
        try:
            combined_table = pd.DataFrame()  # Initialize an empty DataFrame
            
            for item in data:
                if 'table_data' in item:
                    # Convert the `table_date` to a DataFrame
                    table_data = pd.DataFrame(item['table_data'])
                    # Append to the combined table
                    combined_table = pd.concat([combined_table, table_data], ignore_index=True)
                else:
                    return jsonify({"status": "error", "message": "Missing 'table_data' in one of the items"}), 400
            
            # Convert the final combined table to HTML
            table_html = combined_table.to_html(index=False, classes='table table-bordered table-striped')
            
            # Use a simple HTML template to render the table
            html_template = f"""
            <!DOCTYPE html>
            <html lang="en">
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/twitter-bootstrap/4.6.0/css/bootstrap.min.css">
                <title>Table Data</title>
            </head>
            <body>
                <div class="container mt-4">
                    <h2 class="text-center">Combined Table Data</h2>
                    {table_html}
                </div>
            </body>
            </html>
            """
            return html_template  # Return the rendered HTML table
            
        except Exception as e:
            return jsonify({"status": "error", "message": str(e)}), 500
    else:
        return jsonify({"status": "error", "message": "Data not found"}), 400
    
import io
import xlsxwriter

from datetime import datetime

@bp.route('/get_ed', methods=['GET', 'POST'])
def get_excel():
    # Attempt to fetch the format_id from GET or POST data
    format_id = request.args.get('format_id')
    
    if not format_id:
        # Manually parse JSON if Content-Type is not application/json
        try:
            request_data = request.get_json(silent=True)
            if request_data:
                format_id = request_data.get('format_id')
        except Exception:
            pass  # Fallback to format_id remaining None if parsing fails
    
    if not format_id:
        return jsonify({"status": "error", "message": "Format ID not provided"}), 400
    
    # Fetch data
    data = fs.GC(f"tableData/{format_id}/data")
    
    if data:
        try:
            combined_table = pd.DataFrame()  # Initialize an empty DataFrame
            
            for item in data:
                if 'table_data' in item:
                    # Convert the `table_data` to a DataFrame
                    table_data = pd.DataFrame(item['table_data'])
                    # Append to the combined table
                    combined_table = pd.concat([combined_table, table_data], ignore_index=True)
                else:
                    return jsonify({"status": "error", "message": "Missing 'table_data' in one of the items"}), 400
            timestamp = datetime.now().strftime("%y-%b-%d %H:%M")
            file_name = f"{format_id}_{timestamp}"
            # Convert the combined DataFrame to an Excel file in memory
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                combined_table.to_excel(writer, index=False, sheet_name='Sheet1')
            
            # Prepare response   
            output.seek(0)
            response = Response(output, mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
            response.headers['Content-Disposition'] = f'attachment; filename={file_name}.xlsx'
            return response
        
        except Exception as e:
            return jsonify({"status": "error", "message": str(e)}), 500
    else:
        return jsonify({"status": "error", "message": "Data not found"}), 400
