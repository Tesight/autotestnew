import os
import zipfile


def make_zip(local_path, p_name):
    """打包zip"""
    zip_file = zipfile.ZipFile(p_name, 'w', zipfile.ZIP_DEFLATED)
    pre_len = len(os.path.dirname(local_path))
    for parent, dirname, filenames in os.walk(local_path):
        for filename in filenames:
            path_file = os.path.join(parent, filename)
            arc_name = path_file[pre_len:].strip(os.path.sep)
            zip_file.write(path_file, arc_name)
    zip_file.close()
    return p_name
