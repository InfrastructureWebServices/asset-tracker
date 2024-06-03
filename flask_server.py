# modules
from flask import Flask, request, Response, redirect, send_from_directory, render_template, send_file, jsonify
from time import sleep
import threading
import queue
import sys
import os
from os import path
import json
import re
import xml.etree.ElementTree as ET
from dotenv import load_dotenv
from datetime import datetime
import qrcode
import uuid
import base64
from io import BytesIO

load_dotenv('.env')

# local modules


# flask app
app = Flask(__name__)

DEBUG = os.environ.get('DEBUG') != None and os.environ.get('DEBUG') == 'true'
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
base_url = "/"

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(app.root_path, 'favicon.ico', mimetype='image/vnd.microsoft.icon')

@app.route('/public/<path:path>')
def send_report(path):
    return send_from_directory('public', path)

@app.route('/')
def home():
    return render_template('dashboard.html', base_url=base_url)

@app.route('/generate-qr-batch', methods=['GET', 'POST'])
def generate_qr_batch():
    if request.method == "GET":
        return render_template('generate.html', base_url=base_url)
    elif request.method == "POST":
        data = request.form
        with open('database.json', 'r') as f:
            asset_database = json.loads(f.read())
        qrs = []
        now = datetime.now()
        timestamp = now.strftime("%A %d/%m/%Y, %H:%M:%S")
        for i in range(0, int(data['quantity'])):
            id = str(uuid.uuid4())
            url = 'http://localhost:5000/assets/%s' % id
            img = qrcode.make(url)
            buffered = BytesIO()
            img.save(buffered, format='png')
            base64_bytes = base64.b64encode(buffered.getvalue())
            base64_utf8 = base64_bytes.decode('utf-8')
            img_str = '<img src="data:image/png;base64,%s" />' % base64_utf8
            qrs.append({"image": img_str, "url": url})
            asset_database[id] = { "id": id, "description": "Generated on %s" % timestamp}
        with open('database.json', 'w') as f:
            f.write(json.dumps(asset_database, indent='\t'))
        return render_template('qr-batch.html', base_url=base_url, qrs=qrs)
    
@app.route('/assets/<uuid>')
def asset(uuid):
    with open('database.json', 'r') as f:
        asset_database = json.loads(f.read())
    if uuid in asset_database:
        asset_data = asset_database.get(uuid)
        return render_template('asset.html', base_url=base_url, asset_data=asset_data)
    else:
        return render_template('asset.html', base_url=base_url, asset_data=None)
    
@app.route('/assets/update/<uuid>', methods=['POST'])
def update_asset(uuid):
    with open('database.json', 'r') as f:
        asset_database = json.loads(f.read())
    if uuid in asset_database:
        asset_data = asset_database.get(uuid)
        id = asset_data['id']
        data = request.form
        asset_data['description'] = data['description']
        asset_database[id] = asset_data
        with open('database.json', 'w') as f:
            f.write(json.dumps(asset_database, indent='\t'))
        return redirect('assets/%s' % id)
    else:
        return render_template('asset.html', base_url=base_url, asset_data=None)

