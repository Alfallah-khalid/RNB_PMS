from flask import Blueprint, request, render_template, session
from utils.decorators import login_required  # Import the login_required decorator
from firebase_service import FirebaseService as fs
import json
import datetime


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
    # Get the UID from headers if present, else fallback to session email
    
    uid = request.args.get('uid')
    print(uid)
    user_email = uid if uid else session['profile']['email']
    print(user_email)
    # Fetch format data from the database
    format_data = fs.G("formats", document_id=format_id)
    allowed_users = format_data.get("allowedUsers", None)

    # Authorization check
    if allowed_users is not None:
        if user_email not in allowed_users:
            return render_template(
                'baseTemp.html',
                mainMsg="You are not authorized, Please Login with a Different ID (Hint: Office email)",
                user=session['profile']
            )
    
    # Fetch field groups and user-specific data
    field_groups = format_data.get('field_groups', [])
    user_data = fs.G(f"tableData/{format_id}/data", document_id=user_email)

    # Check if user_data is None before attempting to access 'table_data'
    if user_data is None:
        table_data = []
    else:
        table_data = user_data.get('table_data', [])
    
    return render_template(
        'table.html',
        format=json.dumps(format_data),
        user=session['profile'],
        data=json.dumps(table_data)
    )





@bp.route('/submitForm', methods=['GET', 'POST'])
@login_required
def submitForm():
    try:
        data={}
        data["fields"]={}
        data["fields"] = request.get_json()
        data["metadata"]={}
        data['metadata']["ipAddress"]=request.remote_addr
        data['metadata']["Useremail"]=session['profile']['email']
        data['metadata']["time"]=datetime.datetime.now()
        fid=request.referrer.split("/")[-1]
        data['metadata']['formatID']=fid
        print(data)
        print(f"formatsData/{fid}")
        fs.CU(path=f"formatsData/{fid}/data",document_id=session['profile']['email'], data=data)
    except:
        print("hello")
    # Render the form with the field_groups
    return data



@bp.route('/submitTable', methods=['GET', 'POST'])
@login_required
def submitTable():
    try:
        data={}

        data = request.get_json()
        data["metadata"]={}
        data['metadata']["ipAddress"]=request.remote_addr
        data['metadata']["Useremail"]=session['profile']['email']
        data['metadata']["time"]=datetime.datetime.now()
        fid=request.referrer.split("/")[-1]
        data['metadata']['formatID']=fid
        print(data)
        print(f"formatsData/{fid}")
        fs.CU(path=f"tableData/{fid}/data",document_id=session['profile']['email'], data=data)
    except:
        print("hello")
    # Render the form with the field_groups
    return data