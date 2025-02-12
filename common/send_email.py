from datetime import datetime
import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from common.comdata import CommonData
from common.utils.u_compress import make_zip


class HandleEmail:

    def __init__(self):
        config = CommonData.get_config_data()
        email_config = config['邮件发送配置']
        self.host = email_config['host']
        self.port = int(email_config['port'])
        self.sender = email_config['sender']
        self.send_email = email_config['send_email']
        self.receiver = eval(email_config['receiver'])
        self.pwd = email_config['pwd']
        self.subject = email_config['subject']

    @staticmethod
    def add_text(content):
        """添加文本"""
        return MIMEText(content, "plain", "utf-8")

    @staticmethod
    def add_html_text(html):
        """添加html文本"""
        return MIMEText(html, "html", "utf-8")

    @staticmethod
    def add_accessory(filepath):
        """添加附件,图片，txt,pdf,zip"""
        rb_file = open(filepath, "rb").read()
        res = MIMEText(rb_file, "base64", "utf-8")
        res.add_header('Content-Disposition', 'attachment', filename=os.path.basename(filepath))
        return res

    def add_subject_attach(self, attach_info: tuple, send_date=None):
        """添加主题 发件人，收件人
        @param attach_info: 构建附件元组
        @param send_date: 发送日期，"%Y-%m-%d %H:%M:%S"，当为None时用当前时间发送邮件
        @return: msg 可以传给 send_email(）方法发送邮件
        """
        msg = MIMEMultipart('mixed')
        msg['Subject'] = self.subject
        # msg['From'] = '{0} <{1}>'.format(datas["send_email"][send_email][0], send_email)
        msg['From'] = '{0} <{1}>'.format(self.sender, self.send_email)
        msg['To'] = ";".join(self.receiver)
        if send_date:
            msg['Date'] = send_date
        else:
            msg['Date'] = datetime.strftime(datetime.now(), "%Y-%m-%d %H:%M:%S")
        if isinstance(attach_info, tuple):
            for i in attach_info:
                msg.attach(i)
        return msg

    def send_email_oper(self, msg):
        """发送邮件"""
        smtp = None
        try:
            smtp = smtplib.SMTP(self.host, port=self.port)
            smtp.login(self.send_email, self.pwd)
            smtp.sendmail(self.send_email, self.receiver, msg.as_string())
            print("{0}给{1}发送邮件成功,发送时间:{2}".format(self.send_email, self.receiver,
                                                  datetime.strftime(datetime.now(), "%Y-%m-%d %H:%M:%S")))
        except:
            smtp = smtplib.SMTP_SSL(self.host, port=self.port)
            smtp.login(self.send_email, self.pwd)
            smtp.sendmail(self.send_email, self.receiver, msg.as_string())
            print("{0}给{1}发送邮件成功,发送时间:{2}".format(self.send_email, self.receiver,
                                                  datetime.strftime(datetime.now(), "%Y-%m-%d %H:%M:%S")))
        finally:
            smtp.quit()

    def send_public_email(self, send_date=None, content="", hmtl="", filetype='html'):
        attach_info = []
        text_plain = self.add_text(content)
        attach_info.append(text_plain)
        if hmtl:
            text_html = self.add_html_text(hmtl)
            attach_info.append(text_html)
        elif filetype == 'allure':
            allure_zip = make_zip(CommonData.get_allure_report_path(), os.path.join(CommonData.get_allure_report_path(),
                                                                                    'allure.zip'))
            file_attach = self.add_accessory(filepath=allure_zip)
            attach_info.append(file_attach)
        elif filetype == 'html':
            file_attach = self.add_accessory(filepath=os.path.join(CommonData.get_html_path(),
                                                                   'auto_reports.html'))
            attach_info.append(file_attach)
        elif filetype == 'xml':
            file_attach = self.add_accessory(filepath=os.path.join(CommonData.get_xml_path(),
                                                                   'auto_reports.xml'))
            attach_info.append(file_attach)
        # 构建附件元组
        attach_info = tuple(attach_info)
        # 添加主题和附件信息到msg
        msg = self.add_subject_attach(attach_info=attach_info, send_date=send_date)
        # 发送邮件
        self.send_email_oper(msg)


if __name__ == '__main__':
    text = '本邮件由系统自动发出，无需回复！\n各位同事，大家好，以下为本次测试报告!'
    HandleEmail().send_public_email(send_date=None, content=text, hmtl="", filetype='html')
