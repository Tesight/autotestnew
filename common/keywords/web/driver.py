import logging
import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.remote.remote_connection import LOGGER
from common.comdata import CommonData

# 禁用Selenium的调试信息
LOGGER.setLevel(logging.WARNING)


class DriverManager:
    _driver = None

    @classmethod
    def get_driver(cls):
        """获取浏览器对象driver"""
        if not cls._driver:
            web_config = CommonData.get_config_item('WEB自动化配置')
            if web_config['browser'] == "firefox":
                cls._driver = webdriver.Firefox(executable_path=os.path.join(CommonData.DRIVER_DIR, "gecokdriver.exe"))  # noqa
            elif web_config['browser'] == "chrome":
                cls._driver = webdriver.Chrome(executable_path=os.path.join(CommonData.DRIVER_DIR, "chromedriver.exe"))
            elif web_config['browser'] == "ie":
                cls._driver = webdriver.Ie(executable_path=os.path.join(CommonData.DRIVER_DIR, "IEDriverServer.exe"))
            elif web_config['browser'] == "edge":
                cls._driver = webdriver.Edge(executable_path=os.path.join(CommonData.DRIVER_DIR, "msedgedriver.exe"))  # noqa
            elif web_config['browser'] == "chromeheadless":  # noqa
                chrome_options = Options()
                chrome_options.add_argument('--headless')
                cls._driver = webdriver.Chrome(executable_path=os.path.join(CommonData.DRIVER_DIR, "chromedriver.exe"),
                                               chrome_options=chrome_options)
                cls._driver.set_window_size(width=1920, height=1080)
            else:
                raise Exception(f"不支持{web_config['browser']}浏览器！")
        return cls._driver

    @classmethod
    def quit_driver(cls):
        """关闭浏览器对象driver"""
        if cls._driver:
            cls._driver.quit()
            cls._driver = None

    @classmethod
    def capture_screenshot_sel(cls, file_path):
        """浏览器截图，返回base64格式"""
        try:
            driver = DriverManager.get_driver()
            driver.get_screenshot_as_file(file_path)
            return driver.get_screenshot_as_base64()
        except Exception as e:
            raise Exception('浏览器截图失败：{}'.format(e))
