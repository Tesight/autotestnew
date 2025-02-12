import os
import shutil


def file_all_delete(path):
    """删除目录下所有文件,不包含目录"""
    for filename in os.listdir(path):
        os.unlink(os.path.join(path, filename))


def file_copy(file_path, new_path):
    """文件或目录复制"""
    # if not os.path.exists(new_path):
      
    if os.path.isdir(file_path):
        shutil.copytree(file_path, new_path)
    else:
        shutil.copy(file_path, new_path)


def file_cut(file_path, new_path):
    """文件或目录剪切"""
    if os.path.isdir(file_path):
        shutil.copytree(file_path, new_path)
        shutil.rmtree(file_path)
    else:
        shutil.move(file_path, new_path)


def file_rename(file_path, new_path):
    """文件或目录重命名"""
    shutil.move(file_path, new_path)


def file_delete(file_path):
    """文件或目录删除"""
    if os.path.isdir(file_path):
        shutil.rmtree(file_path)
    else:
        os.unlink(file_path)


def file_operate(command, file_path, new_path=None):
    """文件操作"""
    if command == 'copy':
        file_copy(file_path, new_path)
    elif command == 'cut':
        file_cut(file_path, new_path)
    elif command == 'delete':
        file_delete(file_path)
    elif command == 'rename':
        file_rename(file_path, new_path)
    else:
        raise Exception(f"{command}操作未实现！")
