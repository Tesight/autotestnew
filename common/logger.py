from logging import LogRecord
import os
import sys
import time
import logging
import dearpygui.dearpygui as dpg   
from common.comdata import CommonData
from common.utils.u_singleton import singleton


rq = time.strftime('%Y%m%d_%H', time.localtime()) + '.log'

log_config = {
    "formatter": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",  # noqa
    "level": "INFO"
}


@singleton
class Log(object):
    log_color = {'DEBUG': 'white', 'INFO': 'green', 'WARNING': 'yellow', 'ERROR': 'red', 'CRITICAL': 'bold_red'}

    # parent_tag = None

    def __init__(self, name=None,parent_tag = None):
        self.name = name
        self.logger = logging.getLogger(self.name)
        self.logger.setLevel(log_config['level'])
        self.formatter = logging.Formatter(log_config['formatter'])
        self.run_handler = None
        self.stream = sys.stderr
        self.parent_tag = parent_tag
        self.add_run_log_handler()
        self.add_ui_log_handler()

        # 控制台输出
        self.streamHandler = logging.StreamHandler(self.stream)
        self.streamHandler.setLevel(log_config['level'])
        self.streamHandler.setFormatter(self.formatter)
        self.logger.addHandler(self.streamHandler)



    def add_run_log_handler(self):
        if CommonData.RUN_DATA['project_name']:
            self.run_handler = logging.FileHandler(os.path.join(CommonData().get_log_path(), rq), 'a', encoding='utf-8')
            self.run_handler.setLevel(CommonData().get_config_data()['日志打印配置']['level'])
            self.logger.setLevel(CommonData().get_config_data()['日志打印配置']['level'])
            self.run_handler.setFormatter(self.formatter)
            self.logger.addHandler(self.run_handler)

    def add_ui_log_handler(self):
        # print(self.parent_tag,'-----------------')
        if self.parent_tag:
            self.ui_handler = My_UI_logger_handler(self.parent_tag)
            self.ui_handler.setLevel(CommonData().get_config_data()['日志打印配置']['level'])
            self.logger.setLevel(CommonData().get_config_data()['日志打印配置']['level'])
            self.ui_handler.setFormatter(self.formatter)
            self.logger.addHandler(self.ui_handler) 
        


    def get_logger(self):
        return self.logger

    
    def sys_debug(self,file_path):
        """调试"""
        f = open(os.path.join(file_path, "Terminal.log"), "w")
        sys.stdout = f
        sys.stderr = f
        self.stream = f
        


    def clear_log_ui(self):
        if self.parent_tag:
            dpg.delete_item(self.parent_tag,children_only=True) 




class My_UI_logger_handler(logging.Handler):
    def __init__(self,parentTag ) -> None:
        super().__init__()  
        self.parent_tag = parentTag

    def emit(self, record: LogRecord) -> None:
        msg = self.format(record)
        # print('------------------',msg,self.parent_tag)
        y_max = dpg.get_y_scroll_max(self.parent_tag)
        # x_max = dpg.get_x_scroll_max(self.parent_tag)
        
        # print('++++++++++++++++++++++',x_max,'-----',y_max)
        dpg.add_text(msg, parent=self.parent_tag)  
        dpg.set_y_scroll(self.parent_tag,y_max)
        
        

if __name__ == '__main__':
    a = Log().getLogger()
    print(a)
    b = Log().getLogger()
    print(b)
