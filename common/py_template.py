import jinja2

# case_data,class_name,case_name,auto_type,case_config
TEST_CLASS_TEMPLATE = jinja2.Template('''\
import pytest
import allure
from common.comdata import CommonData
from common.container import LocalManager
from common.parser import YamlKwParser


@allure.feature('{{ cls_info }}')
class {{ cls_name }}:
    """{{ cls_info }}"""
    
    {%- for case_item in testcases %}

    @allure.story('{{ case_item.case_name }}')
    @allure.description('{{ case_item.case_info[0].params.title }}')

    {%- for item in case_item.case_config %}

    {%- if item.policy == 'skip' and item.params.flag %}
    @pytest.mark.skip(reason='{{ item.params.reason }}')
    {%- endif %}

    {%- if item.policy == 'mark' and item.params.flag %}
    {%- for name in  item.params.markname.split(';') %}
    @pytest.mark.mark.{{ name }}
    {%- endfor %}
    {%- endif %}

    {%- if item.policy == 'usefixtures' and item.params.flag %}
    @pytest.mark.usefixtures(*{{ item.params.fixtures.split(';') }})
    {%- endif %}

    {%- if item.policy == 'parametrize' and item.params.flag %}
    @pytest.mark.parametrize('case_driver', CommonData.get_data_driver('{{ item.params.filename }}', '{{ item.params.sheetname }}'))
    def {{ case_item.case_name }}(self, case_driver):
    {%- elif item.policy == 'parametrize' and not item.params.flag %}
    def {{ case_item.case_name }}(self):
    {%- endif %}
    {%- endfor %}
        """{{ case_item.case_info[0].params.title }}"""
        {%- for item in case_item.case_config %}
        {%- if item.policy == 'parametrize' and item.params.flag %}
        LocalManager.set_value('DataDriver', case_driver)
        {%- endif %}
        {%- endfor %}
        YamlKwParser.parse([
            {% for case_step in case_item.case_step %}
            {{ case_step }},
            {% endfor %}
        ])
    
    {%- endfor %}
''')

# case_data,case_name,auto_type,case_config
TEST_FUNCTION_TEMPLATE = jinja2.Template('''\
import pytest
import allure
from common.comdata import CommonData
from common.container import LocalManager
from common.parser import YamlKwParser


@allure.story('{{ func_name }}')
@allure.description('{{ func_info[0].params.title }}')

{%- for item in func_config %}

{%- if item.policy == 'skip' and item.params.flag %}
@pytest.mark.skip(reason='{{ item.params.reason }}')
{%- endif %}

{%- if item.policy == 'mark' and item.params.flag %}
{%- for name in item.params.markname.split(';') %}
@pytest.mark.mark.{{ name }}
{%- endfor %}
{%- endif %}

{%- if item.policy == 'usefixtures' and item.params.flag %}
@pytest.mark.usefixtures(*{{ item.params.fixtures.split(';') }})
{%- endif %}

{%- if item.policy == 'parametrize' and item.params.flag %}
@pytest.mark.parametrize('case_driver', CommonData.get_data_driver('{{ item.params.filename }}', '{{ item.params.sheetname }}'))
def {{ func_name }}(case_driver):
{%- elif item.policy == 'parametrize' and not item.params.flag %}
def {{ func_name }}():
{%- endif %}
{%- endfor %}
    """{{ func_info[0].params.title }}"""
    {%- for item in func_config %}
    {%- if item.policy == 'parametrize' and item.params.flag %}
    LocalManager.set_value('DataDriver', case_driver)
    {%- endif %}
    {%- endfor %}
    YamlKwParser.parse([
        {% for case_step in func_step %}
        {{ case_step }},
        {% endfor %}
    ])
''')

# fixture_data,auto_type
FIXTURE_TEMPLATE = jinja2.Template('''\
import pytest
from common.parser import YamlKwParser

{% for key, value in fixture_data.items() recursive %}
{%- if value.params %}
@pytest.fixture(**{{value.params}})
{%- else %}
@pytest.fixture()
{%- endif %}
def {{ key }}():
    YamlKwParser.parse({{value.setup}})
    yield
    YamlKwParser.parse({{value.teardown}})
{% endfor %}
''')

#仿真轨迹模板，静态点
FIX_TEMPLATE = jinja2.Template('''
step:
- action: VariableAction
  method: set_variable
  desc: 轨迹参数_生成控制命令json
  params:
    name: data
    value:
      longitude: {{ longitude }}
      latitude: {{ latitude }}
      altitude: {{ altitude }}
      customizedPath: 
      - type: {{type}}
        timeStep: {{timeStep}}
        directionMatrix:
        - {{x}}
        - {{y}}
        initialVelocity: {{ initialVelocity }}
        finalVelocity: {{finalVelocity}}
        accelerationDistance: {{accelerationDistance}}
        travelTime: {{travelTime}}
- action: HttpAction
  method: request
  desc: 模拟器参数_发送控制命令,返回json
  params:
    method: post
    url: /customized/trajectory
    headers: null
    params: null
    data: null
    json: 'data'
    result_json: result_json
''')


#仿真轨迹模板，圆形轨迹
CIRCLE_TEMPLATE = jinja2.Template('''
step:
- action: VariableAction
  method: set_variable
  desc: 轨迹参数_生成控制命令json
  params:
    name: data
    value:
      longitude: {{ longitude }}
      latitude: {{ latitude }}
      altitude: {{ altitude }}
      customizedPath: 
      - type: {{type}}
        timeStep: {{timeStep}}
        directionMatrix:
        - {{x}}
        - {{y}}
        initialVelocity: {{ initialVelocity }}
        finalVelocity: {{finalVelocity}}
        accelerationDistance: {{accelerationDistance}}
        travelTime: {{travelTime}}
        radius: {{ radius }}
- action: HttpAction
  method: request
  desc: 模拟器参数_发送控制命令,返回json
  params:
    method: post
    url: /customized/trajectory
    headers: null
    params: null
    data: null
    json: 'data'
    result_json: result_json
''')

#仿真轨迹模板，匀速直线轨迹
STRAIGHT_LINE_TEMPLATE = jinja2.Template('''
step:
- action: VariableAction
  method: set_variable
  desc: 轨迹参数_生成控制命令json
  params:
    name: data
    value:
      longitude: {{ longitude }}
      latitude: {{ latitude }}
      altitude: {{ altitude }}
      customizedPath: 
      - type: {{ type }}
        timeStep: {{ timeStep }}
        directionMatrix:
        - {{ x }}
        - {{ y }}
        initialVelocity: {{ initialVelocity }}
        finalVelocity: {{ finalVelocity }}
        accelerationDistance: {{accelerationDistance}}
        travelTime: {{travelTime}}
- action: HttpAction
  method: request
  desc: 模拟器参数_发送控制命令,返回json
  params:
    method: post
    url: /customized/trajectory
    headers: null
    params: null
    data: null
    json: 'data'
    result_json: result_json
''')


#仿真轨迹模板，匀加速直线轨迹
STRAIGHT_HASTEN_LINE_TEMPLATE = jinja2.Template('''
step:
- action: VariableAction
  method: set_variable
  desc: 轨迹参数_生成控制命令json
  params:
    name: data
    value:
      longitude: {{ longitude }}
      latitude: {{ latitude }}
      altitude: {{ altitude }}
      customizedPath: 
      - type: {{ type }}
        timeStep: {{ timeStep }}
        directionMatrix:
        - {{ x }}
        - {{ y }}
        initialVelocity: {{ initialVelocity }}
        finalVelocity: {{ finalVelocity }}
        accelerationDistance: {{accelerationDistance}}
        travelTime: {{travelTime}}
- action: HttpAction
  method: request
  desc: 模拟器参数_发送控制命令,返回json
  params:
    method: post
    url: /customized/trajectory
    headers: null
    params: null
    data: null
    json: 'data'
    result_json: result_json
''')


#仿真轨迹模板，矩形动态轨迹
RECTANGLE_LINE_TEMPLATE = jinja2.Template('''
step:
- action: VariableAction
  method: set_variable
  desc: 轨迹参数_生成控制命令json
  params:
    name: data
    value:
      longitude: {{ longitude }}
      latitude: {{ latitude }}
      altitude: {{ altitude }}
      customizedPath: 
      - type: {{ type }}
        timeStep: {{ timeStep }}
        directionMatrix:
        - {{ x }}
        - {{ y }}
        initialVelocity: {{ initialVelocity }}
        finalVelocity: {{ finalVelocity }}
        accelerationDistance: {{accelerationDistance}}
        travelTime: {{travelTime}}
        width: {{ width }}
        length: {{ length }}
        rotationDirection: {{ rotationDirection }}
        turnRadius: {{ turnRadius }}
- action: HttpAction
  method: request
  desc: 模拟器参数_发送控制命令,返回json
  params:
    method: post
    url: /customized/trajectory
    headers: null
    params: null
    data: null
    json: 'data'
    result_json: result_json
''')