import os
import sys
import types
import importlib


def is_function(tup):
    """判断(name, object)是否为方法，返回bool"""
    name, item = tup
    return isinstance(item, types.FunctionType)


def import_module(module):
    """解析模块中的方法"""
    try:
        imported = importlib.import_module(module)
        imported_function = filter(is_function, vars(imported).items())  # 可迭代对象
        return {k: v for k, v in imported_function}
    except Exception as e:
        raise ModuleNotFoundError(f"模块{module}不存在！\n{e}")


def get_function_by_name(lib_path, py_name, func_name):
    """获取方法对象"""
    if not os.path.exists(lib_path):
        raise FileNotFoundError(f"lib目录不存在，请检查路径是否正确：{lib_path}")
    sys.path.append(lib_path)
    func_dict = import_module(py_name.split('.')[0])
    for k, v in func_dict.items():
        if k == func_name:
            return v


if __name__ == '__main__':
    lp = r'D:\01MyCode\01DemoCode\00temp00\autorunner\testsuits\01gjxt_web\testcase\casedata\lib'  # noqa
    pn = 'fun_demo.py'
    fn = 'say_hello'
    res = get_function_by_name(lp, pn, fn)
    print(res)
