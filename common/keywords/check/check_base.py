import re
from typing import Text, Any, Union
from common.logger import Log
import allure


class CheckAction:

    @classmethod
    def equal(cls, real_value: Any, expect_value: Any):
        try:
            assert real_value == expect_value
            Log().logger.info(
                "[{}.equal]校验两个值相等，验证成功：{}=={}".format(cls.__name__, real_value, expect_value)
            )
            allure.attach(
                body = "[{}.equal]校验两个值相等，验证成功：{}=={}".format(cls.__name__, real_value, expect_value),
                name= "equal", attachment_type=allure.attachment_type.TEXT  
                )
        except Exception as e:
            Log().logger.error(
                "[{}.equal]校验两个值相等，验证失败：{}=={}".format(cls.__name__, real_value, expect_value)
            )
            allure.attach(
                body="[{}.equal]校验两个值相等，验证失败：{}=={}".format(cls.__name__, real_value, expect_value),
                name= "equal", attachment_type=allure.attachment_type.TEXT  
                )
            
            raise e

    @classmethod
    def not_equal(cls, real_value: Any, expect_value: Any, message: Text = ""):
        try:
            assert real_value != expect_value, message
            Log().logger.info(
                "[{}.not_equal]校验两个值不相等，验证成功：{}!={}".format(cls.__name__, real_value, expect_value)
            )
            allure.attach(
                body = "[{}.not_equal]校验两个值不相等，验证成功：{}!={}".format(cls.__name__, real_value, expect_value),
                name= "not_equal", attachment_type=allure.attachment_type.TEXT  
                )   
        except Exception as e:
            Log().logger.error(
                "[{}.not_equal]校验两个值不相等，验证失败：{}!={}".format(cls.__name__, real_value, expect_value)
            )
            allure.attach(
                body="[{}.not_equal]校验两个值不相等，验证失败：{}!={}".format(cls.__name__, real_value, expect_value),
                name= "not_equal", attachment_type=allure.attachment_type.TEXT  
                )   
            raise e

    @classmethod
    def greater_than(cls, real_value: Union[int, float], expect_value: Union[int, float], message: Text = ""):
        try:
            assert real_value > expect_value, message
            Log().logger.info(
                "[{}.greater_than]校验实际结果大于期望结果，验证成功：{}>{}".format(cls.__name__, real_value, expect_value)
            )
            allure.attach(
                body = "[{}.greater_than]校验实际结果大于期望结果，验证成功：{}>{}".format(cls.__name__, real_value, expect_value),
                name= "greater_than", attachment_type=allure.attachment_type.TEXT  
                )
        except Exception as e:
            Log().logger.error(
                "[{}.greater_than]校验实际结果大于期望结果，验证失败：{}>{}".format(cls.__name__, real_value, expect_value)
            )
            allure.attach(
                body="[{}.greater_than]校验实际结果大于期望结果，验证失败：{}>{}".format(cls.__name__, real_value, expect_value),
                name= "greater_than", attachment_type=allure.attachment_type.TEXT  
                )   
            raise e

    @classmethod
    def less_than(cls, real_value: Union[int, float], expect_value: Union[int, float], message: Text = ""):
        try:
            assert real_value < expect_value, message
            Log().logger.info(
                "[{}.less_than]校验实际结果小于期望结果，验证成功：{}<{}".format(cls.__name__, real_value, expect_value)
            )
            allure.attach(
                body = "[{}.less_than]校验实际结果小于期望结果，验证成功：{}<{}".format(cls.__name__, real_value, expect_value),
                name= "less_than", attachment_type=allure.attachment_type.TEXT  
                )   
        except Exception as e:
            Log().logger.error(
                "[{}.less_than]校验实际结果小于期望结果，验证失败：{}<{}".format(cls.__name__, real_value, expect_value)
            )
            allure.attach(
                body="[{}.less_than]校验实际结果小于期望结果，验证失败：{}<{}".format(cls.__name__, real_value, expect_value),
                name= "less_than", attachment_type=allure.attachment_type.TEXT  
                )   
            raise e

    @classmethod
    def greater_or_equals(cls, real_value: Union[int, float], expect_value: Union[int, float], message: Text = ""):
        try:
            assert real_value >= expect_value, message
            Log().logger.info(
                "[{}.greater_or_equals]校验实际结果大于等于期望结果，验证成功：{}>={}".format(cls.__name__, real_value, expect_value)
            )
            allure.attach(
                body = "[{}.greater_or_equals]校验实际结果大于等于期望结果，验证成功：{}>={}".format(cls.__name__, real_value, expect_value),
                name= "greater_or_equals", attachment_type=allure.attachment_type.TEXT  
                )   
        except Exception as e:
            Log().logger.error(
                "[{}.greater_or_equals]校验实际结果大于等于期望结果，验证失败：{}>={}".format(cls.__name__, real_value, expect_value)
            )
            allure.attach(
                body="[{}.greater_or_equals]校验实际结果大于等于期望结果，验证失败：{}>={}".format(cls.__name__, real_value, expect_value),
                name= "greater_or_equals", attachment_type=allure.attachment_type.TEXT  
                )       
            raise e

    @classmethod
    def less_or_equals(cls, real_value: Union[int, float], expect_value: Union[int, float], message: Text = ""):
        try:
            assert real_value <= expect_value, message
            Log().logger.info(
                "[{}.less_or_equals]校验实际结果小于等于期望结果，验证成功：{}<={}".format(cls.__name__, real_value, expect_value)
            )
            allure.attach(
                body = "[{}.less_or_equals]校验实际结果小于等于期望结果，验证成功：{}<={}".format(cls.__name__, real_value, expect_value),
                name= "less_or_equals", attachment_type=allure.attachment_type.TEXT  
                )   
        except Exception as e:
            Log().logger.error(
                "[{}.less_or_equals]校验实际结果小于等于期望结果，验证失败：{}<={}".format(cls.__name__, real_value, expect_value)
            )
            allure.attach(
                body="[{}.less_or_equals]校验实际结果小于等于期望结果，验证失败：{}<={}".format(cls.__name__, real_value, expect_value),
                name= "less_or_equals", attachment_type=allure.attachment_type.TEXT  
                )   
            raise e

    @classmethod
    def string_equals(cls, real_value: Text, expect_value: Any, message: Text = ""):
        try:
            assert str(real_value) == str(expect_value), message
            Log().logger.info(
                "[{}.string_equals]校验两个字符串相等，验证成功：{}={}".format(cls.__name__, real_value, expect_value)
            )
            allure.attach(
                body = "[{}.string_equals]校验两个字符串相等，验证成功：{}={}".format(cls.__name__, real_value, expect_value),
                name= "string_equals", attachment_type=allure.attachment_type.TEXT  
                )   
        except Exception as e:
            Log().logger.error(
                "[{}.string_equals]校验两个字符串相等，验证失败：{}={}".format(cls.__name__, real_value, expect_value)
            )
            allure.attach(
                body="[{}.string_equals]校验两个字符串相等，验证失败：{}={}".format(cls.__name__, real_value, expect_value),
                name= "string_equals", attachment_type=allure.attachment_type.TEXT  
                )   
            raise e

    @classmethod
    def length_equal(cls, real_value: Text, expect_value: int, message: Text = ""):
        try:
            assert isinstance(expect_value, int), "expect_value should be int type"
            assert len(real_value) == expect_value, message
            Log().logger.info(
                "[{}.length_equal]校验文本长度等于期望数值，验证成功：{}={}".format(cls.__name__, real_value, expect_value)
            )
            allure.attach(
                body = "[{}.length_equal]校验文本长度等于期望数值，验证成功：{}={}".format(cls.__name__, real_value, expect_value),
                name= "length_equal", attachment_type=allure.attachment_type.TEXT  
                )   
        except Exception as e:
            Log().logger.error(
                "[{}.length_equal]校验文本长度等于期望数值，验证失败：{}={}".format(cls.__name__, real_value, expect_value)
            )
            allure.attach(
                body="[{}.length_equal]校验文本长度等于期望数值，验证失败：{}={}".format(cls.__name__, real_value, expect_value),
                name= "length_equal", attachment_type=allure.attachment_type.TEXT  
                )       
            raise e

    @classmethod
    def length_greater_than(cls, real_value: Text, expect_value: Union[int, float], message: Text = ""):
        try:
            assert isinstance(
                expect_value, (int, float)
            ), "expect_value should be int/float type"
            assert len(real_value) > expect_value, message
            Log().logger.info(
                "[{}.length_greater_than]校验文本长度大于期望数值，验证成功：{}>{}".format(cls.__name__, real_value, expect_value)
            )
            allure.attach(
                body = "[{}.length_greater_than]校验文本长度大于期望数值，验证成功：{}>{}".format(cls.__name__, real_value, expect_value),
                name= "length_greater_than", attachment_type=allure.attachment_type.TEXT  
                )   
        except Exception as e:
            Log().logger.error(
                "[{}.length_greater_than]校验文本长度大于期望数值，验证失败：{}>{}".format(cls.__name__, real_value, expect_value)
            )
            allure.attach(
                body="[{}.length_greater_than]校验文本长度大于期望数值，验证失败：{}>{}".format(cls.__name__, real_value, expect_value),
                name= "length_greater_than", attachment_type=allure.attachment_type.TEXT  
                )   
            raise e

    @classmethod
    def length_greater_or_equals(cls, real_value: Text, expect_value: Union[int, float], message: Text = ""):
        try:
            assert isinstance(
                expect_value, (int, float)
            ), "expect_value should be int/float type"
            assert len(real_value) >= expect_value, message
            Log().logger.info(
                "[{}.length_greater_or_equals]校验文本长度大于等于期望数值，验证成功：{}>={}".format(cls.__name__, real_value, expect_value)
            )
            allure.attach(
                body = "[{}.length_greater_or_equals]校验文本长度大于等于期望数值，验证成功：{}>={}".format(cls.__name__, real_value, expect_value),
                name= "length_greater_or_equals", attachment_type=allure.attachment_type.TEXT  
                )   
        except Exception as e:
            Log().logger.error(
                "[{}.length_greater_or_equals]校验文本长度大于等于期望数值，验证失败：{}>={}".format(cls.__name__, real_value, expect_value)
            )
            allure.attach(
                body="[{}.length_greater_or_equals]校验文本长度大于等于期望数值，验证失败：{}>={}".format(cls.__name__, real_value, expect_value),
                name= "length_greater_or_equals", attachment_type=allure.attachment_type.TEXT  
                )   
            raise e

    @classmethod
    def length_less_than(cls, real_value: Text, expect_value: Union[int, float], message: Text = ""):
        try:
            assert isinstance(
                expect_value, (int, float)
            ), "expect_value should be int/float type"
            assert len(real_value) < expect_value, message
            Log().logger.info(
                "[{}.length_less_than]校验文本长度小于期望数值，验证成功：{}<{}".format(cls.__name__, real_value, expect_value)
            )
            allure.attach(
                body = "[{}.length_less_than]校验文本长度小于期望数值，验证成功：{}<{}".format(cls.__name__, real_value, expect_value),
                name= "length_less_than", attachment_type=allure.attachment_type.TEXT  
                )
        except Exception as e:
            Log().logger.error(
                "[{}.length_less_than]校验文本长度小于期望数值，验证失败：{}<{}".format(cls.__name__, real_value, expect_value)
            )
            allure.attach(
                body="[{}.length_less_than]校验文本长度小于期望数值，验证失败：{}<{}".format(cls.__name__, real_value, expect_value),
                name= "length_less_than", attachment_type=allure.attachment_type.TEXT  
                )   
            raise e

    @classmethod
    def length_less_or_equals(cls, real_value: Text, expect_value: Union[int, float], message: Text = ""):
        try:
            assert isinstance(
                expect_value, (int, float)
            ), "expect_value should be int/float type"
            assert len(real_value) <= expect_value, message
            Log().logger.info(
                "[{}.length_less_or_equals]校验文本长度小于等于期望数值，验证成功：{}<={}".format(cls.__name__, real_value, expect_value)
            )
            allure.attach(
                body = "[{}.length_less_or_equals]校验文本长度小于等于期望数值，验证成功：{}<={}".format(cls.__name__, real_value, expect_value),
                name= "length_less_or_equals", attachment_type=allure.attachment_type.TEXT  
                )   
        except Exception as e:
            Log().logger.error(
                "[{}.length_less_or_equals]校验文本长度小于等于期望数值，验证失败：{}<={}".format(cls.__name__, real_value, expect_value)
            )
            allure.attach(
                body="[{}.length_less_or_equals]校验文本长度小于等于期望数值，验证失败：{}<={}".format(cls.__name__, real_value, expect_value),
                name= "length_less_or_equals", attachment_type=allure.attachment_type.TEXT  
                )       
            raise e

    @classmethod
    def contains(cls, real_value: Any, expect_value: Any, message: Text = ""):
        try:
            assert isinstance(
                real_value, (list, tuple, dict, str, bytes)
            ), "expect_value should be list/tuple/dict/str/bytes type"
            assert expect_value in real_value, message
            Log().logger.info(
                "[{}.contains]校验实际结果中包含期望结果，验证成功：{} in {}".format(cls.__name__, real_value, expect_value)
            )
            allure.attach(
                body = "[{}.contains]校验实际结果中包含期望结果，验证成功：{} in {}".format(cls.__name__, real_value, expect_value),
                name= "contains", attachment_type=allure.attachment_type.TEXT  
                )   
        except Exception as e:
            Log().logger.error(
                "[{}.contains]校验实际结果中包含期望结果，验证失败：{} in {}".format(cls.__name__, real_value, expect_value)
            )
            allure.attach(
                body="[{}.contains]校验实际结果中包含期望结果，验证失败：{} in {}".format(cls.__name__, real_value, expect_value),
                name= "contains", attachment_type=allure.attachment_type.TEXT  
                )       
            raise e

    @classmethod
    def contained_by(cls, real_value: Any, expect_value: Any, message: Text = ""):
        try:
            assert isinstance(
                expect_value, (list, tuple, dict, str, bytes)
            ), "expect_value should be list/tuple/dict/str/bytes type"
            assert real_value in expect_value, message
            Log().logger.info(
                "[{}.contained_by]校验期望结果中包含实际结果，验证成功：{} in {}".format(cls.__name__, real_value, expect_value)
            )
            allure.attach(
                body = "[{}.contained_by]校验期望结果中包含实际结果，验证成功：{} in {}".format(cls.__name__, real_value, expect_value),
                name= "contained_by", attachment_type=allure.attachment_type.TEXT  
                )   
        except Exception as e:
            Log().logger.error(
                "[{}.contained_by]校验期望结果中包含实际结果，验证失败：{} in {}".format(cls.__name__, real_value, expect_value)
            )
            allure.attach(
                body="[{}.contained_by]校验期望结果中包含实际结果，验证失败：{} in {}".format(cls.__name__, real_value, expect_value),
                name= "contained_by", attachment_type=allure.attachment_type.TEXT  
                )   
            raise e

    @classmethod
    def type_match(cls, real_value: Any, expect_value: Any, message: Text = ""):
        def get_type(name):
            if isinstance(name, type):
                return name
            elif isinstance(name, str):
                try:
                    return __builtins__[name]  # noqa
                except KeyError:
                    raise ValueError(name)
            else:
                raise ValueError(name)
        try:
            if expect_value in ["None", "NoneType", None]:
                assert real_value is None, message
            else:
                assert type(real_value) == get_type(expect_value), message
            Log().logger.info(
                "[{}.type_match]校验期望结果与实际结果数据类型相同，验证成功：{} in {}".format(cls.__name__, real_value, expect_value)
            )
            allure.attach(
                body = "[{}.type_match]校验期望结果与实际结果数据类型相同，验证成功：{} in {}".format(cls.__name__, real_value, expect_value),
                name= "type_match", attachment_type=allure.attachment_type.TEXT  
                )   
        except Exception as e:
            Log().logger.error(
                "[{}.type_match]校验期望结果与实际结果数据类型相同，验证失败：{} in {}".format(cls.__name__, real_value, expect_value)
            )
            allure.attach(
                body="[{}.type_match]校验期望结果与实际结果数据类型相同，验证失败：{} in {}".format(cls.__name__, real_value, expect_value),
                name= "type_match", attachment_type=allure.attachment_type.TEXT  
                )   
            raise e

    @classmethod
    def regex_match(cls, real_value: Text, expect_value: Any, message: Text = ""):
        try:
            assert isinstance(expect_value, str), "expect_value should be Text type"
            assert isinstance(real_value, str), "real_value should be Text type"
            assert re.match(expect_value, real_value), message
            Log().logger.info(
                "[{}.regex_match]校验正则匹配实际结果中的值成功，验证成功：{} in {}".format(cls.__name__, real_value, expect_value)
            )
            allure.attach(
                body = "[{}.regex_match]校验正则匹配实际结果中的值成功，验证成功：{} in {}".format(cls.__name__, real_value, expect_value),
                name= "regex_match", attachment_type=allure.attachment_type.TEXT  
                )   
        except Exception as e:
            Log().logger.error(
                "[{}.regex_match]校验正则匹配实际结果中的值成功，验证失败：{} in {}".format(cls.__name__, real_value, expect_value)
            )
            allure.attach(
                body="[{}.regex_match]校验正则匹配实际结果中的值成功，验证失败：{} in {}".format(cls.__name__, real_value, expect_value),
                name= "regex_match", attachment_type=allure.attachment_type.TEXT  
                )       
            raise e

    @classmethod
    def startswith(cls, real_value: Any, expect_value: Any, message: Text = ""):
        try:
            assert str(real_value).startswith(str(expect_value)), message
            Log().logger.info(
                "[{}.startswith]校验实际结果的开头为期望结果，验证成功：{} in {}".format(cls.__name__, real_value, expect_value)
            )
            allure.attach(
                body = "[{}.startswith]校验实际结果的开头为期望结果，验证成功：{} in {}".format(cls.__name__, real_value, expect_value),
                name= "startswith", attachment_type=allure.attachment_type.TEXT  
                )   
        except Exception as e:
            Log().logger.error(
                "[{}.startswith]校验实际结果的开头为期望结果，验证失败：{} in {}".format(cls.__name__, real_value, expect_value)
            )
            allure.attach(
                body="[{}.startswith]校验实际结果的开头为期望结果，验证失败：{} in {}".format(cls.__name__, real_value, expect_value),
                name= "startswith", attachment_type=allure.attachment_type.TEXT  
                )       
            raise e

    @classmethod
    def endswith(cls, real_value: Text, expect_value: Any, message: Text = ""):
        try:
            assert str(real_value).endswith(str(expect_value)), message
            Log().logger.info(
                "[{}.endswith]校验实际结果的结尾为期望结果，验证成功：{} in {}".format(cls.__name__, real_value, expect_value)
            )
            allure.attach(
                body = "[{}.endswith]校验实际结果的结尾为期望结果，验证成功：{} in {}".format(cls.__name__, real_value, expect_value),
                name= "endswith", attachment_type=allure.attachment_type.TEXT  
                )   
        except Exception as e:
            Log().logger.error(
                "[{}.endswith]校验实际结果的结尾为期望结果，验证失败：{} in {}".format(cls.__name__, real_value, expect_value)
            )
            allure.attach(
                body="[{}.endswith]校验实际结果的结尾为期望结果，验证失败：{} in {}".format(cls.__name__, real_value, expect_value),
                name= "endswith", attachment_type=allure.attachment_type.TEXT  
                )   
            raise e
