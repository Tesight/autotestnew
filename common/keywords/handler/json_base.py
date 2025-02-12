import jsonpath
from common.container import LocalManager
from common.logger import Log
import allure


class JsonAction(object):

    @classmethod
    @LocalManager.save_result
    def get_json_value(cls, json_data, json_path, result='result'):
        """获取json中的值"""
        value = jsonpath.jsonpath(json_data, json_path)[0]
        Log().logger.info(
            f'执行{cls.__name__}.get_json_value方法，返回值{result}==>'
            f'获取json中的值成功：{value}'
        )
        allure.attach(
            body=str(value),
            name=f"获取json中的值：{json_path}",
            attachment_type=allure.attachment_type.TEXT
        )
        return value


if __name__ == '__main__':
    res = JsonAction.get_json_value({"result": "success", "locate": "/zentao/"}, '$.result')
    print(res)
