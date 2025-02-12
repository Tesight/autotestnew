from common.container import LocalManager
from common.logger import Log


class ListAction(object):

    @classmethod
    @LocalManager.save_result
    def get_list_value(cls, list_value, list_index='0', result='result'):
        """获取列表中值"""
        if isinstance(list_value, str):
            list_value = eval(list_value)
        if isinstance(list_index, str):
            list_index = int(list_index)
        element_value = list_value[list_index]
        Log().logger.info(
            f'执行{cls.__name__}.get_list_value方法，返回值{result}==>'
            f'获取列表中值成功：{element_value}'
        )
        return element_value


if __name__ == '__main__':
    res = ListAction.get_list_value("['测试比对样品 - 登录']", '0')
    print(res)
