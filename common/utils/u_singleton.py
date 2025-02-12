def singleton(cls):
    """单例装饰器"""
    def single(*arg, **kwargs):
        if not hasattr(cls, 'instance'):
            cls.instance = cls(*arg, **kwargs)
        return cls.instance
    return single
