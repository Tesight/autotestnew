import os
import yaml
# from ruamel import yaml


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
