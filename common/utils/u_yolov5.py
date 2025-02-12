import time
import requests
import base64
from io import BytesIO
from PIL import ImageGrab


def current_screen_base64():
    """图片转base64格式"""
    try:
        buffer = BytesIO()
        img = ImageGrab.grab()
        img.save(buffer, format='PNG')
        img.close()
        img_bytes = base64.b64encode(buffer.getvalue())
        img_base64 = 'Data:image/png;base64,%s' % img_bytes.decode()
        return img_base64
    except Exception as e:
        raise Exception("截取当前屏幕图片并转base64失败：{}".format(e))


def get_bbox_center(bbox):
    """获取按钮坐标"""
    x = int(bbox[0] + (bbox[2] - bbox[0]) / 2)
    y = int(bbox[1] + (bbox[3] - bbox[1]) / 2)
    return x, y


def recognize_request(server, device, weight, timeout=None):
    """yolo识别请求"""
    start = time.time()
    if not timeout:
        timeout = 5
    try:
        el_list = list()
        while True:
            pic_base64 = current_screen_base64()
            header = {
                'Content-Type': 'application/json'
            }
            body = {
                "image": pic_base64,
                "weights": weight,
                "device": device
            }
            res = requests.post(url=server, headers=header, json=body)
            if (res.status_code == 200) and (res.json()['results']):
                el_list = res.json()['results']
                print("访问YoloV5服务获取图像识别结果成功：{}".format(el_list))
                break
            if time.time() - start > timeout:
                print("访问YoloV5服务获取图像识别结果为空且超时！")
                break
        return el_list
    except Exception as e:
        print("访问YoloV5服务获取图像识别结果失败：{}".format(e))


def is_image_exists(el, el_list, confidence=0.7, el_index=0):
    """基于yolo服务判断图片是否存在"""
    coordinate_list = []
    for i in el_list:
        if i['name'] == el:
            if float(i['conf']) >= confidence:
                coordinate_list.append(get_bbox_center(i['bbox']))
    if coordinate_list:
        coordinate = coordinate_list[el_index]
        return coordinate



