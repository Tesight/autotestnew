from common.keywords.check.check_base import CheckAction
from common.keywords.client.client_base import TemplateClientAction, Yolov5ClientAction
from common.keywords.handler.db_base import DbAction
from common.keywords.handler.dict_base import DictAction
from common.keywords.handler.file_base import FileAction
from common.keywords.handler.json_base import JsonAction
from common.keywords.handler.linux_base import LinuxAction
from common.keywords.handler.list_base import ListAction
from common.keywords.handler.str_base import StrAction
from common.keywords.handler.time_base import TimeAction
from common.keywords.handler.variable_base import VariableAction
from common.keywords.handler.windows_base import WindowsAction
from common.keywords.http.http_base import HttpAction
from common.keywords.web.web_base import WebAction
from common.keywords.report.report_base import ReportAction 
from common.keywords.charts.charts_base import ChartsAction

INIT_ACTION_MAPS = {
    "HttpAction": HttpAction,
    "WebAction": WebAction,
    "TemplateClientAction": TemplateClientAction,
    "Yolov5ClientAction": Yolov5ClientAction,  # noqa
    "CheckAction": CheckAction,
    "DbAction": DbAction,
    "DictAction": DictAction,
    "JsonAction": JsonAction,
    "LinuxAction": LinuxAction,
    "ListAction": ListAction,
    "StrAction": StrAction,
    "TimeAction": TimeAction,
    "VariableAction": VariableAction,
    "WindowsAction": WindowsAction,
    "FileAction": FileAction,
    "ReportAction":ReportAction,
    "ChartsAction":ChartsAction
}
