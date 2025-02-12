import os
import os.path


def get_current_directory():
    """获取当前工作目录"""
    return os.getcwd()


def join_paths(*paths):
    """拼接多个路径"""
    return os.path.join(*paths)


def get_basename(path):
    """获取文件名或目录名"""
    return os.path.basename(path)


def get_dirname(path):
    """获取路径中的目录部分"""
    return os.path.dirname(path)


def is_path_exists(path):
    """检查路径是否存在"""
    return os.path.exists(path)


def is_file(path):
    """检查是否为文件"""
    return os.path.isfile(path)


def is_directory(path):
    """检查是否为目录"""
    return os.path.isdir(path)


def create_directory(path):
    """创建目录"""
    os.makedirs(path, exist_ok=True)


def list_directory(path):
    """列出目录下的文件和子目录"""
    return os.listdir(path)


def remove_file(path):
    """删除文件"""
    os.remove(path)


def remove_directory(path):
    """递归删除目录及其内容"""
    os.rmdir(path)


def format_path_to_linux(path):
    """格式化路径为Linux下的路径写法"""
    return path.replace('\\', '/')


def get_directory_tree(folder: str) -> dict:
    """遍历本地目录返回字典树"""
    dir_tree = {'children': []}
    if os.path.isfile(folder):
        return {'name': os.path.basename(folder), 'href': os.path.abspath(folder)}
    else:
        dir_tree['name'] = os.path.basename(folder)
        dir_tree['href'] = folder
        items = sorted(os.listdir(folder), key=lambda x: (not os.path.isdir(os.path.join(folder, x)), x))
        for item in items:
            dir_tree['children'].append(get_directory_tree(os.path.join(folder, item)))
        return dir_tree


def get_files_path_dict(dir_path):
    """遍历目录下所有层级获取所有图片的路径"""
    path = {}
    value = None
    path_lists = [path_list for path_list in os.walk(dir_path)]
    for path_list in path_lists:
        for file_path in path_list:
            if isinstance(file_path, str):
                value = file_path
            elif isinstance(file_path, list):
                for file_name in file_path:
                    path[file_name.split('.')[0]] = os.path.join(value, file_name)
    return path
