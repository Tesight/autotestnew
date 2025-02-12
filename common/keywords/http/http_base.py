import urllib3
from common.keywords.http.session import SessionManager
from common.logger import Log
from urllib3.exceptions import InsecureRequestWarning
from common.comdata import CommonData
from common.container import GlobalManager
from common.container import LocalManager
from common.utils.u_dict import dict_filtered
import allure

urllib3.disable_warnings(InsecureRequestWarning)


class HttpAction(object):
    """接口测试工具类"""

    @classmethod
    def request(cls, method, url, **kwargs):
        """接口请求公共封装"""
        try:
            unwanted_keys = ['result_code', 'result_json', 'result_text', 'result_content']
            request_kwargs = dict_filtered(kwargs, unwanted_keys)
            config = CommonData.get_config_item("项目运行设置")
            port = config.get("port", "")   # 获取配置文件中的端口号    
            if config["test_url"] not in url:
                if port:
                    url_ = config["test_url"] +':'+str(port)
                else:
                    url_ = config["test_url"]
                url = url_ + url
            Log().logger.info(f"{method}接口调用开始==>{url}")
            cls._request_kwargs(method, **kwargs)
            response = SessionManager.get_session().request(method, url, verify=False,timeout=10, **request_kwargs)
            cls._response_kwargs(method, response, **kwargs)
            Log().logger.info(f"{method}接口的响应时间==>{str(response.elapsed.total_seconds())}")
            Log().logger.info(f"{method}接口调用完成==>{url}")
            allure.attach(
                body=response.content.decode('utf-8'), name=f"{method}接口响应内容", attachment_type=allure.attachment_type.TEXT
            )   
            return response
        except Exception as e:
            with allure.step('捕获异常信息'):
                Log().logger.error(f"捕获异常信息：{str(e)}")   
            Log().logger.error(f"接口请求失败！：{e}")
            raise e

    @classmethod
    def cookies_clear(cls):
        """清空session"""
        try:
            SessionManager.get_session().cookies.clear()
            Log().logger.info(
                f"执行{cls.__name__}.cookies_clear方==>"
                "清除Session中的Cookies成功！"
            )
        except Exception as e:
            Log().logger.error(f"清除Session中的Cookies失败：{e}")
            raise e

    @staticmethod
    def _request_kwargs(method, **kwargs):
        """请求参数处理"""
        try:
            if kwargs.get("headers"):
                Log().logger.info(f"{method}接口请求头headers==>{str(kwargs.get('headers'))}")
            if kwargs.get("params"):
                Log().logger.info(f"{method}接口查询参数params==>{str(kwargs.get('params'))}")
            if kwargs.get("data"):
                Log().logger.info(f"{method}接口请求体data==>{str(kwargs.get('data'))}")
            if kwargs.get("json"):
                Log().logger.info(f"{method}接口请求体json==>{str(kwargs.get('json'))}")
            if kwargs.get("files"):
                Log().logger.info(f"{method}文件对象files==>{str(kwargs.get('files'))}")
        except BaseException as e:
            print(e)

    @staticmethod
    def _response_kwargs(method, response, **kwargs):
        """响应参数处理"""
        try:
            if kwargs.get("result_code"):
                result_code = response.status_code
                LocalManager.set_value(kwargs.get("result_code"), str(result_code))
                Log().logger.debug(f"{method}接口的响应码==>{str(result_code)}")
            if kwargs.get("result_json"):
                result_json = response.json()
                LocalManager.set_value(kwargs.get("result_json"), result_json)
                Log().logger.debug(f"{method}接口的json响应体==>{str(result_json)}")
            if kwargs.get("result_text"):
                result_text = response.text
                LocalManager.set_value(kwargs.get("result_text"), result_text)
                Log().logger.debug(f"{method}接口的text响应体：{result_text}")
            if kwargs.get("result_content"):
                result_content = response.content
                LocalManager.set_value(kwargs.get("result_content"), result_content)
                Log().logger.debug(f"{method}接口的content响应体：{result_content}")
        except BaseException as e:
            print(e)


if __name__ == "__main__":
    pass
