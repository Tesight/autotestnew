import os
from common.comdata import CommonData
from common.utils.u_picture import get_capture_screenshot,get_base64_image_string
from common.logger import Log
import matplotlib.pyplot as plt
from matplotlib import font_manager as fm
import allure



class ChartsAction(object):
    """图表工具类"""

    @classmethod
    def add_line_chart(cls,x:list,y: list,title: str,x_label: str,y_label: str):
        try:
            file_name = title+'_plot.png'
            file_path = os.path.join(CommonData.get_project_data_path(),'picture',file_name)
            if type(x) == str:
                x = eval(x)
            if type(y) == str:
                y = eval(y)
            font = fm.FontProperties(fname=CommonData.FONT_PATH)  
            # # matplotlib.rcParams["font.family"] = [CommonData.FONT_PATH] 
            plt.plot(x,y)
            plt.title(title,fontproperties=font) 
            plt.xlabel(x_label,fontproperties=font)
            plt.ylabel(y_label,fontproperties=font)
            # plt.plot(x,y)
            # plt.title(title,) 
            # plt.xlabel(x_label,)
            # plt.ylabel(y_label,)
            plt.savefig(file_path)  
            Log().logger.info(
                    "[{}.add_line_chart]绘制折线图：{} 成功".format(cls.__name__, title,)
                )
        except Exception as e:
            Log().logger.error(
                    "[{}.add_line_chart]绘制折线图：{} 失败，信息：{}".format(cls.__name__, title,e)
                )
        config_data = CommonData.get_config_data()  
        img = get_base64_image_string(file_path)  
        if config_data['项目运行设置']['report_type'] == 'html' and img:
            if file_name:
                html_text = '<div><img src="{}" alt="screenshot" ' \
                                'style="width:600px;height:100%;" ' \
                                'onclick="lookimg(this.src)" align="right"/></div>'.format(img)  # noqa
                # extra.append(pytest_html.extras.html(html_text))
        elif config_data['项目运行设置']['report_type'] == 'allure' and img:
            allure.attach.file(file_path, "折线图", allure.attachment_type.PNG)
    
    @classmethod
    def add_multi_line_chart(cls,x:list,y: list,title: str,x_label: str,y_label: str): 
        try:
            file_name = title+'_plot.png'
            file_path = os.path.join(CommonData.get_project_data_path(),'picture',file_name)
            if type(x) == str:
                x = eval(x)
            if type(y) == str:
                y = eval(y)
            font = fm.FontProperties(fname=CommonData.FONT_PATH)  
            # matplotlib.rcParams["font.family"] = [CommonData.FONT_PATH] 
            for i in y:
                plt.plot(x,i)
            plt.title(title,fontproperties=font) 
            plt.xlabel(x_label,fontproperties=font)
            plt.ylabel(y_label,fontproperties=font)
            # plt.title(title) 
            # plt.xlabel(x_label)
            # plt.ylabel(y_label)
            plt.savefig(file_path)  
            Log().logger.info(
                    "[{}.add_multi_line_chart]绘制折线图：{} 成功".format(cls.__name__, title,)
                )
        except Exception as e:
            Log().logger.error( 
                    "[{}.add_multi_line_chart]绘制折线图：{} 失败，信息：{}".format(cls.__name__, title,e)
                )   
        config_data = CommonData.get_config_data()  
        img = get_base64_image_string(file_path)  
        if config_data['项目运行设置']['report_type'] == 'html' and img:
            if file_name:
                html_text = '<div><img src="{}" alt="screenshot" ' \
                                'style="width:600px;height:100%;" ' \
                                'onclick="lookimg(this.src)" align="right"/></div>'.format(img)  # noqa
                # extra.append(pytest_html.extras.html(html_text))
        elif config_data['项目运行设置']['report_type'] == 'allure' and img:
            allure.attach.file(file_path, "折线图", allure.attachment_type.PNG)         
         
        

if __name__ == "__main__":
    pass
