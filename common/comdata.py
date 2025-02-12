import os
import sys
from typing import Callable
from common.utils.u_excel import ExcelRead
from common.utils.u_ini import read_ini_file

if hasattr(sys, 'frozen'):
    Path: Callable[[str], str] = lambda path: \
        os.path.abspath(os.path.join(os.path.dirname(sys.executable), path))
else:
    Path: Callable[[str], str] = lambda path: \
        os.path.abspath(os.path.join(os.path.dirname(__file__), path))


class CommonData(object):
    """公共路径类"""

    # 运行时构造项目数据
    RUN_DATA = {
        "project_name": "",  # Optional[str]
        "testcases": [],
        "result": {"总数": 0, "成功": 0, "失败": 0, "跳过": 0, "错误": 0, "通过率": 0}
    }

    PROJECT_ROOT = Path('../')  # 根目录
    DRIVER_DIR = os.path.join(PROJECT_ROOT, 'driver')
    TEST_SUIT_DIR = os.path.join(PROJECT_ROOT, 'testsuits')  # noqa
    IMAGES_ICON_DIR = os.path.join(PROJECT_ROOT, "static", "icon")
    SCREENSHOT_DIR = os.path.join(PROJECT_ROOT, "static", "screenshot")
    THEME_DIR = os.path.join(PROJECT_ROOT, "static", "theme")
    ERROR_PIC = os.path.join(SCREENSHOT_DIR, "error_pic.png")
    DB_DRIVER = os.path.join(PROJECT_ROOT, "driver", "dbdriver")  # noqa
    BASE_KEYWORD = os.path.join(PROJECT_ROOT, "action")
    TEMPLATE_DIR = os.path.join(PROJECT_ROOT, "static", "template")
    TEMPLATE_PROJECT = os.path.join(TEMPLATE_DIR, "project")
    TEMPLATE_CASE = os.path.join(TEMPLATE_DIR, "case.yaml")
    TEMPLATE_BUSINESS = os.path.join(TEMPLATE_DIR, "business.yaml")
    ICON_PICTURE = os.path.join(IMAGES_ICON_DIR, 'brick.png')
    FONT_PATH = os.path.join(PROJECT_ROOT, "static", "font","OPPOSans-R.ttf")
    LANGUAGE_DIR = os.path.join(PROJECT_ROOT, 'static',"language")   

    @classmethod
    def get_project_name(cls):
        """获取项目名称"""
        project_name = cls.RUN_DATA['project_name']
        if not project_name:
            raise KeyError('未指定项目，请指定要运行的项目名称！')
        return project_name

    @classmethod
    def get_testcases(cls, all_flag=False):
        """获取运行用例数据"""
        if (not cls.RUN_DATA['testcases']) and all_flag:
            return [cls.get_project_path()]
        else:
            return cls.RUN_DATA['testcases']

    @classmethod
    def get_project_path(cls):
        """获取项目路径"""
        project_path = os.path.join(cls.TEST_SUIT_DIR, cls.get_project_name())
        if not os.path.exists(project_path):
            raise KeyError('项目{}目录不存在！'.format(project_path))
        return project_path

    @classmethod
    def get_business_path(cls):
        """获取项目路径"""
        business_path = os.path.join(cls.get_project_path(), 'business')
        if not os.path.exists(business_path):
            raise KeyError('业务关键字{}目录不存在！'.format(business_path))
        return business_path

    @classmethod
    def get_testcase_path(cls):
        """获取项目路径"""
        testcase_path = os.path.join(cls.get_project_path(), 'testcase')
        if not os.path.exists(testcase_path):
            raise KeyError('测试用例{}目录不存在！'.format(testcase_path))
        return testcase_path

    @classmethod
    def get_log_path(cls):
        """获取项目路径"""
        log_path = os.path.join(cls.get_project_path(), 'log')
        if not os.path.exists(log_path):
            raise KeyError('日志{}目录不存在！'.format(log_path))
        return log_path

    @classmethod
    def get_allure_report_path(cls):
        """获取项目路径"""
        allure_report_path = os.path.join(cls.get_project_path(), 'report', 'allure', 'report')
        if not os.path.exists(allure_report_path):
            raise KeyError('报告{}目录不存在！'.format(allure_report_path))
        return allure_report_path
    
    @classmethod
    def get_allure_report_zip_path(cls):
        """获取项目路径"""
        allure_report_path = os.path.join(cls.get_project_path(), 'report', 'allure')
        if not os.path.exists(allure_report_path):
            raise KeyError('报告{}目录不存在！'.format(allure_report_path))
        return allure_report_path

    @classmethod
    def get_allure_result_path(cls):
        """获取项目路径"""
        allure_result_path = os.path.join(cls.get_project_path(), 'report', 'allure', 'result')
        if not os.path.exists(allure_result_path):
            raise KeyError('报告{}目录不存在！'.format(allure_result_path))
        return allure_result_path

    @classmethod
    def get_html_path(cls):
        """获取项目路径"""
        html_path = os.path.join(cls.get_project_path(), 'report', 'html')
        if not os.path.exists(html_path):
            raise KeyError('报告{}目录不存在！'.format(html_path))
        return html_path

    @classmethod
    def get_xml_path(cls):
        """获取项目路径"""
        xml_path = os.path.join(cls.get_project_path(), 'report', 'xml')
        if not os.path.exists(xml_path):
            raise KeyError('报告{}目录不存在！'.format(xml_path))
        return xml_path

    @classmethod
    def get_config_path(cls):
        """获取项目配置文件路径"""
        config_path = os.path.join(cls.get_project_path(), 'config', '配置文件.ini')
        if not os.path.exists(config_path):
            raise KeyError('配置{}文件不存在！'.format(config_path))
        return config_path

    @classmethod
    def get_config_data(cls):
        """获取配置文件信息"""
        return read_ini_file(cls.get_config_path())

    @classmethod
    def get_config_item(cls, item):
        item_config = cls.get_config_data().get(item)
        if not item_config:
            raise KeyError('配置项[{}]不存在！'.format(item))
        return item_config

    @classmethod
    def get_data_driver(cls, file_name, sheet_name):
        """获取数据驱动"""
        testcase_path = cls.get_testcase_path()
        file_path = os.path.join(testcase_path, 'casedata', 'datadriver', file_name)  # noqa
        if not os.path.exists(file_path):
            raise FileNotFoundError("文件路径不存在，请检查路径是否正确：%s" % file_path)
        excel = ExcelRead(file_path, sheet_name)
        return excel.dict_date()

    @classmethod
    def get_fixture_path_list(cls):
        """获取前置后置yaml文件路径"""
        conf_test = []
        for root, dirs, files in os.walk(cls.get_testcase_path(), topdown=True):
            for file_name in list(sorted([i for i in files if os.path.splitext(i)[1] == '.yaml'])):
                if file_name == 'conftest.yaml':
                    file_path = os.path.abspath(os.path.join(root, file_name))
                    conf_test.append(file_path)
        return conf_test

    @classmethod
    def get_project_data_path(cls):
        """获取工程数据文件夹"""
        test_data_path = os.path.join(CommonData.get_testcase_path(), 'casedata')
        return test_data_path

    @classmethod
    def get_project_allure_environment_file(cls):
        environment = os.path.join(cls.get_project_path(), 'config','environment.xml')
        if not os.path.exists(environment):
            raise KeyError('配置{}文件不存在！'.format(environment))
        return environment
    



if __name__ == '__main__':
    p = CommonData
    res = p.get_data_driver('登录数据驱动.xlsx', 'Sheet1')
    print(res)
