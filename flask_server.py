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

@app.route('/generate-qr-batch')
def generate_qr_batch():
    if request.method == "GET":
        return render_template('generate.html', base_url=base_url)
    elif request.method == "POST":
        
        return render_template('qr-batch.html', base_url=base_url)
