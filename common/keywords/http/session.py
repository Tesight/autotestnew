import requests


class SessionManager:
    _session = None

    @classmethod
    def get_session(cls):
        """获取会话保存器"""
        if not cls._session:
            cls._session = requests.session()  # 将session会话保存
        return cls._session

    @classmethod
    def close_session(cls):
        """关闭会话保存器"""
        if cls._session:
            cls._session.close()
            cls._session = None
