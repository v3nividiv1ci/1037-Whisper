import smtplib
from email.mime.text import MIMEText
from email.header import Header
import config


# def send_email(email, v_code):
def send_email(email, v_code):
    # 邮件内容
    mail_msg = """
        <p>是来自1037-Whisper的问好呀！这是你的验证码，</p>
        """ + v_code + """
        ，<p>请于817s之内填写喔，</p><p>填晚了那位大人可是会不高兴的</p>
        """
    message = MIMEText(mail_msg, "html", "utf-8")
    # 发件人&&收件人名字（当然是hibana啦口亨
    message["From"] = Header(config.sender, "utf-8")
    message["To"] = Header(config.receiver, "utf-8")
    # 邮件标题
    subject = "来自 1037-Whisper 的验证邮件"
    message["Subject"] = Header(subject, "utf-8")
    # 发送方&&接收方 我真的记不住自己qq，，，
    sender = config.qq_mail
    receiver = [email]
    # 根据pop3服务发邮件
    smtpObj = smtplib.SMTP_SSL("smtp.qq.com", 465)
    smtpObj.login(sender, config.AuthorizationCode)
    smtpObj.sendmail(sender, receiver, message.as_string())
    smtpObj.quit()
    # "email successfully sent! >< plz check it in 3 minutes"


