# -*- coding: UTF-8 -*-
import base64, sys, constant
from aip import AipFace

reload(sys)
sys.setdefaultencoding('utf8')

# 初始化AipFace对象
aipFace = AipFace(constant.APP_ID, constant.API_KEY, constant.SECRET_KEY)


def add_for_face_baidu(file_path, user_id, group_id, user_info):
    # 读取图片
    # filePath = "/home/zenith/multiface.jpg"
    file_data = open(file_path, 'rb')
    image = base64.b64encode(file_data.read())
    image_type = "BASE64"

    """ 如果有可选参数 """
    options = {"user_info": str(user_info)}

    """ 带参数调用人脸更新 """
    result = aipFace.addUser(image, image_type, str(group_id), str(user_id), options)
    print(result)

    return result['error_msg']


def search_for_face_baidu(file_path, group_id_list):
    # 读取图片
    # filePath = "C:\\Users\\Administrator\\Desktop\\01.png"
    file_data = open(file_path, 'rb')
    image = base64.b64encode(file_data.read())
    image_type = "BASE64"

    """ 如果有可选参数 """
    options = {"max_user_num":1}

    """ 带参数调用人脸搜索 """
    ptr = aipFace.search(image, image_type, group_id_list, options)
    # print(ptr)

    if ptr and ptr.has_key('result') and ptr['result'] and ptr['result'].has_key('user_list') \
            and len(ptr['result']['user_list']) > 0:
        return ptr['result']['user_list'][0]['user_id'] \
               + constant.face_info_split + ptr['result']['user_list'][0]['user_info']


def detect_for_face_baidu(file_data):
    # 读取图片
    # filePath = "C:\\Users\\Administrator\\Desktop\\01.png"
    # f = open(filePath,'rb')
    image = base64.b64encode(file_data)
    image_type = "BASE64"

    """ 如果有可选参数 """
    options = {"max_face_num": 5}

    """ 带参数调用人脸搜索 """
    ptr = aipFace.detect(image, image_type, options)

    if ptr and ptr.has_key('result') and ptr['result'] and ptr['result'].has_key('face_list'):
        return (
        [face['location']['top'], face['location']['left'], face['location']['height'], face['location']['width']] for
        face in ptr['result']['face_list'])


if __name__ == '__main__':
    filePath = "/home/zenith/multiface.jpg"
    f = open(filePath, 'rb')
    print(type(f.read()))
    print(search_for_face_baidu(filePath,'test'))
