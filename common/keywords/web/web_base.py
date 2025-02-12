from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.select import Select
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import TimeoutException
from common.container import LocalManager
from common.logger import Log
from common.keywords.web.driver import DriverManager


class WebAction(object):
    _timeout = 10
    _t = 0.5

    @classmethod
    def get_url(cls, url):
        """打开url，最大化窗口"""
        DriverManager.get_driver().get(url)
        DriverManager.get_driver().maximize_window()
        Log().logger.info(
            f"执行{cls.__name__}.get_url方法成功==>"
            f"浏览器访问请求地址成功：{url}"
        )

    @classmethod
    def find_element(cls, element_type, element_info, timeout=_timeout):
        """定位到元素，返回元素对象，没定位到，Timeout异常"""
        try:
            ele = WebDriverWait(DriverManager.get_driver(),
                                timeout, cls._t).until(ec.presence_of_element_located((element_type, element_info)))
            Log().logger.debug(f"元素定位成功：定位方式{element_type};定位信息{element_info}")
            return ele
        except TimeoutException as e:
            Log().logger.error(f'元素定位失败：定位方式{element_type};定位信息{element_info}\n{e}')
            raise e

    @classmethod
    def find_elements(cls, element_type, element_info, timeout=_timeout):
        try:
            ele = WebDriverWait(DriverManager.get_driver(), timeout,
                                cls._t).until(ec.presence_of_all_elements_located((element_type, element_info)))
            Log().logger.debug("元素定位成功：定位方式{};定位信息{}")
            return ele
        except TimeoutException as e:
            Log().logger.error('元素定位失败：定位方式{};定位信息{}\n{}', element_type, element_info, e)
            raise e

    @classmethod
    def input(cls, element_type, element_info, text=''):
        try:
            ele = cls.find_element(element_type, element_info)
            ele.send_keys(text)
            Log().logger.info(
                f'执行{cls.__name__}.input方法成功==>'
                f'元素：定位方式{element_type};定位信息{element_info}，执行输入成功：{text}'
            )
        except Exception as e:
            Log().logger.error(
                f'执行{cls.__name__}.input方法失败==>'
                f'元素：定位方式{element_type};定位信息{element_info}，执行输入失败：{text}\n{e}'
            )
            raise e

    @classmethod
    def click(cls, element_type, element_info):
        try:
            ele = WebDriverWait(DriverManager.get_driver(),
                                cls._timeout, cls._t).until(ec.element_to_be_clickable((element_type, element_info)))
            ele.click()
            Log().logger.info(
                f'执行{cls.__name__}.click方法成功==>'
                f'元素：定位方式{element_type};定位信息{element_info}，执行点击成功'
            )
        except Exception as e:
            Log().logger.error(
                f'执行{cls.__name__}.click方法失败==>'
                f'元素：定位方式{element_type};定位信息{element_info}，执行点击失败\n{e}'
            )
            raise e

    @classmethod
    def clear(cls, element_type, element_info):
        try:
            ele = cls.find_element(element_type, element_info)
            ele.clear()
            Log().logger.info(
                f'执行{cls.__name__}.clear方法成功==>'
                f'元素：定位方式{element_type};定位信息{element_info}，执行清空成功'
            )
        except Exception as e:
            Log().logger.error(
                f'执行{cls.__name__}.clear方法失败==>'
                f'元素：定位方式{element_type};定位信息{element_info}，执行点击失败\n{e}'
            )
            raise e

    @classmethod
    def mouse_move_to(cls, element_type, element_info):
        """鼠标悬停"""
        try:
            element = cls.find_element(element_type, element_info)
            ActionChains(DriverManager.get_driver()).move_to_element(element).perform()
            Log().logger.info(
                f'执行{cls.__name__}.mouse_move_to方法成功==>'
                f'元素：定位方式{element_type};定位信息{element_info}，执行悬停操作成功'
            )
        except Exception as e:
            Log().logger.error(
                f'执行{cls.__name__}.mouse_move_to方法失败==>'
                f'元素：定位方式{element_type};定位信息{element_info}，执行悬停操作失败\n{e}'
            )
            raise e

    @classmethod
    def mouse_drag_to(cls, element_type, element_info, x_offset, y_offset):
        """鼠标拖拽到某一坐标"""
        try:
            element = cls.find_element(element_type, element_info)
            ActionChains(DriverManager.get_driver()).drag_and_drop_by_offset(element, x_offset, y_offset)
            Log().logger.info(
                f'执行{cls.__name__}.mouse_drag_to方法成功==>'
                f'元素：定位方式{element_type};定位信息{element_info}，拖拽到坐标{x_offset};{y_offset}成功'
            )
        except Exception as e:
            Log().logger.error(
                f'执行{cls.__name__}.mouse_drag_to方法失败==>'
                f'元素：定位方式{element_type};定位信息{element_info}，拖拽到坐标{x_offset};{y_offset}失败\n{e}'
            )
            raise e

    @classmethod
    def js_focus_element(cls, element_type, element_info):
        """聚焦元素"""
        try:
            target = cls.find_element(element_type, element_info)
            DriverManager.get_driver().execute_script("arguments[0].scrollIntoView();", target)
            Log().logger.info(
                f'执行{cls.__name__}.js_focus_element方法成功==>'
                f'元素：定位方式{element_type};定位信息{element_info}，滑轮聚焦到元素成功'
            )
        except Exception as e:
            Log().logger.error(
                f'执行{cls.__name__}.js_focus_element方法失败==>'
                f'元素：定位方式{element_type};定位信息{element_info}，滑轮聚焦到元素失败\n{e}'
            )
            raise e

    @classmethod
    def js_scroll_top(cls):
        """滚动到顶部"""
        try:
            js = "window.scrollTo(0,0)"
            DriverManager.get_driver().execute_script(js)
            Log().logger.info(
                f'执行{cls.__name__}.js_scroll_top方法成功==>'
                f'鼠标滑轮滚动到顶部成功'
            )
        except Exception as e:
            Log().logger.error(
                f'执行{cls.__name__}.js_scroll_top方法失败==>'
                f'鼠标滑轮滚动到顶部失败\n{e}'
            )
            raise e

    @classmethod
    def js_scroll_end(cls, x=0):
        """滚动到底部"""
        try:
            js = "window.scrollTo(%s,document.body.scrollHeight)" % x
            DriverManager.get_driver().execute_script(js)
            Log().logger.info(
                f'执行{cls.__name__}.js_scroll_end方法成功==>'
                f'鼠标滑轮滚动到底部成功'
            )
        except Exception as e:
            Log().logger.error(
                f'执行{cls.__name__}.js_scroll_end方法失败==>'
                f'鼠标滑轮滚动到底部失败\n{e}'
            )
            raise e

    @classmethod
    def keyboard_send_keys_to(cls, element_type, element_info, text):
        """模拟键盘输入"""
        try:
            element = cls.find_element(element_type, element_info)
            ActionChains(DriverManager.get_driver()).send_keys_to_element(element, text).perform()
            Log().logger.info(
                f'执行{cls.__name__}.keyboard_send_keys_to方法成功==>'
                f'元素：定位方式{element_type};定位信息{element_info}，执行键盘输入成功:{text}'
            )
        except Exception as e:
            Log().logger.error(
                f'执行{cls.__name__}.keyboard_send_keys_to方法失败==>'
                f'元素：定位方式{element_type};定位信息{element_info}，执行键盘输入失败:{text}\n{e}'
            )
            raise e

    @classmethod
    @LocalManager.save_result
    def get_alert_text(cls, result='result'):
        """获取弹窗文本"""
        try:
            confirm = DriverManager.get_driver().switch_to.alert
            Log().logger.info(
                f'执行{cls.__name__}.get_alert_text方法成功，返回值{result}==>'
                f'获取弹窗文本信息：{confirm.text}'
            )
            return confirm.text
        except Exception as e:
            Log().logger.error(
                f'执行{cls.__name__}.get_alert_text方法失败，返回值{result}==>'
                f'获取弹窗文本信息失败\n{e}'
            )
            return None

    @classmethod
    def alert_accept(cls):
        """弹窗点击接受"""
        try:
            confirm = DriverManager.get_driver().switch_to.alert
            confirm.accept()
            Log().logger.info(
                f'执行{cls.__name__}.alert_accept方法成功==>'
                f'弹窗点击接收成功'
            )
        except Exception as e:
            Log().logger.error(
                f'执行{cls.__name__}.alert_accept方法失败==>'
                f'弹窗点击接收失败\n{e}'
            )
            raise e

    @classmethod
    def alert_dismiss(cls):
        """弹窗点击取消"""
        try:
            confirm = DriverManager.get_driver().switch_to.alert
            confirm.dismiss()
            Log().logger.info(
                f'执行{cls.__name__}.alert_dismiss方法成功==>'
                f'弹窗点击取消成功'
            )
        except Exception as e:
            Log().logger.error(
                f'执行{cls.__name__}.alert_dismiss方法失败==>'
                f'弹窗点击取消失败\n{e}'
            )
            raise e

    @classmethod
    def input_alert(cls, text):
        """弹窗输入"""
        try:
            prompt = DriverManager.get_driver().switch_to.alert
            prompt.send_keys(text)
            Log().logger.info(
                f'执行{cls.__name__}.input_alert方法成功==>'
                f'弹窗输入文本值：{text}'
            )
        except Exception as e:
            Log().logger.error(
                f'执行{cls.__name__}.input_alert方法失败==>'
                f'弹窗输入文本值失败：{text}\n{e}'
            )
            raise e

    @classmethod
    def select_by_index(cls, element_type, element_info, index=0):
        """通过索引,index是索引第几个，从0开始，默认选第一个"""
        try:
            element = cls.find_element(element_type, element_info)  # 定位select这一栏
            Select(element).select_by_index(index)
            Log().logger.info(
                f'执行{cls.__name__}.select_by_index方法成功==>'
                f'元素：定位方式{element_type};定位信息{element_info}，按索引选择下拉项{index}成功'
            )
        except Exception as e:
            Log().logger.error(
                f'执行{cls.__name__}.select_by_index方法失败==>'
                f'元素：定位方式{element_type};定位信息{element_info}，按索引选择下拉项{index}失败\n{e}'
            )
            raise e

    @classmethod
    def select_by_value(cls, element_type, element_info, value):
        """通过value属性"""
        try:
            element = cls.find_element(element_type, element_info)
            Select(element).select_by_value(value)
            Log().logger.info(
                f'执行{cls.__name__}.select_by_value方法成功==>'
                f'元素：定位方式{element_type};定位信息{element_info}，按值{value}选择下拉项成功'
            )
        except Exception as e:
            Log().logger.error(
                f'执行{cls.__name__}.select_by_value方法失败==>'
                f'元素：定位方式{element_type};定位信息{element_info}，按值{value}选择下拉项失败\n{e}'
            )
            raise e

    @classmethod
    def select_by_text(cls, element_type, element_info, text):
        """通过文本值定位"""
        try:
            element = cls.find_element(element_type, element_info)
            Select(element).select_by_visible_text(text)
            Log().logger.info(
                f'执行{cls.__name__}.select_by_text方法成功==>'
                f'元素：定位方式{element_type};定位信息{element_info}，按文本{text}选择下拉项成功'
            )
        except Exception as e:
            Log().logger.error(
                f'执行{cls.__name__}.select_by_text方法失败==>'
                f'元素：定位方式{element_type};定位信息{element_info}，按文本{text}选择下拉项失败\n{e}'
            )
            raise e

    @classmethod
    def switch_iframe(cls, id_index_locator):
        """切换iframe"""
        try:
            if isinstance(id_index_locator, int):
                DriverManager.get_driver().switch_to.frame(id_index_locator)
            elif isinstance(id_index_locator, str):
                DriverManager.get_driver().switch_to.frame(id_index_locator)
            elif isinstance(id_index_locator, tuple) or isinstance(id_index_locator, list):
                ele = cls.find_element(*id_index_locator)
                DriverManager.get_driver().switch_to.frame(ele)
            Log().logger.info(
                f"执行{cls.__name__}.switch_iframe方法成功==>"
                f"iframe切换成功：{id_index_locator}"
            )
        except Exception as e:
            Log().logger.error(
                f'执行{cls.__name__}.switch_iframe方法失败==>'
                f'iframe切换成功失败：{id_index_locator}\n{e}'
            )
            raise e

    @classmethod
    def switch_iframe_out(cls):
        """切换iframe"""
        try:
            DriverManager.get_driver().switch_to.default_content()
            Log().logger.info(
                f'执行{cls.__name__}.switch_iframe_out方法成功==>'
                f'iframe切换到最外层成功'
            )
        except Exception as e:
            Log().logger.error(
                f'执行{cls.__name__}.switch_iframe_out方法失败==>'
                f'iframe切换到最外层失败\n{e}'
            )
            raise e

    @classmethod
    def switch_iframe_up(cls):
        """切换iframe"""
        try:
            DriverManager.get_driver().switch_to.parent_frame()
            Log().logger.info(
                f'执行{cls.__name__}.switch_iframe_up方法成功==>'
                f'iframe切换到上一层成功'
            )
        except Exception as e:
            Log().logger.error(
                f'执行{cls.__name__}.switch_iframe_up方法失败==>'
                f'iframe切换到上一层失败\n{e}'
            )
            raise e

    @classmethod
    @LocalManager.save_result
    def get_handles(cls, result='result'):
        """获取当前所有窗口"""
        try:
            handles = DriverManager.get_driver().window_handles
            Log().logger.info(
                f'执行{cls.__name__}.get_handles方法成功，返回值{result}==>'
                f'获取所有的handle：{handles}'
            )
            return handles
        except Exception as e:
            Log().logger.error(
                f'执行{cls.__name__}.get_handles方法失败，返回值{result}==>获取所有的handle失败\n{e}'
            )
            raise e

    @classmethod
    def switch_handle(cls, index=-1):  # 第几个，-1是最后一个
        """切换窗口"""
        try:
            handle_list = DriverManager.get_driver().window_handles
            DriverManager.get_driver().switch_to.window(handle_list[index])
            Log().logger.info(
                f'执行{cls.__name__}.switch_handle方法成功==>'
                f'切换handle成功：{index}'
            )
        except Exception as e:
            Log().logger.error(
                f'执行{cls.__name__}.switch_handle方法失败==>'
                f'切换handle失败：{index}\n{e}'
            )
            raise e

    @classmethod
    @LocalManager.save_result
    def get_title(cls, result='result'):
        """获取title"""
        try:
            title = DriverManager.get_driver().title
            Log().logger.info(
                f'执行{cls.__name__}.get_title方法成功，返回值{result}==>'
                f'获取title成功：{title}'
            )
            return title
        except Exception as e:
            Log().logger.error(
                f'执行{cls.__name__}.get_title方法失败，返回值{result}==>'
                f'获取title失败\n{e}'
            )
            return None

    @classmethod
    @LocalManager.save_result
    def get_text(cls, element_type, element_info, result='result'):
        """获取文本"""
        try:
            content = cls.find_element(element_type, element_info).text
            Log().logger.info(
                f'执行{cls.__name__}.get_text方法成功，返回值{result}==>'
                f'元素：定位方式{element_type};定位信息{element_info}，获取文本成功：{content}'
            )
            return content
        except Exception as e:
            Log().logger.error(
                f'执行{cls.__name__}.get_text方法失败，返回值{result}==>'
                f'元素：定位方式{element_type};定位信息{element_info}，获取文本失败\n{e}'
            )
            return None

    @classmethod
    @LocalManager.save_result
    def get_attribute(cls, element_type, element_info, name, result='result'):
        """获取属性"""
        try:
            element = cls.find_element(element_type, element_info)
            attr = element.get_attribute(name)
            Log().logger.info(
                f'执行{cls.__name__}.get_attribute方法成功，返回值{result}==>'
                f'元素：定位方式{element_type};定位信息{element_info}，获取属性成功：{attr}'
            )
            return attr
        except Exception as e:
            Log().logger.error(
                f'执行{cls.__name__}.get_attribute方法失败，返回值{result}==>'
                f'元素：定位方式{element_type};定位信息{element_info}，获取属性失败\n{e}'
            )
            return None

    @classmethod
    @LocalManager.save_result
    def is_title(cls, title='', result='result'):
        """判断当前页面的title是否完全等于预期字符串,返回bool值"""
        try:
            bool_result = WebDriverWait(DriverManager.get_driver(), cls._timeout, cls._t).until(ec.title_is(title))
            Log().logger.info(
                f'执行{cls.__name__}.is_title方法成功，返回值{result}==>'
                f'判断当前页面的title是否完全等于"{title}",返回bool值：{bool_result}'
            )
            return bool_result
        except Exception as e:
            Log().logger.error(
                f'执行{cls.__name__}.is_title方法失败，返回值{result}==>'
                f'判断当前页面的title是否完全等于"{title}"失败,返回bool值\n{e}'
            )
            return False

    @classmethod
    @LocalManager.save_result
    def is_title_contains(cls, title='', result='result'):
        """判断当前页面的title是否包含预期字符串，返回布尔值"""
        try:
            bool_result = WebDriverWait(DriverManager.get_driver(), cls._timeout, cls._t).until(ec.title_contains(title))
            Log().logger.info(
                f'执行{cls.__name__}.is_title_contains方法成功，返回值{result}==>'
                f'判断当前页面的title是否包含"{title}",返回bool值：{bool_result}'
            )
            return bool_result
        except Exception as e:
            Log().logger.error(
                f'执行{cls.__name__}.is_title_contains方法失败，返回值{result}==>'
                f'判断当前页面的title是否包含"{title}"失败,返回bool值\n{e}'
            )
            return False

    @classmethod
    @LocalManager.save_result
    def is_text_in_element(cls, element_type, element_info, text='', result='result'):
        """判断某个元素中的text是否包含了预期的字符串,返回bool值"""
        try:
            bool_result = WebDriverWait(DriverManager.get_driver(),
                                        cls._timeout, cls._t).until(
                ec.text_to_be_present_in_element((element_type, element_info), text))
            Log().logger.info(
                f'执行{cls.__name__}.is_text_in_element方法成功，返回值{result}==>'
                f'元素：定位方式{element_type};定位信息{element_info}，判断元素中的text是否包含了"{text}",返回bool值：{bool_result}'
            )
            return bool_result
        except Exception as e:
            Log().logger.error(
                f'执行{cls.__name__}.is_text_in_element方法失败，返回值{result}==>'
                f'元素：定位方式{element_type};定位信息{element_info}，判断元素中的text是否包含了"{text}"失败,返回bool值\n{e}'
            )
            return False

    @classmethod
    @LocalManager.save_result
    def is_value_in_element(cls, element_type, element_info, value='', result='result'):
        """判断某个元素中的value属性是否包含了预期的字符串,返回bool值"""
        try:
            bool_result = WebDriverWait(DriverManager.get_driver(),
                                        cls._timeout, cls._t).until(
                ec.text_to_be_present_in_element_value((element_type, element_info), value))
            Log().logger.info(
                f'执行{cls.__name__}.is_value_in_element方法成功，返回值{result}==>'
                f'元素：定位方式{element_type};定位信息{element_info}，判断元素中的value属性是否包含了"{value}",返回bool值：{bool_result}')
            return bool_result
        except Exception as e:  # noqa
            Log().logger.error(
                f'执行{cls.__name__}.is_value_in_element方法失败，返回值{result}==>'
                f'元素：定位方式{element_type};定位信息{element_info}，判断元素中的value属性是否包含了"{value}"失败,返回bool值\n{e}')
            return False

    @classmethod
    @LocalManager.save_result
    def is_alert(cls, timeout=3, result='result'):
        """判断页面上是否存在alert弹窗,返回bool值"""
        try:
            bool_result = WebDriverWait(DriverManager.get_driver(), timeout, cls._t).until(ec.alert_is_present())
            Log().logger.info(
                f'执行{cls.__name__}.is_alert方法成功，返回值{result}==>'
                f'判断页面上是否存在alert弹窗,返回bool值：{bool_result}'
            )
            return bool_result
        except Exception as e:
            Log().logger.error(
                f'执行{cls.__name__}.is_alert方法成功，返回值{result}==>'
                f'判断页面上是否存在alert弹窗失败,返回bool值：False\n{e}'
            )
            return False

    @classmethod
    @LocalManager.save_result
    def is_element_exist(cls, element_type, element_info, timeout, result='result'):
        try:
            element = (element_type, element_info)
            WebDriverWait(DriverManager.get_driver(), timeout).until(ec.presence_of_element_located(element))
            Log().logger.debug(
                f'执行{cls.__name__}.is_element_exist方法成功，返回值{result}==>'
                f'元素：定位方式{element_type};定位信息{element_info}，元素存在返回bool值：True'
            )
            return True
        except Exception as e:
            Log().logger.debug(
                f'执行{cls.__name__}.is_element_exist方法失败，返回值{result}==>'
                f'元素：定位方式{element_type};定位信息{element_info}，元素不存在返回bool值：False\n{e}'
            )
            return False

    @classmethod
    @LocalManager.save_result
    def is_element_displayed(cls, element_type, element_info, result='result'):
        """判断元素是否显示，返回bool值"""
        try:
            ele = cls.find_element(element_type, element_info)
            res = ele.is_displayed()
            Log().logger.debug(
                f'执行{cls.__name__}.is_element_displayed方法成功，返回值{result}==>'
                f'元素：定位方式{element_type};定位信息{element_info}，元素显示返回bool值：{res}'
            )
            return res
        except Exception as e:
            Log().logger.debug(
                f'执行{cls.__name__}.is_element_displayed方法失败，返回值{result}==>'
                f'元素：定位方式{element_type};定位信息{element_info}，元素未显示返回bool值：False\n{e}'
            )
            return False
