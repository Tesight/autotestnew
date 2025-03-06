import yaml
import os
from filelock import FileLock


def read_yaml_file(yaml_path):
    """读取yaml文件"""
    if not os.path.isfile(yaml_path):
        raise FileNotFoundError("文件路径不存在，请检查路径是否正确：%s" % yaml_path)
    with open(yaml_path, 'r', encoding='utf-8') as doc:
        content = yaml.load(doc, Loader=yaml.Loader)
    return content


def write_yaml_file(yaml_path, data):
    """写入yaml文件"""
    if not os.path.isfile(yaml_path):
        raise FileNotFoundError("文件路径不存在，请检查路径是否正确：%s" % yaml_path)
    with open(yaml_path, 'w', encoding='utf-8') as f:
        yaml.dump(data, f, Dumper=yaml.Dumper, allow_unicode=True,sort_keys=False)

def append_test_item(yaml_file, test_item, test_info=None):
    """
    向YAML测试报告文件添加新的测试项
    
    参数:
        yaml_file (str): YAML文件路径
        test_item (dict): 要添加的测试项数据，如 {'测试项目': '动态定位精度', ...}
        test_info (dict, optional): 测试基本信息，仅在需要创建新结构时使用
        
    返回:
        bool: 操作成功返回True，否则返回False
    """
    # 如果未提供测试基本信息，使用默认值
    if test_info is None:
        test_info = {
            '测试编号': 'TEST-2025-0228',
            '测试时间': '2025-02-28 14:30:00',
            '测试人': '车载接收机',
            '环境温度': '25°C',
            '环境湿度': '65%',
            '备注': '在开阔场地进行测试，天气晴朗，无电磁干扰'
        }
    
    try:
        # 确保文件存在
        if not os.path.exists(yaml_file):
            with open(yaml_file, 'w', encoding='utf-8') as f:
                pass
                
        with FileLock(f"{yaml_file}.lock"):
            # 读取现有数据
            try:
                data = read_yaml_file(yaml_file)
            except FileNotFoundError:
                # 如果文件不存在但路径有效，创建空文件
                with open(yaml_file, 'w', encoding='utf-8') as f:
                    pass
                data = None
            
            if data is None or not isinstance(data, list) or len(data) == 0:
                # 如果文件为空或格式不正确，创建新的结构
                data = [{
                    '测试基本信息': test_info,
                    '测试项目列表': [test_item]
                }]
            else:
                # 寻找包含"测试项目列表"的条目
                found = False
                for item in data:
                    if isinstance(item, dict) and '测试项目列表' in item:
                        # 找到了测试项目列表，追加新测试项
                        item['测试项目列表'].append(test_item)
                        found = True
                        break
                        
                # 如果没有找到测试项目列表，检查第一个条目是否有测试基本信息
                if not found and len(data) > 0 and isinstance(data[0], dict) and '测试基本信息' in data[0]:
                    # 在第一个条目中添加测试项目列表
                    data[0]['测试项目列表'] = data[0].get('测试项目列表', []) + [test_item]
                    found = True
                    
                # 如果还是没找到合适的位置，删除可能存在的顶层测试项并添加到正确的结构中
                if not found:
                    # 过滤掉可能是单独测试项的顶层条目
                    data = [item for item in data if not (isinstance(item, dict) and '测试项目' in item)]
                    # 如果第一个条目是字典且没有测试基本信息，添加基本信息和测试项目列表
                    if len(data) > 0 and isinstance(data[0], dict):
                        data[0]['测试项目列表'] = data[0].get('测试项目列表', []) + [test_item]
                    else:
                        # 创建新的结构
                        data.insert(0, {
                            '测试基本信息': test_info,
                            '测试项目列表': [test_item]
                        })

            # 写回文件
            write_yaml_file(yaml_file, data)
            return True
            
    except Exception as e:
        print(f"添加测试项目时出错: {str(e)}")
        return False

# 使用示例:
if __name__ == "__main__":
    # 新的测试项目数据
    new_test_item = {
        '测试项目': '动态定位精度',
        '测试数据': 16,
        '标准要求值': 15,
        '测试结果': 'FAIL'
    }
    
    yaml_file = 'c:/baidunetdiskdownload/mysence/testsuits/yongli/testcase/casedata/lib/测试报告.yaml'
    
    # 调用函数添加测试项
    if append_test_item(yaml_file, new_test_item):
        print(f"测试项目已添加到测试项目列表中")
    else:
        print(f"添加测试项目失败")