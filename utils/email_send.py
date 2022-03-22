from datetime import datetime
from random import Random  # 用于生成随机码
from django.core.mail import send_mail  # 发送邮件模块

from app import models
from MIS_server.settings import EMAIL_FROM  # setting.py添加的的配置信息


# 生成随机字符串
def random_str(randomlength=10):
    str = ''
    chars = '0123456789'
    length = len(chars) - 1
    random = Random()
    for i in range(randomlength):
        str += chars[random.randint(0, length)]
    return str


def send_email(email):
    user = models.User.objects.filter(email=email).first()
    code = random_str(8)
    curr_email = models.EmailVerifyRecord.objects.filter(email=email)
    if curr_email.exists():
        curr_email.update(code=code, send_time=datetime.now())
    else:
        models.EmailVerifyRecord.objects.create(code=code, email=email, user_id=user)
    email_title = "验证账户"
    html_message = '<p>你好，%s：</p>' \
                   '<p>有人尝试更改你的帐户密码。</p>' \
                   '<p>如果是你本人操作，请使用以下验证码验证身份：</p>' \
                   '<h4>%s</h4>' \
                   '<p>如果这不是你本人，请不要泄露验证码给他人，保护帐户安全。</p>' % (user, code)
    # 发送邮件
    send_status = send_mail(subject=email_title, from_email=EMAIL_FROM, recipient_list=[email], message='',
                            html_message=html_message)
    if send_status:
        pass
