from typing import Any
from typing import Dict, Text, Union
from typing import List
from pydantic import BaseModel, PydanticValueError, ValidationError, validator
from common.logger import Log


class YamlFormatError(PydanticValueError):
    """yaml格式异常报错"""
    code = 'YamlFormatError'
    msg_template = 'value is not found : "{wrong_value}"'


class ActionModel(BaseModel):
    """基础关键字数据模型"""
    action: Text
    method: Text
    desc: Text
    params: Dict[Text, Any] = {}


class FunctionModel(BaseModel):
    """方法关键字数据模型"""
    function: Text
    desc: Text
    params: Dict[Text, Any] = {}


class CaseInfoModel(BaseModel):
    """测试用例中用例信息数据格式"""
    desc: Text
    params: Dict[Text, Text] = {}


class CaseConfigModel(BaseModel):
    """测试用例中用例配置数据格式"""
    policy: Text
    flag: bool = False
    desc: Text
    params: Dict[Text, Any] = {}


class CaseBusinessModel(BaseModel):
    """测试用例中业务关键字数据格式"""
    business: Text
    desc: Text
    params: Dict[Text, Any] = {}


class TestCaseModel(BaseModel):
    """测试用例完整数据格式"""
    info: List[CaseInfoModel]
    config: List[CaseConfigModel]
    step: List[Union[ActionModel, FunctionModel, CaseBusinessModel]] = None

    @validator('step')
    def step_validator(cls, v):
        if v:
            if 'action' in v:
                for step in v:
                    if step.method == 'request':
                        if not step.params.get('method'):
                            raise YamlFormatError(wrong_value='method')
                        if not step.params.get('url'):
                            raise YamlFormatError(wrong_value='url')
            return v


class ConftestModel(BaseModel):
    """前后置数据格式"""
    desc: Text
    params: Dict[Text, Any] = {}
    setup: List[Union[ActionModel, FunctionModel, CaseBusinessModel]] = None
    teardown: List[Union[ActionModel, FunctionModel, CaseBusinessModel]] = None


def yaml_conftest_format(conftest_data, filepath):
    """对conftest.yaml数据进行格式验证"""
    if not isinstance(conftest_data, dict):
        raise TypeError('conftest.yaml\n文件数据格式必须为字典！')
    try:
        for fix in conftest_data.values():
            res = ConftestModel(**fix)
            return res.dict()
    except ValidationError as e:
        Log().logger.error('文件{}\n数据格式验证失败：{}'.format(filepath, e.json()))
        raise e


def yaml_testcase_format(case_data, filepath):
    """对测试用例数据进行格式验证"""
    if not isinstance(case_data, dict):
        raise TypeError('测试用例文件数据格式必须为字典！')
    try:
        res = TestCaseModel(**case_data)
        return res.dict()
    except ValidationError as e:
        Log().logger.error('文件{}数据格式验证失败：{}'.format(filepath, e.json()))
        raise e
