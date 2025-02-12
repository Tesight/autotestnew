import os
import pyperclip
import pyautogui
from common.container import LocalManager
from common.logger import Log
from common.comdata import CommonData
from common.utils.u_path import get_files_path_dict
from common.utils.u_yolov5 import recognize_request, is_image_exists


class ClientAction:
    """客户端操作基类"""

    @classmethod
    def mouse_click(cls, pos_x=None, pos_y=None, clicks=1, button='left'):
        """鼠标点击方法"""
        duration = float(CommonData.get_config_item('客户端自动化配置')['duration'])
        interval = float(CommonData.get_config_item('客户端自动化配置')['interval'])
        pyautogui.click(pos_x, pos_y, clicks=clicks, button=button, duration=duration, interval=interval)
        Log().logger.info(
            f'执行{cls.__name__}.mouse_click方法==>'
            f'鼠标在坐标{pos_x},{pos_y} 点击{button}键 {clicks}次'
        )

    @classmethod
    def rel_mouse_click(cls, rel_x=0, rel_y=0, clicks=1, button='left'):
        """相对坐标点击"""
        duration = float(CommonData.get_config_item('客户端自动化配置')['duration'])
        interval = float(CommonData.get_config_item('客户端自动化配置')['interval'])
        pyautogui.move(rel_x, rel_y)
        pyautogui.click(clicks=clicks, button=button, duration=duration, interval=interval)
        Log().logger.info(
            f'执行{cls.__name__}.rel_mouse_click方==>'
            f'鼠标在相对坐标{rel_x},{rel_y} 点击{button}键 {clicks}次'
        )

    @classmethod
    def moveto(cls, pos_x=0, pos_y=0, rel=False):
        """鼠标移动方法"""
        duration = float(CommonData.get_config_item('客户端自动化配置')['duration'])
        if rel:
            pyautogui.move(pos_x, pos_y, duration=duration)
            Log().logger.info(
                f'执行{cls.__name__}.moveto方法==>'
                f'鼠标偏移{pos_x},{pos_y}'
            )
        else:
            pyautogui.moveTo(pos_x, pos_y, duration=duration)
            Log().logger.info(
                f'执行{cls.__name__}.moveto方法==>'
                f'鼠标移动到{pos_x},{pos_y}'
            )

    @classmethod
    def dragto(cls, pos_x, pos_y, button='left', rel=False):
        """鼠标拖拽"""
        duration = float(CommonData.get_config_item('客户端自动化配置')['duration'])
        if rel:
            pyautogui.dragRel(pos_x, pos_y, duration=duration)
            Log().logger.info(
                f'执行{cls.__name__}.dragto方法==>'
                f'鼠标相对拖拽{pos_x},{pos_y}'
            )
        else:
            pyautogui.dragTo(pos_x, pos_y, duration=duration, button=button)
            Log().logger.info(
                f'执行{cls.__name__}.dragto方法==>'
                f'鼠标拖拽{pos_x},{pos_y}'
            )

    @classmethod
    def scroll(cls, amount_to_scroll, move_x=None, move_y=None):
        """鼠标滚动"""
        pyautogui.scroll(clicks=amount_to_scroll, x=move_x, y=move_y)
        Log().logger.info(
            f'执行{cls.__name__}.scroll方法==>'
            f'鼠标在{move_x},{move_y}位置滚动{amount_to_scroll}值'
        )

    @classmethod
    def keyboard_write(cls, content):
        """键盘输入"""
        interval = float(CommonData.get_config_item('客户端自动化配置')['interval'])
        pyautogui.typewrite(content, interval=interval)
        Log().logger.info(
            f'执行{cls.__name__}.keyboard_write方法==>'
            f'键盘输入：{content}'
        )

    @classmethod
    def input_string(cls, text, clear=False):
        """输入中文"""
        pyperclip.copy(text)
        if not clear:
            pyautogui.hotkey('ctrl', 'v')
        Log().logger.info(
            f'执行{cls.__name__}.input_string方法==>'
            f'输入文本：{text}'
        )

    @classmethod
    def press(cls, key):
        pyautogui.press(key)
        Log().logger.info(
            f"执行{cls.__name__}.press方法==>"
            f"键盘按下单个按键：{key}"
        )

    @classmethod
    def hotkey(cls, keys):
        pyautogui.hotkey(*keys)
        Log().logger.info(
            f"执行{cls.__name__}.hotkey方法==>"
            f"键盘执行组合键：{keys}"
        )


class TemplateClientAction(ClientAction):

    @classmethod
    @LocalManager.save_result
    def is_image_exists(cls, el, timeout=None, result="result"):
        """判断图片是否存在"""
        confidence = float(CommonData.get_config_item('客户端自动化配置')['confidence'])  # 设置图片识别信任度
        picture_dir = os.path.join(CommonData.get_testcase_path(), 'casedata', 'picture')  # noqa
        el_path = get_files_path_dict(picture_dir).get(el)
        if not el_path:
            raise FileNotFoundError('el:{} 不存在检查文件名或检查配置文件test_project！'.format(el))
        if not timeout:
            timeout = 5
        coordinates = pyautogui.locateOnScreen(el_path, minSearchTime=timeout, confidence=confidence, grayscale=True)
        if coordinates:
            coordinate = pyautogui.center(coordinates)
            Log().logger.info(
                f"执行{cls.__name__}.is_image_exists方法，返回值{result}==>"
                f"查找图片对象{el}在{coordinate}位置，存在!"
            )
            return coordinate
        Log().logger.info(
            f"执行{cls.__name__}.is_image_exists方法==>"
            f"查找图片对象{el}不存在"
        )

    @classmethod
    def click_picture(cls, el, clicks=1, button='left', is_click=True):
        """点击图片方法"""
        duration = float(CommonData.get_config_item('客户端自动化配置')['duration'])
        interval = float(CommonData.get_config_item('客户端自动化配置')['interval'])
        pos_x_y = cls.is_image_exists(el)
        if not pos_x_y:
            raise FileNotFoundError('el:{el} 不存在当前屏幕！')
        pyautogui.moveTo(*pos_x_y)
        if is_click:
            pyautogui.click(*pos_x_y, duration=duration, interval=interval, clicks=clicks, button=button)
        Log().logger.info(
            f'执行{cls.__name__}.click_picture方法==>'
            f'{el}图片模拟鼠标{button}键，点击{clicks}次，成功!'
        )

    @classmethod
    def rel_picture_click(cls, el, rel_x=0, rel_y=0, clicks=1, button='left', is_click=True):
        """图像的相对位置点击"""
        duration = float(CommonData.get_config_item('客户端自动化配置')['duration'])
        interval = float(CommonData.get_config_item('客户端自动化配置')['interval'])
        pos_x_y = cls.is_image_exists(el)
        if not pos_x_y:
            raise FileNotFoundError('el:{el} 不存在当前屏幕！')
        pyautogui.moveTo(*pos_x_y, duration=duration)  # 移动到 (100,100)
        pyautogui.move(rel_x, rel_y, duration=duration)  # 从当前位置右移100像素
        if is_click:
            pyautogui.click(clicks=clicks, button=button, duration=duration, interval=interval)
        Log().logger.info(
            f'执行{cls.__name__}.rel_picture_click方法==>'
            f'相对偏移{rel_x}，{rel_y}位置，{el}图片模拟鼠标{button}键，点击{clicks}次，成功!'
        )


class Yolov5ClientAction(ClientAction):  # noqa

    @classmethod
    @LocalManager.save_result
    def yolo_recognize_request(cls, weight, timeout=None, result="result"):
        """yolo识别请求"""
        ai_server = CommonData.get_config_item('客户端自动化配置')['ai_server']
        ai_device = CommonData.get_config_item('客户端自动化配置')['ai_device']
        el_list = recognize_request(ai_server, ai_device, weight, timeout)
        if el_list:
            Log().logger.info(
                f"执行{cls.__name__}.yolo_recognize_request方法，返回值{result}==>"
                f"获取yolo服务识别结果成功：{el_list}"
            )
            return el_list
        Log().logger.info(
            f"执行{cls.__name__}.yolo_recognize_request方法==>"
            f"未识别到所训练的图片！"
        )

    @classmethod
    @LocalManager.save_result
    def yolo_is_image_exists(cls, el, el_list, el_index=0, result="result"):
        """基于yolo服务判断图片是否存在"""
        confidence = float(CommonData.get_config_item('客户端自动化配置')['confidence'])  # 设置图片识别信任度
        coordinate = is_image_exists(el, el_list, confidence=confidence, el_index=el_index)
        if coordinate:
            Log().logger.info(
                f"执行{cls.__name__}.yolo_is_image_exists方法,返回值{result}==>"
                f"查找图片对象{el}在{coordinate}位置，存在！"
            )
            return coordinate
        Log().logger.info(
            f"执行{cls.__name__}.yolo_is_image_exists方法==>"
            f"查找图片对象{el}不存在"
        )

    @classmethod
    def yolo_click_picture(cls, el, el_list, clicks=1, button='left', is_click=True, el_index=0):
        """点击图片方法"""
        duration = float(CommonData.get_config_item('客户端自动化配置')['duration'])
        interval = float(CommonData.get_config_item('客户端自动化配置')['interval'])
        pos_x_y = cls.yolo_is_image_exists(el, el_list, int(el_index))
        if not pos_x_y:
            raise FileNotFoundError('el:{el} 不存在当前屏幕！')
        pyautogui.moveTo(*pos_x_y)
        if is_click:
            pyautogui.click(*pos_x_y, duration=duration, interval=interval, clicks=clicks, button=button)
        Log().logger.info(
            f'执行{cls.__name__}.yolo_click_picture方法==>'
            f'{el}图片模拟鼠标{button}键，点击{clicks}次，成功!'
        )

    @classmethod
    def yolo_rel_picture_click(cls, el, el_list, rel_x=0, rel_y=0, clicks=1, button='left', is_click=True, el_index=0):
        """图像的相对位置点击"""
        duration = float(CommonData.get_config_item('客户端自动化配置')['duration'])
        interval = float(CommonData.get_config_item('客户端自动化配置')['interval'])
        pos_x_y = cls.yolo_is_image_exists(el, el_list, el_index)
        if not pos_x_y:
            raise FileNotFoundError('el:{el} 不存在当前屏幕！')
        pyautogui.moveTo(*pos_x_y, duration=duration)  # 移动到 (100,100)
        pyautogui.move(rel_x, rel_y, duration=duration)  # 从当前位置右移100像素
        if is_click:
            pyautogui.click(clicks=clicks, button=button, duration=duration, interval=interval)
        Log().logger.info(
            f'执行{cls.__name__}.yolo_rel_picture_click方法==>'
            f'相对偏移{rel_x}，{rel_y}位置，{el}图片模拟鼠标{button}键，点击{clicks}次，成功!'
        )


if __name__ == '__main__':
    gui = Yolov5ClientAction()
    gui.hotkey(['win', 'm'])
