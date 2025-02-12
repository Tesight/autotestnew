import xlrd
import xlwt


class ExcelRead:

    def __init__(self, excel_path, sheet_name="Sheet1"):
        self.data = xlrd.open_workbook(excel_path)
        self.table = self.data.sheet_by_name(sheet_name)
        # 获取第一行为key值
        self.keys = self.table.row_values(0)
        # 获取总行数
        self.rowNum = self.table.nrows
        # 获取总列数
        self.colNum = self.table.ncols

    def dict_date(self):
        if self.rowNum <= 1:
            print("总行数小于1")
        else:
            r = []
            j = 1
            for i in range(self.rowNum - 1):
                s = {}
                # 从第二行取对应的values值
                values = self.table.row_values(j)
                for x in range(self.colNum):
                    value_data = values[x]
                    if type(value_data) == float:
                        if int(str(value_data).split('.')[1]) == 0:
                            value_data = int(value_data)
                    elif type(value_data) == str:
                        try:
                            if value_data.isdigit():
                                value_data = eval(value_data)    
                            elif value_data.startswith('[') and value_data.endswith(']'):
                                value_data = eval(value_data)
                            elif value_data.startswith('{') and value_data.endswith('}'):
                                value_data = eval(value_data)   
                        except NameError:
                            pass
                    s[self.keys[x]] = value_data
                r.append(s)
                j += 1
            return r

    def get_row_data(self, row):
        """获取exl中行信息,row--行数（int）"""
        if row <= 1:
            row_data = None
        else:
            test_dates = self.dict_date()
            row_data = test_dates[row - 2]
        return row_data

    def get_col_data(self, name):
        """获取exl中列信息"""
        name_data = []
        test_dates = self.dict_date()
        for t_data in test_dates:
            name_data.append(t_data[name])
        return name_data

    def get_cell_data(self, row, name):
        """获取exl中某一单元格信息，row--行数（int）；name--列名(char)"""
        if row <= 1:
            row_data = None
        else:
            test_dates = self.dict_date()
            row_data = test_dates[row - 2][name]
        return row_data


class ExcelWrite:

    def __init__(self, sheet_name="Sheet1"):
        self.workbook = xlwt.Workbook(encoding='utf-8')
        # 获取工作表对象Worksheet
        self.worksheet = self.workbook.add_sheet(sheet_name)

    def set_header(self, list_data):
        if not isinstance(list_data, list):
            raise TypeError("数据必须是列表")
        keys_data = list(list_data[0].keys())
        num = len(keys_data)
        for c in range(num):
            self.worksheet.write(0, c, label=keys_data[c])

    def excl_write(self, list_data, excel_path):
        """表格写入全部数据"""
        if not isinstance(list_data, list):
            raise TypeError("数据必须是列表")
        # 获取每行列表
        self.set_header(list_data)
        rows_num = len(list_data)
        for r in range(rows_num):
            values_data = list(list_data[r].values())
            cows_num = len(values_data)
            for c in range(cows_num):
                self.worksheet.write(r + 1, c, values_data[c])
        # 保存数据到硬盘
        self.workbook.save(excel_path)


if __name__ == "__main__":
    # Data = ExcelWrite()
    # filepath = r"./excelFile.xls"
    # l = [{'姓名': '张三', '年龄': 18, '职业': '学生'},
    #      {'姓名': '李四', '年龄': 19, '职业': '学生'},
    #      {'姓名': '王五', '年龄': 20, '职业': '学生'}]
    # Data.excl_write(l, filepath)
    path = r'C:\Users\Administrator\Desktop\auto\data\download\1590883213892.xls'
    data = ExcelRead(path, 'Sheet1')
    col = data.get_col_data('服务器名称')
    print(col)
