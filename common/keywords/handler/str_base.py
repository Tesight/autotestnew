import re
from common.container import LocalManager
from common.logger import Log


class StrAction(object):

    @classmethod
    @LocalManager.save_result
    def re_match_str(cls, str_value, pattern, result='result'):
        """字符串正则匹配"""
        try:
            if isinstance(str_value, dict) or isinstance(str_value, list):
                str_value = str(str_value)
            new_value = re.findall(pattern, str_value)
            Log().logger.info(
                f'执行{cls.__name__}.re_match_str方法，返回值{result}==>'
                f'字符串正则匹配成功：{new_value}'
            )
            return new_value
        except AssertionError as e:
            Log().logger.error('正则匹配的入参不是字符串，请检查变量值。失败原因：%s' % e)
            raise e
        except BaseException as e:
            Log().logger.error('字符串正则匹配失败！失败原因：%s' % e)
            raise e

    @classmethod
    @LocalManager.save_result
    def str_join(cls, str_var1, str_var2, result='result'):
        """字符串拼接"""
        try:
            new_str = str(str_var1) + str(str_var2)
            Log().logger.info(
                f'执行{cls.__name__}.str_join方法，返回值{result}==>'
                f'字符串正则匹配成功：{new_str}'
            )
        except Exception as e:
            Log().logger.error(f'执行{cls.__name__}.str_join方法字符串拼接失败！失败原因：{e}')
            raise e
