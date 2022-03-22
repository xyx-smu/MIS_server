from datetime import datetime

from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    # 数据有效状态
    DATA_STATUS_TUPLE = (('1', "有效"), ('0', "失效"))

    real_name = models.CharField(max_length=50, verbose_name="真实姓名", help_text='真实姓名')
    phone = models.CharField(max_length=20, verbose_name='联系电话', help_text="联系电话")
    data_status = models.CharField(max_length=2, choices=DATA_STATUS_TUPLE, default='1', verbose_name='数据状态',
                                   help_text="数据状态")

    def save(self, *args, **kwargs):
        self.password = make_password(self.password, None, 'pbkdf2_sha256')
        super(User, self).save(*args, **kwargs)

    class Meta:
        verbose_name = "用户信息表"
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.username


class EmailVerifyRecord(models.Model):
    # 验证码
    code = models.CharField(max_length=20, verbose_name="邮箱验证码")
    email = models.EmailField(max_length=50, verbose_name="邮箱")
    user_id = models.ForeignKey(User, max_length=20, verbose_name="用户编号", on_delete=models.DO_NOTHING)
    send_time = models.DateTimeField(verbose_name="发送时间", auto_now=True)

    class Meta:
        verbose_name = "邮箱验证码"
        verbose_name_plural = verbose_name

    def __str__(self):
        return '{0}({1})'.format(self.code, self.email)
