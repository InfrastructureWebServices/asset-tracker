# modules
from flask import Flask, request, Response, redirect, send_from_directory, render_template, send_file, jsonify
import os
from os import path
import json
from dotenv import load_dotenv
from datetime import datetime, timedelta
import qrcode
import uuid
import base64
import csv
from io import BytesIO, StringIO


from flask_sqlalchemy import SQLAlchemy
db = SQLAlchemy()
from model.model import *
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, login_required, login_user

load_dotenv('.env')

# check database json exists, if not create it
directory = path.dirname(__file__)
database_path = path.join(directory, 'database.json')
if not path.exists(database_path):
    with open(database_path, 'w') as f:
        f.write('{}')

# flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ['SECRET_KEY']
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['SQLALCHEMY_DATABASE_URI']
db.init_app(app)

login_manager = LoginManager()
login_manager.login_view = '/login'
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    # since the user_id is just the primary key of our user table, use it in the query for the user
    return User.query.get(int(user_id))

with app.app_context():
#     db.create_all()
    if db.session.query(User).count() == 0:
        new_user = User(email="brendan.horne@outlook.com", name="Brendan Horne", password=generate_password_hash("test123abc", method='sha256'))
        db.session.add(new_user)
        # add the new user to the database
        db.session.commit()

base_url = "/private/asset-tracker/"
domain = 'https://www.infrastructurewebservices.com/private/asset-tracker/'

# debug variable dependents
DEBUG = os.environ.get('DEBUG') != None and os.environ.get('DEBUG') == 'true'
if DEBUG:
    app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
    base_url = "/"
    domain = "http://localhost:5000/"

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(app.root_path, 'favicon.ico', mimetype='image/vnd.microsoft.icon')

@app.route('/public/<path:path>')
def send_report(path):
    return send_from_directory('public', path)

def generate_url(id):
    return '%sassets/%s' % (domain, id)

def generate_qr(url):
    img = qrcode.make(url)
    buffered = BytesIO()
    img.save(buffered, format='png')
    base64_bytes = base64.b64encode(buffered.getvalue())
    base64_utf8 = base64_bytes.decode('utf-8')
    img_str = '<img height="120px" width="120px" src="data:image/png;base64,%s" />' % base64_utf8
    return img_str


phone_sessions = {
    
}

@app.route('/')
@login_required
def home():
    return render_template('dashboard.html', base_url=base_url)

@app.route('/login')
def login():
    return render_template('login.html', base_url=base_url)

@app.route('/generate-sms-code', methods=["POST"])
def genenerate_sms_code():
    data = request.form
    from sms import send_sms
    import secrets
    code = secrets.token_hex(3)
    mobile_number = "+61%s" % (data['mobile_number'])
    phone_sessions[mobile_number] = {
        "code": code, "ts": datetime.now()
    }
    send_sms(mobile_number, code)
    return redirect('/verify-sms-code/%s' %(data['mobile_number']))

@app.route('/verify-sms-code/<mobile_number>', methods=["GET", "POST"])
def verify_sms_code(mobile_number):
    if request.method == "GET":
        return render_template('verify-sms-code.html', base_url=base_url, mobile_number=mobile_number)
    else:
        mobile_number = "+61%s" % (mobile_number)
        data = request.form
        verification_code = data['verification_code']
        now = datetime.now()
        if mobile_number in phone_sessions:
            session = phone_sessions[mobile_number]
            if verification_code == session['code'] and (now - session['ts'] < timedelta(minutes=5)):
                user = User.query.filter_by(email="brendan.horne@outlook.com").first()
                login_user(user, remember=True)
                del phone_sessions[mobile_number] # don't allow code to be shared
                return redirect('/')
        return render_template('verify-sms-code.html', base_url=base_url, mobile_number=mobile_number, error_message="Invalid code!")

@app.route('/scanner')
@login_required
def scanner():
    return render_template('scanner.html', base_url=base_url)

@app.route('/show-database')
@login_required
def show_database():
    with open(database_path, 'r') as f:
        asset_database = json.loads(f.read())
    for asset in asset_database:
        asset_data = asset_database[asset]
        id = asset_data['id']
        url = generate_url(id)
        asset_data['url'] = url
        asset_data['qr'] = generate_qr(url)
    return render_template('show-database.html', base_url=base_url, asset_database=asset_database)

@app.route('/generate-qr-batch', methods=['GET', 'POST'])
@login_required
def generate_qr_batch():
    if request.method == "GET":
        return render_template('generate.html', base_url=base_url)
    elif request.method == "POST":
        data = request.form
        asset_type = data['type']
        with open(database_path, 'r') as f:
            asset_database = json.loads(f.read())
        csv_data = StringIO()
        writer = csv.writer(csv_data, delimiter=',', lineterminator=',\n')
        writer.writerow(['urls'])
        qrs = []
        now = datetime.now()
        timestamp = now.strftime("%A %d/%m/%Y, %H:%M:%S")
        for i in range(0, int(data['quantity'])):
            id = str(uuid.uuid4())
            url = generate_url(id)
            writer.writerow([url])
            img_str = generate_qr(url)
            qrs.append({"image": img_str, "url": url, "type": asset_type})
            asset_database[id] = { "id": id, "type": asset_type, "description": "Generated on %s" % timestamp}
        csv_string = csv_data.getvalue()
        with open(database_path, 'w') as f:
            f.write(json.dumps(asset_database, indent='\t'))
        return render_template('qr-batch.html', base_url=base_url, qrs=qrs, csv=csv_string)
    
@app.route('/assets/<uuid>')
@login_required
def asset(uuid):
    with open(database_path, 'r') as f:
        asset_database = json.loads(f.read())
    if uuid in asset_database:
        asset_data = asset_database.get(uuid)
        if asset_data['type'] == 'equipment':
            return render_template('equipment.html', base_url=base_url, asset_data=asset_data)
        elif asset_data['type'] == 'isolation':
            return render_template('electrical-isolation.html', base_url=base_url, asset_data=asset_data)
    else:
        return render_template('asset.html', base_url=base_url, asset_data=None)
    
@app.route('/assets/update/<uuid>', methods=['POST'])
@login_required
def update_asset(uuid):
    with open(database_path, 'r') as f:
        asset_database = json.loads(f.read())
    if uuid in asset_database:
        asset_data = asset_database.get(uuid)
        id = asset_data['id']
        data = request.form
        for property in data:
            asset_data[property] = data[property]
        asset_database[id] = asset_data
        with open(database_path, 'w') as f:
            f.write(json.dumps(asset_database, indent='\t'))
        return redirect('%sassets/%s' % (base_url, id))
    else:
        return render_template('asset.html', base_url=base_url, asset_data=None)

