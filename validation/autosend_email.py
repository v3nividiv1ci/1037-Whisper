import smtplib
from email.mime.text import MIMEText
from email.header import Header


# def send_email(email, v_code):
def send_email(email, v_code):
    # 邮件内容
    mail_msg = """
        <p>是来自1037-Whisper的问好呀！这是你的验证码，</p>
        """ + v_code + """
        ，<p>请于817s之内填写喔</p><p>时间正在1s1s地流逝呢，填晚了那位大人可是会不高兴的喔</p>
        """
    message = MIMEText(mail_msg, "html", "utf-8")
    # 发件人&&收件人名字（当然是hibana啦口亨
    message["From"] = Header("什么嘛你居然想知道我的名字", "utf-8")
    message["To"] = Header("Pure HUSTer", "utf-8")
    # 邮件标题
    subject = "来自 1037-Whisper 的验证邮件"
    message["Subject"] = Header(subject, "utf-8")
    # 发送方&&接收方 我真的记不住自己qq，，，
    sender = "什么嘛你居然想知道我的邮箱@whatever.com"
    receiver = [email]
    # 根据pop3服务发邮件
    smtpObj = smtplib.SMTP_SSL("smtp.qq.com", 465)
    smtpObj.login(sender, "什么嘛你居然想知道我的授权码")
    smtpObj.sendmail(sender, receiver, message.as_string())
    smtpObj.quit()
    return "email successfully sent! >< plz check it in 3 minutes"
