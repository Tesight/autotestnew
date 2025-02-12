import os
from common.container import LocalManager
from common.comdata import CommonData
from common.logger import Log


class FileAction(object):

    @classmethod
    @LocalManager.save_result
    def get_file_joined_path(cls, file_name, result='result'):
        """获取file目录文件路径"""
        try:
            testcase_path = CommonData.get_testcase_path()
            file_path = os.path.join(testcase_path, 'casedata', 'file', file_name)  # noqa
            Log().logger.info(
                f'执行{cls.__name__}.get_file_joined_path方法，返回值{result}==>'
                f'获取file目录文件路径成功：{file_path}'
            )
            return file_path
        except Exception as e:
            Log().logger.error(f'执行{cls.__name__}.get_file_joined_path方法获取file目录文件路径失败！失败原因：{e}')
            raise e

    @classmethod
    @LocalManager.save_result
    def get_file_content(cls, file_path, mode, result='result'):
        """获取文件内容"""
        try:
            with open(file_path, mode) as f:
                content = f.read()
            Log().logger.info(
                f'执行{cls.__name__}.get_file_content方法，返回值{result}==>'
                f'获取文件内容成功：{content}'
            )
            return content
        except Exception as e:
            Log().logger.error(f'执行{cls.__name__}.get_file_content方法获取文件内容失败！失败原因：{e}')
            raise e

    @classmethod
    @LocalManager.save_result
    def get_file_object(cls, file_path, mode, result='result'):
        """获取文件对象"""
        try:
            file_object = open(file_path, mode)
            Log().logger.info(
                f'执行{cls.__name__}.get_file_object方法，返回值{result}==>'
                f'获取文件对象成功：{file_object}'
            )
            return file_object
        except Exception as e:
            Log().logger.error(f'执行{cls.__name__}.get_file_object方法获取文件对象失败！失败原因：{e}')
            raise e

    @classmethod
    def write_file_content(cls, file_path, mode, content):
        """写入文件内容"""
        try:
            with open(file_path, mode) as f:
                f.write(content)
            Log().logger.info(
                f'执行{cls.__name__}.write_file_content方法==>'
                f'写入文件内容成功！'
            )
        except Exception as e:
            Log().logger.error(f'执行{cls.__name__}.write_file_content方法写入文件内容失败！失败原因：{e}')
            raise e

    @classmethod
    @LocalManager.save_result
    def is_file_exist(cls, file_path, result='result'):
        """判断文件是否存在"""
        is_exist = os.path.exists(file_path)
        Log().logger.info(
            f'执行{cls.__name__}.is_file_exist方法，返回值{result}==>'
            f'判断文件是否存在：{str(is_exist)}'
        )
        return is_exist


if __name__ == '__main__':
    res = FileAction.get_file_joined_path('upload_file.txt')
    print(res)