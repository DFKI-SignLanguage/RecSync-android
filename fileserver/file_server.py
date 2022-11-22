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

UPLOAD_FOLDER = 'static/uploads/'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'mov', 'mp4'])

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def main():
    return 'Homepage'

@app.route('/upload', methods=['POST'])
def upload_file():
   #import pdb; pdb.set_trace()
   if 'file' not in request.files:
           resp = jsonify({'message' : 'No file part in the request'})
           resp.status_code = 400
           return resp

   files = request.files.getlist('file')

   errors = {}
   success = False

   for file in files:
       if file and allowed_file(file.filename):
           filename = secure_filename(file.filename)
           file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
           success = True
       else:
           errors[file.filename] = 'File type is not allowed'

   if success and errors:
       errors['message'] = 'File(s) successfully uploaded'
       resp = jsonify(errors)
       resp.status_code = 500
       return resp
   if success:
       resp = jsonify({'message' : 'Files successfully uploaded'})
       resp.status_code = 201
       return resp
   else:
       resp = jsonify(errors)
       resp.status_code = 500
       return resp

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000,debug=True)