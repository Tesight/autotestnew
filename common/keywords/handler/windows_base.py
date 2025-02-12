import io
import os
import random
import shutil
import subprocess
from common.container import LocalManager
from common.logger import Log


class WindowsAction(object):

    @classmethod
    @LocalManager.save_result
    def execute_cmd(cls, cmd, buffering=-1, result='result'):
        if not isinstance(cmd, str):  # 判断输入谁否为字符串，不是则报错
            raise TypeError("invalid cmd type (%s, expected string)" % type(cmd))
        if buffering == 0 or buffering is None:  # 判断缓冲区大小是否为0和空，是则报错
            raise ValueError("popen() does not support unbuffered streams")  # noqa
        proc = subprocess.Popen(cmd,  # 输入的cmd命令
                                shell=True,  # 通过操作系统的 shell 执行指定的命令
                                stdout=subprocess.PIPE,  # 将结果标准输出
                                bufsize=buffering)  # -1，使用系统默认的缓冲区大小
        response = os._wrap_close(io.TextIOWrapper(proc.stdout), proc)  # noqa
        Log().logger.info(
            f'执行{cls.__name__}.execute_cmd方法，返回值{result}==>'
            f'执行CMD命令，执行成功：{response}'
        )
        return response

    @classmethod
    @LocalManager.save_result
    def file_rename(cls, filename, result='result'):
        """生成新的文件名"""
        list_f = filename.split(".")
        str1 = list_f[0]
        str2 = list_f[1]
        ran_str = random.sample('abcdefghijklmnopqrstuvwxyz', 4)  # noqa
        str3 = "".join(ran_str)
        new_file_name = str1 + str3 + "." + str2
        Log().logger.info(
            f'执行{cls.__name__}.file_rename方法，返回值{result}==>'
            f'生成的新字符串为：{new_file_name}'
        )
        return new_file_name

    @classmethod
    def file_add(cls, path, filename, content=None):
        """新建文件"""
        cmd1 = path[:2]
        if not content:
            cls.execute_cmd("%s & cd %s & type nul > %s" % (cmd1, path, filename))
            Log().logger.info(
                f'执行{cls.__name__}.file_add方法==>'
                f'空文件新建执行完成，文件：{filename}'
            )
        else:
            cls.execute_cmd("%s & cd %s & echo %s > %s" % (cmd1, path, content, filename))
            Log().logger.info(
                f'执行{cls.__name__}.file_add方法==>'
                f'内容文件新建执行完成，文件：{filename}'
            )

    @classmethod
    def open_file(cls, filepath):
        """打开文件并关闭"""
        try:
            os.startfile(filepath)
            Log().logger.info(
                f'执行{cls.__name__}.open_file方法==>'
                f'打开文件：{filepath}'
            )
        except Exception as e:
            print(e)
            subprocess.Popen(['xdg-open', filepath])
            Log().logger.info(
                f'执行{cls.__name__}.open_file方法==>'
                f'打开文件：{filepath}'
            )

    @classmethod
    @LocalManager.save_result
    def file_copy(cls, filepath, path, result='result'):
        """文件复制"""
        try:
            copy_path = shutil.copy(filepath, path)
            Log().logger.info(
                f'执行{cls.__name__}.file_copy方法，返回值{result}==>'
                f'文件复制成功，路径：{copy_path}'
            )
            return copy_path
        except Exception as e:
            Log().logger.info(
                f'执行{cls.__name__}.file_copy方法==>'
                f'文件复制失败\n{e}'
            )

    @classmethod
    @LocalManager.save_result
    def file_cut(cls, filepath, path, result='result'):
        """文件剪切"""
        try:
            move_path = shutil.move(filepath, path)
            Log().logger.info(
                f'执行{cls.__name__}.file_cut方法，返回值{result}==>'
                f'文件剪切成功，路径：{move_path}'
            )
            return move_path
        except Exception as e:
            Log().logger.info(
                f'执行{cls.__name__}.file_copy方法==>'
                f'文件剪切失败\n{e}'
            )

    @classmethod
    def file_all_delete(cls, path):
        """删除所有文件"""
        for filename in os.listdir(path):
            os.unlink(path + "\\" + filename)
        Log().logger.info(
            f'执行{cls.__name__}.file_all_delete方法==>'
            f'所有文件删除成功，路径：{path}'
        )

    @classmethod
    def start_process(cls, process):
        """开启windows进程"""
        cls.execute_cmd("start %s" % process)
        Log().logger.info(
            f'执行{cls.__name__}.start_process方法==>'
            f'进程开启：{process}'
        )

    @classmethod
    def close_process(cls, process, is_force=False):
        """关闭windows进程"""
        if is_force:
            cls.execute_cmd("taskkill /f /t /im %s" % process)  # noqa
            Log().logger.info(
                f'执行{cls.__name__}.close_process方法==>'
                f'强制关闭进程：{process}'
            )
        else:
            cls.execute_cmd("taskkill /t /im %s" % process)  # noqa
            Log().logger.info(
                f'执行{cls.__name__}.close_process方法==>'
                f'关闭进程：{process}'
            )


if __name__ == "__main__":
    w = WindowsAction()
    res = w.execute_cmd('start wps')
    print(res)
