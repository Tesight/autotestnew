import os
import re
import sys
import allure
from common.container import LocalManager
from common.logger import Log
from common.utils.u_json import set_json_value
from common.utils.u_obj import get_function_by_name
from common.utils.u_yaml import read_yaml_file
from common.comdata import CommonData
from common.register import INIT_ACTION_MAPS

#解析action
class YamlKwParser(object):

    @classmethod
    def parse(cls, step_list: list):
        """步骤转换器，解析全部用例步骤并执行函数
        :param step_list: 所有的行为步骤列表
        """
        if not step_list:
            return
        for step in step_list:
            if 'action' in step.keys():
                cls._action_step_parse(step)
            elif 'function' in step.keys():
                cls._function_step_parse(step)
            elif 'business' in step.keys():
                cls._business_step_parse(step)

    @classmethod
    def _action_step_parse(cls, step: dict):
        """解析yaml用例中action步骤

        :param step: 关键字步骤action
        :return: 关键字执行结果
        """
        if step["action"] in INIT_ACTION_MAPS.keys():
            method_name = step["method"]
            instance = INIT_ACTION_MAPS[step["action"]]
            with allure.step("action步骤:{}".format(step['desc'])):
                if hasattr(instance, method_name):
                    Log().logger.info(f"{'- '*20}基础关键字[{step['desc']}],开始执行！{'- ' * 20}")
                    params = dict()
                    if step.get('params'):
                        params = cls.replace_variables(step.get('params'), LocalManager.local_dict)
                    getattr(instance, method_name)(**params)
                    Log().logger.debug(f'执行action步骤解析==>函数{method_name}执行成功,参数：{params}')
                    # allure.attach(f'函数{method_name}执行成功,参数：{params}')
                else:
                    Log().logger.error(f'执行action步骤解析==>基础关键字{method_name}未找到或未实现！')
                    # allure.attach(f'执行action步骤解析==>基础关键字{method_name}未找到或未实现！')
                    raise AssertionError("基础关键字未找到或未实现：{}".format(method_name))
        else:
            Log().logger.error(f'基础关键字类{step["action"]}未找到或未实现！')
            raise AssertionError(f'基础关键字类{step["action"]}未找到或未实现！')

    @classmethod
    def _function_step_parse(cls, step: dict):
        """解析yaml用例中function步骤
        :param step: 关键字步骤function
        """
        if step.get('function') == 'python':
            with allure.step(f"function步骤:{step['desc']}"):
                sys.path.append(CommonData.DRIVER_DIR)
                lib_path = os.path.join(CommonData.get_testcase_path(), 'casedata', 'lib')  # noqa
                func_obj = get_function_by_name(lib_path, step['params']['py_name'], step['params']['func_name'])
                if not func_obj:
                    Log().logger.error(f"自定义关键字未找到或未实现：{step['params']['func_name']}")
                    raise AssertionError(f"自定义关键字未找到或未实现：{step['params']['func_name']}")
                Log().logger.info(f"{'- ' * 20}自定义关键字[{step['desc']}],开始执行！{'- ' * 20}")
                params = dict()
                if step['params'].get('kwargs'):
                    params = cls.replace_variables(step['params'].get('kwargs'), LocalManager.local_dict)
                    # print(params)
                    # params = eval(params)
                    # print(LocalManager.local_dict)
                res = func_obj(**params)
                LocalManager.set_value(step['params']['result'], res)
                allure.attach(f"函数{step['params']['func_name']}执行成功,参数：{params},返回值：{res}",
                              name=f"函数{step['params']['func_name']}")   
                Log().logger.debug(f"自定义函数{step['params']['func_name']}执行成功,参数：{params}")
        else:
            Log().logger.error(f"方法未找到或未实现：{step['function']}")
            raise AssertionError(f"方法未找到或未实现：{step['function']}")

    @classmethod
    def _business_step_parse(cls, step: dict):
        """解析yaml用例中business步骤
        :param step: 业务关键字步骤
        """
        path = os.path.join(CommonData.get_business_path(), step['business'])
        if os.path.exists(path):
            business_data = read_yaml_file(path)
            if step.get('params'):
                kwargs = step['params']
                for extract_data in kwargs.values():
                    set_json_value(business_data['step'], extract_data['path'], extract_data['value'])
            for child_step in business_data['step']:
                if child_step.get('action'):
                    cls._action_step_parse(child_step)
                elif child_step.get('function'):
                    cls._function_step_parse(child_step)
        else:
            Log().logger.error(f"业务关键字{step['business']}不存在!")
            raise AssertionError(f"业务关键字{step['business']}不存在!")

    @classmethod
    def replace_variable_data(cls, data, global_dict):
        """动态变量替换"""
        pattern_variable = r'\${(.*?)}'
        if type(data) != str:
            data = str(data)
        var_names = re.findall(pattern_variable, data)
        if var_names:
            for var_name in var_names:
                if var_name in global_dict:
                    var_value = global_dict.get(var_name)
                    if isinstance(global_dict[var_name], str):
                        data = data.replace(f"${{{var_name}}}", var_value)
                    else:
                        data = global_dict[var_name]

                    if var_name not in ["result_text", "result_content"]:
                        Log().logger.info(f"动态变量{var_name}替换成功,替换后的值==>{str(var_value)}")
        if type(data) == str:
                try:
                    if data.isdigit():
                        data = eval(data)    
                    elif data.startswith('[') and data.endswith(']'):
                        data = eval(data)
                    elif data.startswith('{') and data.endswith('}'):
                        data = eval(data)   
                except NameError:
                    pass
        return data

    @classmethod
    def replace_driven_data(cls, data, global_dict):
        """数据驱动变量替换"""
        pattern_driven = r'DataDriver\.(\w+)'
        var_names = re.findall(pattern_driven, data)
        if var_names:
            for var_name in var_names:
                var_value = global_dict.get("DataDriver")[var_name]
                data = data.replace(f"DataDriver.{var_name}", str(var_value))
                if type(data) == str:
                        try:
                            if data.isdigit():
                                data = eval(data)    
                            elif data.startswith('[') and data.endswith(']'):
                                data = eval(data)
                            elif data.startswith('{') and data.endswith('}'):
                                data = eval(data)   
                        except NameError:
                            pass

                Log().logger.info(f"数据驱动变量[DataDriver.{var_name}]替换成功,替换后的值==>{str(var_value)}")
        return data

    @classmethod
    def replace_variables(cls, yaml_data, global_dict):
        """动态变量替换"""
        if isinstance(yaml_data, str):
            yaml_data = cls.replace_driven_data(yaml_data, global_dict)
            yaml_data = cls.replace_variable_data(yaml_data, global_dict)
        elif isinstance(yaml_data, dict):
            for key, value in yaml_data.items():
                yaml_data[key] = cls.replace_variables(value, global_dict)
        elif isinstance(yaml_data, list):
            for i in range(len(yaml_data)):
                yaml_data[i] = cls.replace_variables(yaml_data[i], global_dict)
        return yaml_data


if __name__ == '__main__':
    pass
