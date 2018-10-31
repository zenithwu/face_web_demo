# coding=utf8
import ConfigParser
import os
import pickle

import cv2
import face_recognition

from constant import show_face_path, model_dir

# video_capture = cv2.VideoCapture(0)
# video_capture = cv2.VideoCapture("rtmp://rtmp.open.ys7.com/openlive/9e6c5a1a61e648d0bb7143db71e363c6.hd")
#video_capture = cv2.VideoCapture("http://hls.open.ys7.com/openlive/1bfb0f89a7924ec28d23d637cc0a7267.m3u8")
video_capture = cv2.VideoCapture("rtsp://show_face:face_show@863@192.168.0.215:554/h264/ch1/sub/av_stream")

def show_face():
    # knn_clf = None
    distance_threshold = 0.9
    # load knn
    with open(os.path.join(model_dir, 'trained_knn_model.clf'), 'rb') as f:
        knn_clf = pickle.load(f)
    # STEP 2: Using the trained classifier, make predictions for unknown images
    # Get a reference to webcam #0 (the default one)

    # Initialize some variables
    face_names = []
    process_this_frame = True
    while True:
        try:
            # Grab a single frame of video
            ret, frame = video_capture.read()
            # Resize frame of video to 1/4 size for faster face recognition processing
            small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
            # Convert the image from BGR color (which OpenCV uses) to RGB color (which face_recognition uses)
            rgb_small_frame = small_frame[:, :, ::-1]
            # cv2.imshow('small',rgb_small_frame)
            # Only process every other frame of video to save time
            if process_this_frame:
                # Find all the faces and face encodings in the current frame of video
                face_locations = face_recognition.face_locations(rgb_small_frame)
                user_ids = []

                if len(face_locations) > 0:
                    face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)
                    # Use the KNN model to find the best matches for the test face
                    closest_distances = knn_clf.kneighbors(face_encodings, n_neighbors=1)
                    are_matches = [closest_distances[0][i][0] <= distance_threshold for i in range(len(face_locations))]

                    # Predict classes and remove classifications that aren't within the threshold
                    user_ids = [pred if rec else "unknown" for pred, loc, rec in
                                zip(knn_clf.predict(face_encodings), face_locations, are_matches)]
                    # face_names = knn_clf.predict(face_encodings)
                    # Display the results
                    for user_id in user_ids:
                        print("-----------"+user_id)
                        if user_id is not "unknown":
                            face_cf = ConfigParser.ConfigParser()
                            face_cf.read(show_face_path)
                            if not face_cf.has_section(user_id):
                                face_cf.add_section(user_id)
                            # 更新offset
                            face_cf.write(open(show_face_path, "w"))
        except:
            continue
        process_this_frame = not process_this_frame
        print(len(user_ids))

        # Display the resulting image
        # cv2.imshow('Video', frame)

        # Hit 'q' on the keyboard to quit!
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break


if __name__ == '__main__':
    show_face()
    # Release handle to the webcam
    video_capture.release()
    cv2.destroyAllWindows()
    # print(get_face_info_list("/home/zenith/multiface.jpg"))
