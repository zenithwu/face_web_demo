# coding=utf8
import json
import math
import os
import pickle
import shutil
import sys
import urllib
import urllib2

import face_recognition
from face_recognition.face_detection_cli import image_files_in_folder
from sklearn import neighbors

from constant import model_dir, train_dir, face_img_fix, train_ext_dir, face_name


reload(sys)
sys.setdefaultencoding('utf8')

def train_model(train_dir, model_save_path=None, n_neighbors=None, knn_algo='ball_tree', verbose=False):
    X = []
    y = []

    # Loop through each person in the training set
    for class_dir in os.listdir(train_dir):
        if not os.path.isdir(os.path.join(train_dir, class_dir)):
            continue

        # Loop through each training image for the current person
        for img_path in image_files_in_folder(os.path.join(train_dir, class_dir)):
            image = face_recognition.load_image_file(img_path)
            face_bounding_boxes = face_recognition.face_locations(image)

            if len(face_bounding_boxes) != 1:
                # If there are no people (or too many people) in a training image, skip the image.
                if verbose:
                    print("Image {} not suitable for training: {}".format(img_path, "Didn't find a face" if len(
                        face_bounding_boxes) < 1 else "Found more than one face"))
            else:
                # Add face encoding for current image to the training set
                X.append(face_recognition.face_encodings(image, known_face_locations=face_bounding_boxes)[0])
                y.append(class_dir)

    # Determine how many neighbors to use for weighting in the KNN classifier
    if n_neighbors is None:
        n_neighbors = int(round(math.sqrt(len(X))))
        if verbose:
            print("Chose n_neighbors automatically:", n_neighbors)

    # Create and train the KNN classifier
    knn_clf = neighbors.KNeighborsClassifier(n_neighbors=n_neighbors, algorithm=knn_algo, weights='distance')
    knn_clf.fit(X, y)

    # Save the trained KNN classifier
    if model_save_path is not None:
        with open(model_save_path, 'wb') as f:
            pickle.dump(knn_clf, f)

    return knn_clf


def train_model_noapi(model_save_path=None, n_neighbors=None, knn_algo='ball_tree', verbose=False):
    X = []
    y = []
    for img_path in image_files_in_folder(train_dir):
        try:
            image = face_recognition.load_image_file(img_path)
        except:
            print(img_path + " is not a img")
            continue
        user_id = os.path.basename(img_path).replace(face_img_fix, "")
        face_bounding_boxes = face_recognition.face_locations(image)

        if len(face_bounding_boxes) != 1:
            # If there are no people (or too many people) in a training image, skip the image.
            if verbose:
                print("Image {} not suitable for training: {}".format(img_path, "Didn't find a face" if len(
                    face_bounding_boxes) < 1 else "Found more than one face"))
        else:
            # Add face encoding for current image to the training set
            X.append(face_recognition.face_encodings(image, known_face_locations=face_bounding_boxes)[0])
            y.append(user_id)

    for user_id in os.listdir(train_ext_dir):
        if not os.path.isdir(os.path.join(train_ext_dir, user_id)):
            continue
        # Loop through each training image for the current person
        for img_path in image_files_in_folder(os.path.join(train_ext_dir, user_id)):
            image = face_recognition.load_image_file(img_path)
            face_bounding_boxes = face_recognition.face_locations(image)

            if len(face_bounding_boxes) != 1:
                # If there are no people (or too many people) in a training image, skip the image.
                if verbose:
                    print("Image {} not suitable for training: {}".format(img_path, "Didn't find a face" if len(
                        face_bounding_boxes) < 1 else "Found more than one face"))
            else:
                # Add face encoding for current image to the training set
                X.append(face_recognition.face_encodings(image, known_face_locations=face_bounding_boxes)[0])
                y.append(user_id)

    # Determine how many neighbors to use for weighting in the KNN classifier
    if n_neighbors is None:
        n_neighbors = int(round(math.sqrt(len(X))))
        if verbose:
            print("Chose n_neighbors automatically:", n_neighbors)

    # Create and train the KNN classifier
    knn_clf = neighbors.KNeighborsClassifier(n_neighbors=n_neighbors, algorithm=knn_algo, weights='distance')
    knn_clf.fit(X, y)

    # Save the trained KNN classifier
    if model_save_path is not None:
        with open(model_save_path, 'wb') as f:
            pickle.dump(knn_clf, f)

    return knn_clf

def train_model_api(model_save_path=None, n_neighbors=None, knn_algo='ball_tree', verbose=False):
    X = []
    y = []

    url = "http://i.863jp.com.cn:86/ioms/app/getEmployeeList"
    req = urllib2.Request(url)
    res_data = urllib2.urlopen(req)
    data = json.loads(res_data.read())
    info_list= data.get("userIdList") if data.has_key("userIdList") else []
    if ( info_list !=None and len(list(info_list))>0):
        print("clean train pic:"+train_dir)
        shutil.rmtree(train_dir)
        os.mkdir(train_dir)

    for user_id in info_list:
        img_src = 'http://i.863jp.com.cn:86/ioms/static/upload/head/%s/%s.jpg' % (user_id,user_id)
        print(img_src)
        # 将远程数据下载到本地，第二个参数就是要保存到本地的文件名
        urllib.urlretrieve(img_src, os.path.join(train_dir, user_id+ face_img_fix))

    for img_path in image_files_in_folder(train_dir):
        try:
            image = face_recognition.load_image_file(img_path)
        except:
            print(img_path + " is not a img")
            if os.path.exists(img_path):
                os.remove(img_path)
            continue
        user_id = os.path.basename(img_path).replace(face_img_fix, "")
        face_bounding_boxes = face_recognition.face_locations(image)

        if len(face_bounding_boxes) != 1:
            # If there are no people (or too many people) in a training image, skip the image.
            if verbose:
                print("Image {} not suitable for training: {}".format(img_path, "Didn't find a face" if len(
                    face_bounding_boxes) < 1 else "Found more than one face"))
        else:
            # Add face encoding for current image to the training set
            X.append(face_recognition.face_encodings(image, known_face_locations=face_bounding_boxes)[0])
            y.append(user_id)

    for user_id in os.listdir(train_ext_dir):
        if not os.path.isdir(os.path.join(train_ext_dir, user_id)):
            continue
        # Loop through each training image for the current person
        for img_path in image_files_in_folder(os.path.join(train_ext_dir, user_id)):
            image = face_recognition.load_image_file(img_path)
            face_bounding_boxes = face_recognition.face_locations(image)

            if len(face_bounding_boxes) != 1:
                # If there are no people (or too many people) in a training image, skip the image.
                if verbose:
                    print("Image {} not suitable for training: {}".format(img_path, "Didn't find a face" if len(
                        face_bounding_boxes) < 1 else "Found more than one face"))
            else:
                # Add face encoding for current image to the training set
                X.append(face_recognition.face_encodings(image, known_face_locations=face_bounding_boxes)[0])
                y.append(user_id)

    # Determine how many neighbors to use for weighting in the KNN classifier
    if n_neighbors is None:
        n_neighbors = int(round(math.sqrt(len(X))))
        if verbose:
            print("Chose n_neighbors automatically:", n_neighbors)

    # Create and train the KNN classifier
    knn_clf = neighbors.KNeighborsClassifier(n_neighbors=n_neighbors, algorithm=knn_algo, weights='distance')
    knn_clf.fit(X, y)

    # Save the trained KNN classifier
    if model_save_path is not None:
        with open(model_save_path, 'wb') as f:
            pickle.dump(knn_clf, f)

    return knn_clf

if __name__ == '__main__':
    print("Training KNN classifier...")
    # train_model(train_dir, model_save_path=os.path.join(model_dir,"trained_knn_model.clf"), n_neighbors=2)
    train_model_api(model_save_path=os.path.join(model_dir, "trained_knn_model.clf"), n_neighbors=2)
    print("Training complete!")
