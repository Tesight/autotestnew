import json
import os
from jsonpath_ng import parse


def read_json_file(json_path):
    """从json中获取数据"""
    if not os.path.isfile(json_path):
        raise FileNotFoundError("文件路径不存在，请检查路径是否正确：%s" % json_path)
    with open(json_path, 'r', encoding='utf-8') as f:
        json_data = json.load(f)
    return json_data


def set_json_value(json_data, json_path, value):
    """为json中的参数赋值"""
    parser = parse(json_path)
    parser.update(json_data, value)
    return json_data
