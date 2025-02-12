import os,time
import subprocess
import pytest
from common.comdata import CommonData
from common.logger import Log
from common.send_email import HandleEmail
from common.utils.u_cmd import run_cmd
from common.utils.u_file import file_all_delete,file_copy
from common.utils.u_allure_reports import rename_allure_report_name

#测试
class AutoTestRunner:
    
    def __init__(self):
        self.run_config = CommonData.get_config_data()['项目运行设置']
    
    def run(self, all_flag=False):
        Log().sys_debug(CommonData.DRIVER_DIR)
        Log().logger.info(f"{'* '*20}【自动化测试开始】{'* '*20}")
        # print(CommonData.RUN_DATA)
        
        Log().logger.info(
            f"加载运行设置 ==> "
            f"自动化测试类型：{self.run_config['auto_type']}，"
            f"测试报告类型：{self.run_config['report_type']}，"
            f"项目测试地址：{self.run_config['test_url']}，"
            f"是否发送邮件：{self.run_config['is_email']}"
        )
        if self.run_config['report_type'] == 'allure':
            file_all_delete(CommonData.get_allure_result_path())
            # print('++++++++++++++++++++++++',self.run_cmd_by_allure(all_flag))
            pytest.main(self.run_cmd_by_allure(all_flag))
            
            file_copy(CommonData.get_project_allure_environment_file(),os.path.join(CommonData.get_allure_result_path(),'environment.xml'))
            Log().logger.info('正在生成报告')
            r = run_cmd(self.result_cmd_by_allure())
            Log().logger.info(r)
            try:
                time.sleep(1)
                
                rename_allure_report_name(CommonData.RUN_DATA['project_name'] + ' Report')
            except Exception as e:
                time.sleep(3)
                rename_allure_report_name(CommonData.RUN_DATA['project_name'] + ' Report')
            try:
                self.allure_copy_file()
            except Exception as e:
                Log().logger.error(e)   
            

            
        elif self.run_config['report_type'] == 'html':
            pytest.main(self.run_cmd_by_html(all_flag))
        elif self.run_config['report_type'] == 'xml':
            pytest.main(self.run_cmd_by_xml(all_flag))
        else:
            Log().logger.error(f"暂不支持此报告类型:{self.run_config['report_type']}")

        # 邮件发送
        if self.run_config['is_email'] == 'yes':
            el = HandleEmail()
            text = '本邮件由系统自动发出，无需回复！\n各位同事，大家好，以下为本次测试报告!'
            el.send_public_email(content=text, filetype=self.run_config['report_type'])
            print(f"邮件发送成功：{self.run_config['report_type']}")

        Log().logger.info(f"{'* '*20}【自动化测试结束】{'* '*20}")

    @staticmethod
    def exit(code):
        """退出执行"""
        if code == 0:
            pytest.exit("测试停止", code)
        elif code == 1:
            pytest.exit("测试失败", code)
        elif code == 2:
            pytest.exit("测试错误", code)
        else:
            raise Exception(f"没有此停止码：{code}")

    @staticmethod
    def run_cmd_by_allure(all_flag) -> list:
        return [
            '-sv',
            f'--alluredir={CommonData.get_allure_result_path()}',   # noqa
            *CommonData.get_testcases(all_flag)
        ]

    @staticmethod
    def allure_copy_file():
        # file_copy(CommonData.get_project_allure_environment_file(),os.path.join(CommonData.get_allure_result_path(),'environment.xml'))
        file_copy(os.path.join(CommonData.TEMPLATE_DIR,'allure'),os.path.join(CommonData.get_allure_report_path(),'allure')) 
        file_copy(os.path.join(CommonData.TEMPLATE_DIR,'allure_open_report.bat'),os.path.join(CommonData.get_allure_report_path(),'allure_open_report.bat')) 
        

    @staticmethod
    def result_cmd_by_allure() -> str:
        return f'allure generate {CommonData.get_allure_result_path()} ' \
               f'-o {CommonData.get_allure_report_path()} --clean'

    @staticmethod
    def run_cmd_by_html(all_flag) -> list:
        report_path = os.path.join(CommonData.get_html_path(), 'auto_reports.html')
        return [
            '-sv',
            f'--html={report_path}',
            '--self-contained-html',
            *CommonData.get_testcases(all_flag)
        ]

    @staticmethod
    def run_cmd_by_xml(all_flag) -> list:
        report_path = os.path.join(CommonData.get_xml_path(), 'auto_reports.xml')
        return [
            '-sv',
            f'--junitxml={report_path}',   # noqa
            *CommonData.get_testcases(all_flag)
        ]
