import yaml
from pathlib import Path
from fpdf import FPDF
from datetime import datetime
from contextlib import contextmanager
import imghdr

class PDF(FPDF):
    def __init__(self):
        super().__init__()
        self.add_font('OPPOSans', '', 'C:/baidunetdiskdownload/clean_production/autotestnew/font/OPPOSans-B.ttf', uni=True)
        self.logo_path = 'C:/baidunetdiskdownload/clean_production/autotestnew/logo/favicon.png'  # 默认 logo 路径

    def header(self):
        # 设置页面宽度
        page_width = self.w
        
        # 设置字体和标题
        self.set_font('OPPOSans', '', 16)
        title = '自动化测试报告'
        title_width = self.get_string_width(title)
        
        # 固定 logo 尺寸
        logo_width = 13
        logo_height = 13
        
        # 计算标题居中位置（不包含logo宽度）
        center_without_logo = page_width / 2
        title_x = center_without_logo - title_width / 2
        
        # 绘制标题
        self.set_x(title_x)
        self.cell(title_width, 10, title, 0, 0, 'C')  # 不换行
        
        # 在标题右侧放置logo
        logo_x = title_x + title_width + 50  # 标题右侧5mm处
        
        try:
            if hasattr(self, 'logo_path') and Path(self.logo_path).exists():
                self.image(self.logo_path, x=logo_x, y=8, w=logo_width, h=logo_height)
        except Exception as e:
            print(f"无法加载logo: {e}")
        
        self.ln(30)  # 添加足够的空间
    
    def footer(self):
        self.set_y(-15)
        self.set_font('OPPOSans', '', 8)
        self.cell(0, 10, f'第 {self.page_no()} 页', 0, 0, 'C')

@contextmanager
def text_color(pdf, r, g, b):
    #original = pdf.text_color
    pdf.set_text_color(r, g, b)
    yield
    pdf.set_text_color(r,b,g)

def yaml_to_pdf(yaml_file_path, pdf_file_path=None, logo_path=None):
    try:
        yaml_path = Path(yaml_file_path)
        if not yaml_path.exists():
            raise FileNotFoundError(f"YAML文件 {yaml_file_path} 不存在")
        
        with open(yaml_path, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
        
        pdf = PDF()
        if logo_path:
            # 检查是否是有效的图像类型
            img_type = imghdr.what(logo_path)
            if img_type in ['png', 'jpeg', 'jpg', 'gif','ico']:
                pdf.logo_path = logo_path
            else:
                print(f"警告: 忽略不支持的图像格式: {logo_path} (类型: {img_type})")
    
        pdf.add_page()
        pdf.set_font('OPPOSans', '', 12)

                # 提取测试基本信息
        if data and isinstance(data[0], dict) and '测试基本信息' in data[0]:
            test_info = data[0]['测试基本信息']
            test_id = test_info.get('测试编号', 'N/A')
            test_time = test_info.get('测试时间', 'N/A')
            test_person = test_info.get('测试人', 'N/A')
            test_temp = test_info.get('环境温度', 'N/A')
            test_humidity = test_info.get('环境湿度', 'N/A')
            test_notes = test_info.get('备注', 'N/A')
            
            # 显示基本信息
            pdf.cell(0, 10, f'测试编号: {test_id}', 0, 0, 'L')
            pdf.cell(0, 10, f'测试时间: {test_time}', 0, 1, 'R')
            pdf.cell(0, 10, f'测试人员: {test_person}', 0, 0, 'L')
            pdf.cell(0, 10, f'环境温度: {test_temp}  环境湿度: {test_humidity}', 0, 1, 'R')
            pdf.cell(0, 10, f'备注: {test_notes}', 0, 1, 'L')

        pdf.ln(10)  # 添加10毫米的垂直空间作为空行
        # 定义列宽和行高（确保是数字）
        col_widths = [50, 50, 50, 40]
        row_height = 15
        
        # 生成表头
        pdf.set_fill_color(200, 220, 255)
        pdf.cell(col_widths[0], row_height, '测试项', 1, 0, 'C', 1)
        pdf.cell(col_widths[1], row_height, '测试数据', 1, 0, 'C', 1)
        pdf.cell(col_widths[2], row_height, '标准值', 1, 0, 'C', 1)
        pdf.cell(col_widths[3], row_height, '结果', 1, 1, 'C', 1)
        
        # 填充表格内容 - 从测试项目列表中获取数据
        test_items = []
        if data and isinstance(data[0], dict) and '测试项目列表' in data[0]:
            test_items = data[0]['测试项目列表']
        elif data and all(isinstance(item, dict) and '测试项目' in item for item in data):
            test_items = data  # 如果顶层就是测试项目列表
            
        for item in test_items:
            result = item.get('测试结果', 'FAIL')
            color = (0, 128, 0) if result == 'PASS' else (255, 0, 0)
            
            # 前三列使用默认黑色
            pdf.set_text_color(0, 0, 0)  # 确保使用黑色
            pdf.cell(col_widths[0], row_height, str(item.get('测试项目', 'N/A')), 1, 0, 'C')
            pdf.cell(col_widths[1], row_height, str(item.get('测试数据', 'N/A')), 1, 0, 'C')
            pdf.cell(col_widths[2], row_height, str(item.get('标准要求值', 'N/A')), 1, 0, 'C')
            
            # 只对结果列应用颜色
            with text_color(pdf, *color):
                pdf.cell(col_widths[3], row_height, str(result), 1, 1, 'C')
        
        # 输出 PDF 文件
        output_path = pdf_file_path if pdf_file_path else yaml_path.with_suffix('.pdf')
        pdf.output(output_path)
        return output_path
    
    except Exception as e:
        print(f"错误: {str(e)}")
        return None

if __name__ == "__main__":
    yaml_file = "C:/baidunetdiskdownload/clean_production/autotestnew/lib/测试报告.yaml"
    logo_path = "C:/baidunetdiskdownload/clean_production/autotestnew/logo/favicon.png"
    pdf_path = yaml_to_pdf(yaml_file,logo_path=logo_path)
    if pdf_path:
        print(f"PDF 文件已生成: {pdf_path}")
    else:
        print("PDF 生成失败")