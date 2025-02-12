from common.container import LocalManager
from common.container import GlobalManager
from common.logger import Log
import allure


class VariableAction(object):

    @classmethod
    def set_Localvariable(cls, name, value):
        """设置变量"""
        LocalManager.set_value(name, value)
        allure.attach(
            body=f'设置变量: {name}={value}',
            name=f'设置变量',
            attachment_type=allure.attachment_type.TEXT     
        )
        if name == 'result':
            Log().logger.info(
                f'执行{cls.__name__}.set_variable方法==>'
                f'设置局部变量{name}的值为：{value}'
            )
    @classmethod
    def set_Globalvariable(cls, name, value):
        """设置变量"""
        GlobalManager.set_value(name, value)
        allure.attach(
            body=f'设置变量: {name}={value}',
            name=f'设置变量',
            attachment_type=allure.attachment_type.TEXT     
        )
        if name == 'result':
            Log().logger.info(
                f'执行{cls.__name__}.set_variable方法==>'
                f'设置局部变量{name}的值为：{value}'
            )
    @classmethod
    def print_variable(cls, name):
        """打印变量"""
        # LocalManager.set_value(name, value)
        value = LocalManager.get_value(name)
        allure.attach(
            body=f'读取变量: {name}={value}',
            name=f'读取变量',
            attachment_type=allure.attachment_type.TEXT     
        )
        if name == 'result':
            Log().logger.info(
                f'执行{cls.__name__}.print_variable方法==>'
                f'读取局部变量{name}的值为：{value}'
            )
