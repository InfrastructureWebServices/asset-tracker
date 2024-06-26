# modules
from flask import Flask, request, Response, redirect, send_from_directory, render_template, send_file, jsonify
import os
from os import path
import json
from dotenv import load_dotenv
from zoneinfo import ZoneInfo
from datetime import datetime, timezone, timedelta
import qrcode
import uuid
import base64
import csv
from io import BytesIO, StringIO
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, login_required, login_user, current_user
import pytz
import calendar
from uuid import UUID as UUIDC, uuid4

# local modules
from model.model import *

load_dotenv('.env')
base_url = "/private/asset-tracker/"
domain = 'https://www.infrastructurewebservices.com/private/asset-tracker/'

# debug variable dependents
DEBUG = os.environ.get('DEBUG') != None and os.environ.get('DEBUG') == 'true'
if DEBUG:
    base_url = "/"
    domain = "http://localhost:5000/"

directory = path.dirname(__file__)

# flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ['SECRET_KEY']
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['SQLALCHEMY_DATABASE_URI']
db.init_app(app)
if DEBUG:
    app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0


# login manager
login_manager = LoginManager()
login_manager.login_view = '%slogin' % base_url
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    # since the user_id is just the primary key of our user table, use it in the query for the user
    return User.query.get(int(user_id))

# check database json exists, if not create it
database_path = path.join(directory, 'db.sqlite')
if not path.exists(database_path):
    with app.app_context():
        db.create_all()

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
    full_mobile_number = "+61%s" % (data['mobile_number'])
    with SessionFactory() as session:
        t = Verification_Session
        count = session.query(t).where(t.mobile_number==full_mobile_number).count()
        if count > 0:
            verification_sessions = session.query(t).where(t.mobile_number==full_mobile_number).all()
            for verification_session in verification_sessions:
                session.delete(verification_session)
            session.commit()
        new_verification_session = Verification_Session(code=code, mobile_number=full_mobile_number, existing_user=user_exists(full_mobile_number))
        session.add(new_verification_session)
        session.commit()

    send_sms(full_mobile_number, code) # don't waste trial sms calls, save for demo
    # print("code", code)
    return redirect('/verify-sms-code/%s' %(data['mobile_number']))

def user_exists(full_mobile_number):
    return User.query.filter_by(mobile_number=full_mobile_number).count() > 0

@app.route('/verify-sms-code/<mobile_number>', methods=["GET", "POST"])
def verify_sms_code(mobile_number):
    full_mobile_number = "+61%s" % (mobile_number)
    if request.method == "GET":
        if user_exists(full_mobile_number):
            return render_template('verify-sms-code.html', base_url=base_url, mobile_number=mobile_number, existing_user=True)
        else:
            return render_template('verify-sms-code.html', base_url=base_url, mobile_number=mobile_number)
    else:
        data = request.form
        verification_code = data['verification_code']
        now = datetime.now(pytz.utc)
        count_activate_sessions = Verification_Session.query.filter_by(mobile_number=full_mobile_number, active=True).count()
        if count_activate_sessions == 1:
            verification_session = Verification_Session.query.filter_by(mobile_number=full_mobile_number, active=True).one()
            ts = calendar.timegm(verification_session.ts.utctimetuple())
            now = calendar.timegm(now.utctimetuple())
            timeout = (now - ts) > 3*60 # 3 minutes
            if verification_code == verification_session.code and timeout == False: # test time out works
                if data.get('first_name') != None and data.get('last_name') != None:
                    user = User(first_name=data['first_name'], last_name=data['last_name'], mobile_number=full_mobile_number)
                    with SessionFactory() as session:
                        session.add(user)
                        session.commit()
                user = User.query.filter_by(mobile_number=full_mobile_number).first()
                login_user(user, remember=True)
                Verification_Session.query.filter_by(id=verification_session.id).delete()
                return redirect('/')
        return render_template('verify-sms-code.html', base_url=base_url, mobile_number=mobile_number, error="Invalid or expired code!")

@app.route('/scanner')
@login_required
def scanner():
    return render_template('scanner.html', base_url=base_url)

@app.route('/show-database')
@login_required
def show_database():
    with SessionFactory() as session:
        assets = session.query(Asset).all()
    return render_template('show-database.html', base_url=base_url, assets=assets, generate_url=generate_url, generate_qr=generate_qr)

@app.route('/generate-qr-batch', methods=['GET', 'POST'])
@login_required
def generate_qr_batch():
    if request.method == "GET":
        return render_template('generate.html', base_url=base_url)
    elif request.method == "POST":
        data = request.form
        asset_type = data['type']
        csv_data = StringIO()
        writer = csv.writer(csv_data, delimiter=',', lineterminator=',\n')
        writer.writerow(['urls'])
        qrs = []
        with SessionFactory() as session:
            for i in range(0, int(data['quantity'])):
                asset = Asset()
                session.add(asset)
                session.commit()
                id = asset.id
                url = generate_url(id)
                writer.writerow([url])
                img_str = generate_qr(url)
                qrs.append({"image": img_str, "url": url, "type": asset_type})
            csv_string = csv_data.getvalue()
            return render_template('qr-batch.html', base_url=base_url, qrs=qrs, csv=csv_string)
    
@app.route('/assets/<uuid_str>')
@login_required
def asset(uuid_str):
    with SessionFactory() as session:
        uuid = UUIDC(uuid_str)
        asset = session.query(Asset).get(uuid)
        change_logs = session.query(Change_Log).filter_by(asset_id=uuid).all()
        if asset != None:
            return render_template('equipment.html', base_url=base_url, asset=asset, change_logs=change_logs)
        else: 
            return render_template('404.html', base_url=base_url)
        
@app.route('/assets/<uuid_str>/update', methods=['POST'])
@login_required
def update_asset(uuid_str):
    data = request.form
    uuid = UUIDC(uuid_str)
    change_log_str = ""
    with SessionFactory() as session:
        asset = session.query(Asset).get(uuid)
        for property in data:
            if data[property] != getattr(asset, property):
                if data[property] == '' and getattr(asset, property) == None: continue
                change_log_str = "%s (%s -> %s)" % (property, getattr(asset, property), data[property])
                change_log = Change_Log(user_id=current_user.id, value=change_log_str, asset_id=uuid)
                session.add(change_log)
                setattr(asset, property, data[property])
        session.commit()
        return redirect('/assets/%s' % uuid_str)

