from logging import LogRecord
import os
import sys
import time
import logging
from common.utils.u_singleton import singleton


rq = time.strftime('%Y%m%d_%H', time.localtime()) + '.log'

log_config = {
    "formatter": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",  # noqa
    "level": "INFO"
}


@singleton
class Log(object):
    log_color = {'DEBUG': 'white', 'INFO': 'green', 'WARNING': 'yellow', 'ERROR': 'red', 'CRITICAL': 'bold_red'}
    SERVER_LOG_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'logs')
    
    # parent_tag = None

    def __init__(self, name=None,parent_tag = None):
        self.name = name
        self.logger = logging.getLogger(self.name)
        self.logger.setLevel(log_config['level'])
        self.formatter = logging.Formatter(log_config['formatter'])
        self.run_handler = None
        self.stream = sys.stderr
        self.parent_tag = parent_tag

        self.add_server_log_handler()


        # 控制台输出
        self.streamHandler = logging.StreamHandler(self.stream)
        self.streamHandler.setLevel(log_config['level'])
        self.streamHandler.setFormatter(self.formatter)
        self.logger.addHandler(self.streamHandler)


    def add_server_log_handler(self):
        """为服务器添加专用日志处理器，无需依赖 CommonData"""
        try:
            if not os.path.exists(self.SERVER_LOG_DIR):
                os.makedirs(self.SERVER_LOG_DIR)
            
            server_log_file = os.path.join(self.SERVER_LOG_DIR, f'server_{rq}')
            self.run_handler = logging.FileHandler(server_log_file, 'a', encoding='utf-8')
            self.run_handler.setLevel(log_config['level'])
            self.run_handler.setFormatter(self.formatter)
            self.logger.addHandler(self.run_handler)
            print(f"服务器日志将写入: {server_log_file}")
        except Exception as e:
            print(f"无法创建服务器日志处理器: {e}")

