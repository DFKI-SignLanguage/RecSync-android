# TODO:// Need to do changes based on file storage idea. i.e what folder structure etc 
from flask import Flask, request, jsonify
import os
from werkzeug.utils import secure_filename

try:
    from io import BytesIO
except ImportError:
    from StringIO import StringIO as BytesIO
app = Flask(__name__)

app.secret_key = "recSync-fileserver"

UPLOAD_FOLDER = 'uploads/'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'mov', 'mp4', 'csv'])


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/')
def main():
    return 'Homepage'


@app.route('/upload', methods=['POST'])
def upload_file():

    if 'file' not in request.files:
        resp = jsonify({'message': 'No file part in the request'})
        resp.status_code = 400
        return resp

    session_prefix, client_id = request.form.get("session_prefix"), request.form.get("client_id")
    print("Request to upload received from CLIENT:" + client_id + " for session " + session_prefix)

    files = request.files.getlist('file')
    files.extend(request.files.getlist('csv_file'))
    errors = {}
    success = False

    # create a directory based on session and client id
    directory_path = os.path.join(app.config['UPLOAD_FOLDER'], session_prefix + "/" + client_id + "/")
    if not os.path.exists(directory_path):
        os.makedirs(directory_path)

    for file in files:
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            print("received file: " + filename + " from CLIENT:" + client_id + " for session " + session_prefix)
            file.save(os.path.join(directory_path, filename))
            success = True
        else:
            errors[file.filename] = 'File type is not allowed'

    resp = jsonify({'message': 'Files successfully downloaded'})
    resp.status_code = 201
    return resp


@app.route('/namelist', methods=['POST'])
def print_filelist():
    print("CLIENT ID:" + request.form.get("client_id", "") + " have these FILES:" + request.form.get("file_list", []))
    resp = jsonify({'message': 'File List Printed'})
    resp.status_code = 200
    return resp


#
# MAIN
#
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
