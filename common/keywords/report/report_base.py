import os
from common.comdata import CommonData
from common.utils.u_picture import get_capture_screenshot,get_base64_image_string
from common.logger import Log
from common.keywords.web.driver import DriverManager
import allure



class ReportAction(object):
    """报表工具类"""

    @classmethod
    def save_screenshot(cls,file_name):
        file_name = file_name+'.png'
        file_path = os.path.join(CommonData.get_project_data_path(),'picture',file_name)
        get_capture_screenshot(file_path)
        Log().logger.info(
            f'执行{cls.__name__}.save_screenshot方法'
        )

    @classmethod
    def add_screenshot(cls,file_name):
        file_name = file_name+'.png'
        file_path = os.path.join(CommonData.get_project_data_path(),'picture',file_name)  
        config_data = CommonData.get_config_data()  
        img = get_base64_image_string(file_path)  
        if config_data['项目运行设置']['report_type'] == 'html' and img:
            if file_name:
                html_text = '<div><img src="{}" alt="screenshot" ' \
                                'style="width:600px;height:100%;" ' \
                                'onclick="lookimg(this.src)" align="right"/></div>'.format(img)  # noqa
                # extra.append(pytest_html.extras.html(html_text))
        elif config_data['项目运行设置']['report_type'] == 'allure' and img:
            allure.attach.file(file_path, "截图", allure.attachment_type.PNG)

if __name__ == "__main__":
    pass
