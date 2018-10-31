# coding=utf8
import ConfigParser
import time

from baidu_face_util import detect_for_face_baidu, search_for_face_baidu
import cv2
import math

from constant import show_face_path, face_name, face_phone, face_position, face_temp_name, img_temp_name, \
    face_id, face_info_split

video_capture = cv2.VideoCapture(0)


def show_face():
    while True:
        # time.sleep(0.5)
        # Grab a single frame of video
        print(str(time.time()) + "begin video_capture.read()")
        ret, frame = video_capture.read()
        small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
        cv2.imshow('frame', small_frame)
        print(str(time.time()) + "end video_capture.read()")
        cv2.imwrite(img_temp_name, small_frame)
        print(str(time.time()) + "end imwrite")
        for info in get_face_info_list(img_temp_name):
            if info and info.find(face_info_split) > -1:
                info_array = info.split(face_info_split, 3)
                if len(info_array) == 4:
                    face_cf = ConfigParser.ConfigParser()
                    face_cf.read(show_face_path)
                    id = info_array[0]
                    if not face_cf.has_section(id):
                        face_cf.add_section(id)
                    face_cf.set(id, face_name, info_array[1])
                    face_cf.set(id, face_position, info_array[2])
                    face_cf.set(id, face_phone, info_array[3])
                    # 更新offset
                    face_cf.write(open(show_face_path, "w"))

        # # Hit 'q' on the keyboard to quit!
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break


def get_face_info_list(file_path):
    f = open(file_path, 'rb')
    info_list = []
    result_list = detect_for_face_baidu(f.read())
    print(str(time.time()) + "end detect_for_face")
    if result_list:
        org = cv2.imread(file_path)
        # top:height+top,left:left+width
        for top, left, height, width in result_list:
            top_v = int(math.floor(top) - 20 if math.floor(top) > 20 else 0)
            left_v = int(math.floor(left) - 20 if math.floor(left) > 20 else 0)
            h_v = int(math.ceil(top + height) + 20)
            w_v = int(math.ceil(left + width) + 20)
            roi = org[top_v:h_v, left_v:w_v]
            # cv2.imshow('roi', roi)
            # cv2.waitKey(0)
            cv2.imwrite(face_temp_name, roi)
            print(str(time.time()) + "begin search_for_face")
            info_list.append(search_for_face_baidu(face_temp_name, 'test'))
            print(str(time.time()) + "end search_for_face")
    print(str(time.time()) + "end get_face_info_list")
    return info_list


if __name__ == '__main__':
    show_face()
    # Release handle to the webcam
    video_capture.release()
    cv2.destroyAllWindows()
    # print(get_face_info_list("/home/zenith/multiface.jpg"))
