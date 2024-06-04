# modules
from flask import Flask, request, Response, redirect, send_from_directory, render_template, send_file, jsonify
import os
from os import path
import json
from dotenv import load_dotenv
from datetime import datetime
import qrcode
import uuid
import base64
from io import BytesIO

# import xml.etree.ElementTree as ET
# import threading
# import queue
# from time import sleep
# import sys
# import re

load_dotenv('.env')

# check database json exists, if not create it
directory = path.dirname(__file__)
database_path = path.join(directory, 'database.json')
if not path.exists(database_path):
    with open(database_path, 'w') as f:
        f.write('{}')

# flask app
app = Flask(__name__)
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

@app.route('/')
def home():
    return render_template('dashboard.html', base_url=base_url)

@app.route('/show-database')
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
def generate_qr_batch():
    if request.method == "GET":
        return render_template('generate.html', base_url=base_url)
    elif request.method == "POST":
        data = request.form
        asset_type = data['type']
        with open(database_path, 'r') as f:
            asset_database = json.loads(f.read())
        csv = ""
        qrs = []
        now = datetime.now()
        timestamp = now.strftime("%A %d/%m/%Y, %H:%M:%S")
        for i in range(0, int(data['quantity'])):
            id = str(uuid.uuid4())
            url = generate_url(id)
            csv += "%s\n" % url
            img_str = generate_qr(url)
            qrs.append({"image": img_str, "url": url, "type": asset_type})
            asset_database[id] = { "id": id, "type": asset_type, "description": "Generated on %s" % timestamp}
        with open(database_path, 'w') as f:
            f.write(json.dumps(asset_database, indent='\t'))
        return render_template('qr-batch.html', base_url=base_url, qrs=qrs, csv=csv)
    
@app.route('/assets/<uuid>')
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

