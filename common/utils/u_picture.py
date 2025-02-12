import base64
from io import BytesIO
from PIL import ImageGrab


def get_capture_screenshot(file_path=None):
    """屏幕截图，保存图片并返回base64格式"""
    try:
        buffer = BytesIO()
        img = ImageGrab.grab()
        if file_path:
            img.save(file_path)
        img.save(buffer, format='PNG')
        img.close()
        img_bytes = base64.b64encode(buffer.getvalue())
        buffer.close()
        img_base64 = 'Data:image/png;base64,%s' % img_bytes.decode()
        return img_base64
    except Exception as e:
        print("截取当前屏幕图片并转base64失败：{}".format(e))


def get_base64_image_string(image_path):
    """获取图片的base64字符串"""
    with open(image_path, "rb") as image_file:
        base64_string = base64.b64encode(image_file.read()).decode('utf-8')
    return base64_string
