import json
import os
import sys

from flask import Flask
from flask import render_template, redirect, url_for, request, flash, make_response
from flask_login import LoginManager
from flask_restful import Api

path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(path)

from libs.pylib import get_random_uuid
from libs.settings import SQLALCHEMY_DATABASE_URI
from libs.settings import FLASK_SESSION_TYPE, FLASK_UPLOAD_FOLDER
from libs.settings import FLASK_ALLOWED_EXTENSIONS, FLASK_RESOURCE_STATUSES
from libs.db import DbProxy


__NAME__ = "monoringOfResources"
ALLOWED_EXTENSIONS = set(FLASK_ALLOWED_EXTENSIONS)
STATUSES = set(FLASK_RESOURCE_STATUSES)

# Create application
app = Flask(__NAME__)
#, static_url_path = '/home/ubuntu/ocr/storage',
#                      static_folder = '/home/ubuntu/ocr/storage')

# Create dummy secrey key so we can use sessions
app.secret_key = get_random_uuid()
app.url_map.strict_slashes = False
app.config['SESSION_TYPE'] = FLASK_SESSION_TYPE
app.config['UPLOAD_FOLDER'] = FLASK_UPLOAD_FOLDER
app.config['SQLALCHEMY_DATABASE_URI'] = SQLALCHEMY_DATABASE_URI
api = Api(app)

# Create database
# db = SQLAlchemy(app)

# Create admin
login_manager = LoginManager()


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

def output_xml(data, code, headers=None):
    """Makes a Flask response with a XML encoded body"""
    resp = make_response(json.dumps(data), code)
    resp.headers.extend(headers or {'content-type': 'application/xml'})
    return resp

# Routes
# Main pages
@app.route('/')
def results_list_page():
    dbproxy = DbProxy()
    results = dbproxy.get_all()
    for i in results:
        if i.status:
            i.status = 'PASS'
        else:
            i.status = 'FAIL'
    # resources = Resource.query.all()
    context = {'results': results}
    return render_template('index.html', data=context)

@app.route('/help')
def help_page():
    return render_template('help.html')

if __name__ == '__main__':
    # db.drop_all()
    # db.create_all()
    # run_services()
    app.run('127.0.0.1', 8989, debug=True)
