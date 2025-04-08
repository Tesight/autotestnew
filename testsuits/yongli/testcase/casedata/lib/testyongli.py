# test_static_position.py
import sys
import os
import yaml
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../../../'))
sys.path.append(project_root)

# 然后导入模块
from testsuits.yongli.testcase.casedata.lib.jinduceshi import capture_sensitivity, tracking_sensitivity

def test_static_position_bias():
    standard=-130
    # 设置静态位置
    
    # rsv_location = requests.get(url='http://'+'127.0.0.1:5000'+'/receiver/location').json()
    # print(rsv_location)
    print("开始捕获灵敏度测试...")
    result = capture_sensitivity(
        data_num =9,address = '127.0.0.1:5000'
    )
    print(f"测试状态: {result['status']}")
    if result['status'] == 'success':
        print(f"捕获灵敏度静态误差: {result['result_static_mbias']} 米")
        print(f"测试结果: {'通过' if result['pc'] <= standard else '未通过'}")
    else:
        print(f"测试失败: {result.get('message', '未知错误')}")
    
    # standard=-130
    # # 设置静态位置
    
    # # rsv_location = requests.get(url='http://'+'127.0.0.1:5000'+'/receiver/location').json()
    # # print(rsv_location)
    # print("开始跟踪灵敏度测试...")
    # result = tracking_sensitivity(
    #     data_num =9,address = '127.0.0.1:5000'
    # )
    # print(f"测试状态: {result['status']}")
    # if result['status'] == 'success':
    #     print(f"跟踪灵敏度静态误差: {result['result_static_mbias']} 米")
    #     print(f"测试结果: {'通过' if result['pc'] <= standard else '未通过'}")
    # else:
    #     print(f"测试失败: {result.get('message', '未知错误')}")
    return result

if __name__ == "__main__":
    test_static_position_bias()