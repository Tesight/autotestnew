import yaml
import requests

import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from common.register import INIT_ACTION_MAPS
from common.comdata import CommonData
from common.container import GlobalManager
from common.container import LocalManager
from common.logger import Log

CommonData.RUN_DATA = {
        "project_name": "new",  # Optional[str]
    }

VariableAction = INIT_ACTION_MAPS.get("VariableAction")
HttpAction= INIT_ACTION_MAPS.get("HttpAction")

# 确保 VariableAction 和 HttpAction 类存在
if not VariableAction or not HttpAction:
    raise ImportError("VariableAction or HttpAction class not found in INIT_ACTION_MAPS")

def execute_yaml_steps(yaml_data):
    for step in yaml_data['step']:
        action = step['action']
        method = step['method']
        params = step['params']
        
        if action == 'VariableAction' and method == 'set_variable':
            VariableAction.set_Globalvariable(params['name'], params['value'])
            print(params['name'], params['value'])
        elif action == 'HttpAction' and method == 'request':
            url = params['url']
            method = params['method']
            headers = params.get('headers')
            data = params.get('data')
            json_data = GlobalManager.get_value(params['json'])
            result_json = params['result_json']
            response = HttpAction.request(method, url, headers=headers, data=data, json=json_data, result_json=result_json)
 
            
           # 尝试输出JSON格式的响应
            try:
                json_data = response.json()
                print(f"JSON响应: {json_data}")
                GlobalManager.set_value(result_json, json_data)
            except requests.exceptions.JSONDecodeError:
                # 如果不是JSON，输出文本内容
                print(f"文本响应: {response.text}")
                GlobalManager.set_value(result_json, {"error": True, "text": response.text})
            
            # 如果需要查看原始二进制内容
            # print(f"二进制内容前100字节: {response.content[:100]}")
            
            return response
        else:
            pass
        # elif action == 'JsonAction' and method == 'get_json_value':
        #     json_data = GlobalManager.get_value(params['json_data'])
        #     json_path = params['json_path']
        #     result = params['result']
        #     value = json_data.get(json_path)
        #     VariableAction.set_variable(result, value)
        # elif action == 'CheckAction' and method == 'equal':
        #     real_value = GlobalManager.get_value(params['real_value'])
        #     expect_value = params['expect_value']
        #     assert real_value == expect_value, f"Expected {expect_value}, but got {real_value}"

if __name__ == "__main__":
    # with open('C:/baidunetdiskdownload/mysence/testsuits/new/skydel基础设置.yaml', 'r', encoding='utf-8') as file:
    #     yaml_data = yaml.safe_load(file)
    # execute_yaml_steps(yaml_data)
    with open('C:/baidunetdiskdownload/mysence/testsuits/new/dut基础设置_串口.yaml', 'r', encoding='utf-8') as file:
        yaml_data = yaml.safe_load(file)
    execute_yaml_steps(yaml_data)
    # with open('C:/baidunetdiskdownload/mysence/testsuits/new/dut基础设置_以太网.yaml', 'r', encoding='utf-8') as file:
    #     yaml_data = yaml.safe_load(file)
    # execute_yaml_steps(yaml_data)

