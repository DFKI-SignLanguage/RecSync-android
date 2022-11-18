# TODO:// Need to do changes based on file storage idea. i.e what folder structure etc 
from flask import Flask, json, request, jsonify
import os
import urllib.request
import base64
from werkzeug.utils import secure_filename
import multipart as mp

try:
    from io import BytesIO
except ImportError:
    from StringIO import StringIO as BytesIO
app = Flask(__name__)

app.secret_key = "recSync-fileserver"

UPLOAD_FOLDER = 'static/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'mov', 'mp4'])

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def main():
    return 'Homepage'

@app.route('/upload', methods=['POST'])
def upload_file():
    # check if the post request has the file part
    data = request.get_data()
    import pdb;pdb.set_trace()
    dd = b''.join(data.split(b'\r')[3:6])[2:]
    #dd = data.split(b'\r')[5]
    with open('binary.mp4', 'wb') as wfile:
        wfile.write(dd.decode())

    if 'name' not in request.files:
        print("request inside files not found")
        resp = jsonify({'message' : 'No file part in the request'})
        print(resp.data)
        resp.status_code = 400
        return resp

    errors = {}
    success = False
    resp = jsonify({"message" : "git files"})
    resp.status_code = 200
    return resp

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000,debug=True)