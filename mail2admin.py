import smtplib
from email.header import Header
from email.mime.text import MIMEText

#发送邮件函数
def sendmail(tolist,subject,message):
    try:
        server = smtplib.SMTP_SSL("smtp.qq.com",465)
        server.login("","")
        msg = MIMEText('<html><body><h1>用户自检结果报告：</h1>' +
            '<p>%s</a></p>'%message +
            '</body></html>', 'html', 'utf-8')
        msg["Subject"] = Header(subject,"utf-8")
        msg["from"] = "335320567@qq.com"#发送人

        msg["to"] = ";".join(tolist)
        #tolist = msg["to"].split(";")
        server.sendmail(msg["from"],tolist,msg.as_string())
        #self.server.set_debuglevel(1)
        return None,"[Done]"
    except:
        return None,"[Error]:邮件发送失败"

if __name__ == "__main__":
    print(sendmail("test","aaa"))
