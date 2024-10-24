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
    uemail=session['profile']['email']
    # Fetch the format structure from Firebase
    format = fs.G("formats", document_id=format_id)
    aw={}
    try:
        aw=format["allowedUsers"]
        print(aw)
    except:
        print("no Allowed used")
    if uemail in aw:
    # Extract field_groups from the format_data
        field_groups = format.get('field_groups', [])

        data=fs.G(f"tableData/{format_id}/data", document_id=uemail)
        try:
            data=data.get('table_data',[])
        except:
            data={}

    # Render the form with the field_groups
        return render_template('table.html', format=json.dumps(format),user=session['profile'],data=json.dumps(data))
    else:
        return render_template('basetemp.html',mainMsg="You are not authorized, Please Login with a Differnt ID (Hint Office )",user=session['profile'])


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