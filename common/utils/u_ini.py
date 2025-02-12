import os
from configparser import RawConfigParser, ConfigParser


def read_ini_file(file_path):
    """获取ini文件数据，返回字典"""
    if not os.path.isfile(file_path):
        raise FileNotFoundError("文件路径不存在，请检查路径是否正确：%s" % file_path)
    dictionary = {}
    config = RawConfigParser()
    config.read(file_path, encoding='utf-8')
    for section in config.sections():
        dictionary[section] = {}
        for option in config.options(section):
            dictionary[section][option] = config.get(section, option)
    return dictionary


def edit_ini_file(file_path, section, key, value):
    """写入ini文件数据"""
    if not os.path.isfile(file_path):
        raise FileNotFoundError("文件路径不存在，请检查路径是否正确：%s" % file_path)
    cfp = ConfigParser(comment_prefixes='/', allow_no_value=True)
    cfp.read(file_path, encoding='utf-8')
    cfp.set(section, key, value)
    cfp.write(open(file_path, 'w', encoding='utf-8'))
