#
class GlobalManager:
    """全局变量变量"""
    global_dict = {}

    @classmethod
    def init_global(cls):
        cls.global_dict = dict()

    @classmethod
    def set_value(cls, name, value):
        cls.global_dict[name] = value


    @classmethod
    def get_value(cls, name):
        try:
            print(cls.global_dict)
            return cls.global_dict[name]
        except KeyError as e:
            print("获取全局变量名称：{}不存在：{}".format(name, e))

    @classmethod
    def clear(cls):
        cls.global_dict.clear()


class LocalManager:
    """局部变量"""
    local_dict = {}

    @classmethod
    def init_local(cls):
        cls.local_dict = dict()

    @classmethod
    def set_value(cls, name, value):
        cls.local_dict[name] = value

    @classmethod
    def get_value(cls, name):
        try:
            return cls.local_dict[name]
        except KeyError as e:
            print("获取局部变量名称：{}不存在：{}".format(name, e))

    @classmethod
    def clear(cls):
        cls.local_dict.clear()

    @classmethod
    def save_result(cls, func):
        def wrapper(*args, **kwargs):
            try:
                result = func(*args, **kwargs)
                cls.set_value(kwargs.get('result'), result)
                return result
            except Exception as e:  # noqa
                cls.set_value(kwargs.get('result'), None)
                return None
        return wrapper


if __name__ == "__main__":
    g = GlobalManager()
    res = g.get_value('driver')
    print(res)
