# coding=utf8

import ConfigParser
import base64
import json
import os
import pickle
import sys
import urllib2
import uuid
from cStringIO import StringIO

import face_recognition
import time
from flask import Flask, render_template, send_from_directory, request, redirect, make_response

from constant import show_face_path, face_src, face_img_fix, model_dir, face_id, face_name

reload(sys)
sys.setdefaultencoding('utf8')

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

app = Flask(__name__)
# refers to application_top
APP_ROOT = os.path.dirname(os.path.abspath(__file__))
APP_DATA = os.path.join(APP_ROOT, 'data')
FACE_DATA = os.path.join(APP_ROOT, 'data', 'faces')

@app.route('/favicon.ico',methods=['GET'])
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static/image/'),
                               '863logo.ico')


@app.route('/face_info')
def face_info():
    faces = list()
    face_cf = ConfigParser.ConfigParser()
    face_cf.read(os.path.join(APP_ROOT, show_face_path))
    user_ids = face_cf.sections()
    for user_id in user_ids:
        info = dict()
        info[face_id] = user_id
        info[face_src] = user_id + face_img_fix
        info[face_name]=json.loads(urllib2.urlopen(urllib2.Request("http://i.863jp.com.cn:86/ioms/attendance/getUserInfoByUsername/"+user_id)).read()).get("realName")
        faces.append(info)
        face_cf.remove_section(user_id)
    face_cf.write(open(os.path.join(APP_ROOT, show_face_path), 'w'))
    return json.dumps(faces)

@app.route('/add_face', methods=['GET'])
def add_face():
    return render_template('add_face.html')

@app.route('/show_face', methods=['GET'])
def show_face():
    date=time.strftime("%Y-%m-%d")
    return render_template('show_face.html',date=date)

@app.route('/show_photo/<string:filename>', methods=['GET'])
def show_photo(filename):
    if request.method == 'GET':
        if filename is None:
            pass
        else:
            image_data = open(os.path.join(APP_DATA, 'train/%s' % filename), "rb").read()
            response = make_response(image_data)
            response.headers['Content-Type'] = 'image/png'
            return response
    else:
        pass


@app.route('/show_ext_photo/<string:user_id>/<string:filename>', methods=['GET'])
def show_ext_photo(filename, user_id):
    if request.method == 'GET':
        if filename is None:
            pass
        else:
            image_data = open(os.path.join(APP_DATA, 'train_ext/%s/%s' % (user_id, filename)), "rb").read()
            response = make_response(image_data)
            response.headers['Content-Type'] = 'image/png'
            return response
    else:
        pass


@app.route('/user_ext_img/<string:user_id>', methods=['GET'])
def user_ext_img(user_id):
    if request.method == 'GET':
        if user_id is None:
            pass
        else:
            return json.dumps(os.listdir(os.path.join(APP_DATA, 'train_ext/%s' % user_id)))
    else:
        pass


# @app.route('/do_add_face', methods=['POST'])
# def do_add_face():
#     if 'file' not in request.files:
#         return redirect(request.url)
#     file_data = request.files['file']
#     user_id = request.form['userId']
#     user_name = request.form['userName']
#     user_position = request.form['userPosition']
#     user_phone = request.form['userPhone']
#     is_show = request.form['isShow']
#     if file_data.filename == '':
#         return redirect(request.url)
#     if file_data and allowed_file(file_data.filename):
#         img_path = os.path.join(APP_DATA, 'train', user_id, str(uuid.uuid1()) + face_img_fix)
#         if not os.path.exists(os.path.join(APP_DATA, 'train', user_id)):
#             os.mkdir(os.path.join(APP_DATA, 'train', user_id))
#         file_data.save(img_path)
#         # 设置成显示封面
#         if is_show == "1":
#             open(os.path.join(FACE_DATA, user_id + face_img_fix), "wb").write(open(img_path, "rb").read())
#         return render_template('result.html',
#                                msg=add_for_face(os.path.join(APP_ROOT, user_info_path), user_id, user_name,
#                                                 user_position, user_phone))

@app.route('/do_add_face', methods=['POST'])
def do_add_face():
    if 'file' not in request.files:
        return redirect(request.url)
    file_data = request.files['file']
    user_id = request.form['userId']

    if file_data.filename == '' or user_id == '':
        return redirect(request.url)
    if file_data and allowed_file(file_data.filename):
        img_path = os.path.join(APP_DATA, 'train_ext', user_id, str(uuid.uuid1()) + face_img_fix)
        if not os.path.exists(os.path.join(APP_DATA, 'train_ext', user_id)):
            os.mkdir(os.path.join(APP_DATA, 'train_ext', user_id))
        file_data.save(img_path)
        return render_template('result.html', msg="sucess")


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


#
# def add_for_face(path, user_id, user_name, user_position, user_phone):
#     user_cf = ConfigParser.ConfigParser()
#     user_cf.read(path)
#     if not user_cf.has_section(user_id):
#         user_cf.add_section(user_id)
#     user_cf.set(user_id, face_name, user_name)
#     user_cf.set(user_id, face_position, user_position)
#     user_cf.set(user_id, face_phone, user_phone)
#     user_cf.write(open(path, "w"))
#     return "sucess"


@app.route('/detect_faces_in_image', methods=['POST'])
def detect_faces_in_image():
    # Check if a valid image file was uploaded
    file_code = request.form['file_code']
    # print(file_code)
    faces = []
    #must be a img
    if str(file_code).find("data:image/png;base64,")>=0:
        file_code = str(file_code).replace("data:image/png;base64,", "")
        binary_data = base64.b64decode(file_code)
        file_data = StringIO(binary_data)

        distance_threshold = 0.6

        if file_data:
            # Load the uploaded image file
            img = face_recognition.load_image_file(file_data)
            # Get face encodings for any faces in the uploaded image
            face_encodings = face_recognition.face_encodings(img)

            if len(face_encodings) > 0:
                # Use the KNN model to find the best matches for the test face
                with open(os.path.join(APP_ROOT, model_dir, 'trained_knn_model.clf'), 'rb') as f:
                    knn_clf = pickle.load(f)
                closest_distances = knn_clf.kneighbors(face_encodings, n_neighbors=1)
                are_matches = [closest_distances[0][i][0] <= distance_threshold for i in range(len(face_encodings))]

                # Predict classes and remove classifications that aren't within the threshold
                user_ids = [pred if rec else "unknown" for pred, rec in
                            zip(knn_clf.predict(face_encodings), are_matches)]
                for user_id in user_ids:
                    info = dict()
                    info[face_id] = user_id
                    info[face_src] = user_id + face_img_fix
                    info[face_name]=json.loads(urllib2.urlopen(urllib2.Request("http://i.863jp.com.cn:86/ioms/attendance/getUserInfoByUsername/"+user_id)).read()).get("realName")
                    faces.append(info)
    print(json.dumps(faces))
    return json.dumps(faces)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port='8089', debug=False, threaded=True)
    # print(uuid.uuid1())
