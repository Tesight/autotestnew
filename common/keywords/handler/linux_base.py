#!/usr/bin/python
# -*- coding:utf-8 -*-
import paramiko
from common.container import GlobalManager, LocalManager
from common.logger import Log
from common.comdata import CommonData


class SSHBase(object):

    def __init__(self, ip, username, password, port=22):
        self.ip = ip
        self.port = int(port)
        self.username = username
        self.password = password

    def shell_cmd(self, cmd):
        try:
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.connect(self.ip, self.port, self.username, self.password, timeout=5)
            stdin, stdout, stderr = ssh.exec_command(cmd)
            content = stdout.read().decode('utf-8')
            res = content.split('\n')
            ssh.close()
            return res
        except Exception as e:
            Log().logger.error('远程执行shell命令失败！！！', e)
            return False

    def shell_upload(self, local_path, remote_path):
        try:
            transport = paramiko.Transport((self.ip, self.port))
            transport.connect(username=self.username, password=self.password)
            sftp = paramiko.SFTPClient.from_transport(transport)
            sftp.put(local_path, remote_path)
            transport.close()
            return True
        except Exception as e:
            Log().logger.error('文件上传失败！！！', e)
            return False

    def shell_download(self, local_path, remote_path):
        try:
            transport = paramiko.Transport((self.ip, self.port))
            transport.connect(username=self.username, password=self.password)
            sftp = paramiko.SFTPClient.from_transport(transport)
            sftp.get(remote_path, local_path)
            transport.close()
            return True
        except Exception as e:
            Log().logger.error('文件下载失败！！！', e)
            return False


class LinuxAction(object):

    @staticmethod
    def _get_ssh_config(ip=None, username=None, password=None, port=None):
        """获取ssh配置数据"""
        ssh_config = {
            "ip": ip,
            "username": username,
            "password": password,
            "port": port
        }
        config_info = CommonData.get_config_item("SSH")
        if not ip:
            ssh_config["ip"] = config_info["ip"]
        if not username:
            ssh_config["username"] = config_info["username"]
        if not password:
            ssh_config["password"] = config_info["password"]
        if not port:
            ssh_config["port"] = config_info["port"]
        Log().logger.info("获取SSH配置信息：{}".format(ssh_config))
        return ssh_config

    @classmethod
    @LocalManager.save_result
    def ssh_shell(cls, shell, ip=None, username=None, password=None, port=None, result='result'):
        """远程执行shell"""
        Log().logger.info("传入shell命令:{}".format(shell))
        ssh_config = cls._get_ssh_config(ip, username, password, port)
        ssh = SSHBase(**ssh_config)
        ssh_result = ssh.shell_cmd(shell)
        Log().logger.info(
            f'执行{cls.__name__}.ssh_shell方法，返回值{result}==>'
            f'执行shell成功：{ssh_result}'
        )
        return ssh_result

    @classmethod
    def ssh_upload(cls, local_path, remote_path, ip=None, username=None, password=None, port=None, result='result'):
        """远程文件上传，返回bool"""
        Log().logger.info('待上传文件路径：{}'.format(local_path))
        ssh_config = cls._get_ssh_config(ip, username, password, port)
        ssh = SSHBase(**ssh_config)
        ssh_result = ssh.shell_upload(local_path, remote_path)
        Log().logger.info(
            f'执行{cls.__name__}.ssh_upload方法，返回值{result}==>'
            f'文件上传成功，上传路径：{remote_path}'
        )
        return ssh_result

    @classmethod
    def shell_download(cls, local_path, remote_path, ip=None, username=None, password=None, port=None, result='result'):
        """远程文件下载，返回bool"""
        Log().logger.info('待下载文件路径：{}'.format(remote_path))
        ssh_config = cls._get_ssh_config(ip, username, password, port)
        ssh = SSHBase(**ssh_config)
        ssh_result = ssh.shell_download(local_path, remote_path)
        Log().logger.info(
            f'执行{cls.__name__}.shell_download方法，返回值{result}==>'
            f'文件下载成功，下载路径：{local_path}'
        )
        return ssh_result
