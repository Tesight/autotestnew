import os
import types
import pytest
import allure
from py.xml import html
from _pytest.python import Module
from common.logger import Log
from common.models import yaml_conftest_format, yaml_testcase_format
from common.comdata import CommonData
from common.container import LocalManager # noqa
from common.py_template import FIXTURE_TEMPLATE, TEST_FUNCTION_TEMPLATE
from common.utils.u_picture import get_capture_screenshot
from common.utils.u_yaml import read_yaml_file
from common.parser import YamlKwParser  # noqa
from common.keywords.web.driver import DriverManager

#
def pytest_collect_file(parent, path):
    """收集用例"""
    
    # print('parent:',parent)
    # print('path:',path)
    config = CommonData.get_config_data()['项目运行设置']
    # 初始化前置后置文件
    fixture_files = CommonData.get_fixture_path_list()
    for file_path in fixture_files:
        # 构造前置后置
        yaml_data = read_yaml_file(file_path)
        yaml_conftest_format(yaml_data, file_path)
        data = {
            "auto_type": config['auto_type'],
            "fixture_data": yaml_data,
        }
        content = FIXTURE_TEMPLATE.render(data)
        py_path = os.path.join(os.path.dirname(file_path), 'conftest.py')
        with open(py_path, 'w', encoding='utf-8') as f:
            f.write(content)
    if path.ext == ".yaml":
        if 'testcase' in path.strpath and 'conftest' not in path.strpath:   
            func_name = 'test_' + path.purebasename
            pytest_module = Module.from_parent(parent, fspath=path)
            # 动态创建 module
            module = types.ModuleType(path.purebasename)
            # 构造测试函数
            yaml_data = read_yaml_file(path.strpath)
            # print(yaml_data)
            yaml_testcase_format(yaml_data, path.strpath)
            data = {
                'func_name': func_name,
                'func_info': yaml_data['info'],
                'func_config': yaml_data['config'],
                'func_step': yaml_data['step']
            }
            function_str = TEST_FUNCTION_TEMPLATE.render(data)
            # print(function_str)
            exec(function_str)
            exec_function = eval(func_name)
            setattr(module, func_name, exec_function)
            pytest_module._getobj = lambda: module  # noqa
            return pytest_module


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item): # noqa
    """当测试失败的时候，自动截图，展示到html报告中"""
    outcome = yield
    pytest_html = item.config.pluginmanager.getplugin('html')
    report = outcome.get_result()
    extra = getattr(report, 'extra', [])
    config_data = CommonData.get_config_data()
    if report.when == 'call' or report.when == "setup":
        xfail = hasattr(report, 'wasxfail')  # noqa
        if (report.skipped and xfail) or (report.failed and not xfail):  # 失败截图
            file_name = report.nodeid.split("::")[-1] + ".png"
            file_path = os.path.join(CommonData.SCREENSHOT_DIR, file_name)
            if config_data['项目运行设置']['auto_type'] == 'web':
                screen_img = DriverManager.capture_screenshot_sel(file_path)
            elif config_data['项目运行设置']['auto_type'] == 'client':
                screen_img = get_capture_screenshot(file_path)
            else:
                screen_img = None
            if config_data['项目运行设置']['report_type'] == 'html' and screen_img:
                if file_name:
                    html_text = '<div><img src="{}" alt="screenshot" ' \
                                'style="width:600px;height:100%;" ' \
                                'onclick="lookimg(this.src)" align="right"/></div>'.format(screen_img)  # noqa
                    extra.append(pytest_html.extras.html(html_text))
            elif config_data['项目运行设置']['report_type'] == 'allure' and screen_img:
                allure.attach.file(file_path, "失败截图", allure.attachment_type.PNG)
    report.extra = extra
    report.description = str(item.function.__doc__)


def pytest_terminal_summary(terminalreporter, exitstatus, config):  # noqa
    """获取用例执行结果钩子函数"""
    total_case = terminalreporter._numcollected  # noqa
    pass_case = len([i for i in terminalreporter.stats.get('passed', [])])
    fail_case = len([i for i in terminalreporter.stats.get('failed', [])])
    error_case = len([i for i in terminalreporter.stats.get('error', [])])
    skip_case = len([i for i in terminalreporter.stats.get('skipped', [])])
    pass_rate = round(pass_case / total_case * 100, 2)
    CommonData.RUN_DATA['result'] = dict(
        总数=total_case, 成功=pass_case, 失败=fail_case, 错误=error_case, 跳过=skip_case, 成功率=pass_rate
    )
    desc = """
        本次执行情况如下：
        总用例数为：{}
        通过用例数：{}
        失败用例数：{}
        错误用例数：{}
        跳过用例数：{}
        通过率为： {} %
        """.format(total_case, pass_case, fail_case, error_case, skip_case, pass_rate)

    # TODO :此处可以调用微信、钉钉、短信相应方法推送消息
    # WeChat.sendMsg(desc)
    # DingDing.sendMsg(desc)
    # SMS.sendMsg(desc)
    Log().logger.info(desc)


def pytest_html_results_summary(prefix):
    prefix.extend([html.p("测试开发组: 工具人1号")])


def pytest_html_results_table_header(cells):
    cells.insert(1, html.th('Description'))
    cells.pop()


def pytest_html_results_table_row(report, cells):
    if hasattr(report, 'description'):
        cells.insert(1, html.td(report.description))
        cells.pop()
    else:
        print("html报告异常：", report.longreprtext)
