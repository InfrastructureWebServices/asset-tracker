# Setup

## Requirements
* VS Code
* Python 3.10+
* git

## Setup Python Virtual Environment (optional)
* In the root directory (i.e. qr-tracker)
* `python -m  venv venv`
* `source venv/bin/activate`

## Install Python Modules
* `pip install -r requirements.txt`
* Please note, this includes modules not neccessary for this repository. Alternatively you can run the server and install missing modules as needed. Most likely `flask`, `flask_sqlalchemy`, `flask_login`, `python_dotenv`, `qr_code`. 

## Configuring .env file
* Copy the `template.env` and rename it `.env`
* Go to `https://www.twilio.com/en-us` and setup a trial account, get the twilio if you want to test sms functionality. Otherwise the authentication code will be output to the terminal if `DEBUG=true`.
* Generate a flask secrete key, generate it yourself or use an online tool like `https://onlinetools.com/hex/generate-random-hex-numbers`.
* Enter the path to the sqlite database that will be generated in the root directory.
  * For linux: `sqlite:////home/user/path/to/git/repo/db.sqlite`.
  * For windows `sqlite:///C:\\Users\\user\\path\\to\\git\\repo\\db.sqlite`, noting the escaped backslashes for windows paths.

## Running Flask Server
* Run from debugger in VS Code
* Open the address shown in the terminal in the browser (ctrl + click)

### Or from terminal
* `python flask_server.py`

## Development Log

### Add QR code generator

### Add development json database

### Add asset input forms

### Add QR scanning view
 * QR codes
 * barcodes? Not in this library

### Migrate database to SQL

### Authentication using SMS
 * mandatory first and last name fields in verify SMS code
 * login after first, hide these fields

## Options for future development
 * Track changes log
 * admin controls
 * Photos
 * Add create pick list