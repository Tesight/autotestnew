import time,allure
from common.logger import Log
from common.container import LocalManager



class TimeAction(object):

    @classmethod
    def time_sleep(cls, second):
        """时间等待"""
        Log().logger.info(
            f'开始执行{cls.__name__}.time_sleep方法==>时间等待{second}秒'   
        )
        time.sleep(second)
        allure.attach(
            body=f'执行{cls.__name__}.time_sleep方法==>时间等待{second}秒',
            name=f'执行{cls.__name__}.time_sleep方法==>时间等待{second}秒',
            attachment_type=allure.attachment_type.TEXT 
        )
        
        Log().logger.info(
            f'执行{cls.__name__}.time_sleep方法 完成==>'
            f'时间等待{second}秒'
        )
        
    @classmethod
    @LocalManager.save_result
    def time_now(cls,result = 'result'):
        """获取当前时间戳"""
        time_now = time.time()
        allure.attach(
            body=f'执行{cls.__name__}.time_now方法==>当前时间戳为{time_now}',
            name=f'执行{cls.__name__}.time_now方法==>当前时间戳为{time_now}',
            attachment_type=allure.attachment_type.TEXT 
        )
        
        Log().logger.info(
            f'执行{cls.__name__}.time_now方法==>'
            f'当前时间戳为{result}'
        )   
        return time_now