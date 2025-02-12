import sys
import inspect
import pytest
import common.hooks as hooks
from common.comdata import CommonData
from common.container import LocalManager
from common.keywords.web.driver import DriverManager
from common.keywords.http.session import SessionManager


# 获取当前模块对象
obj_module = sys.modules[inspect.currentframe().f_globals['__name__']]
# 在当前模块对象中添加函数对象
setattr(obj_module, 'pytest_collect_file', hooks.pytest_collect_file)
setattr(obj_module, 'pytest_runtest_makereport', hooks.pytest_runtest_makereport)  # noqa
setattr(obj_module, 'pytest_terminal_summary', hooks.pytest_terminal_summary)
setattr(obj_module, 'pytest_html_results_summary', hooks.pytest_html_results_summary)
setattr(obj_module, 'pytest_html_results_table_header', hooks.pytest_html_results_table_header)
setattr(obj_module, 'pytest_html_results_table_row', hooks.pytest_html_results_table_row)


@pytest.fixture(autouse=True)#
def new_driver():
    LocalManager.init_local()
    run_config = CommonData.get_config_data()['项目运行设置']
    if run_config['auto_type'] == 'web':
        DriverManager.get_driver()
    elif run_config['auto_type'] == 'http':
        SessionManager.get_session()
    yield
    if run_config['auto_type'] == 'web':
        DriverManager.quit_driver()
    elif run_config['auto_type'] == 'http':
        SessionManager.close_session()
    LocalManager.clear()
