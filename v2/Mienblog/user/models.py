import random

from django.db import models

# Create your models here.

def default_sign():
    signs=['来吧，兄弟','奔跑吧兄弟','暂未想好']
    return random.choice(signs)


class UserProfile(models.Model):

    username=models.CharField(max_length=11,verbose_name='用户名',primary_key=True)
    nickname=models.CharField(max_length=30,verbose_name='昵称')
    password=models.CharField(max_length=32)
    email=models.EmailField()
    phone=models.CharField(max_length=11)
    avatar=models.ImageField(upload_to='avatar',null=True)
    sign=models.CharField(max_length=50,verbose_name='个人签名',default=default_sign)
    info=models.CharField(max_length=150,verbose_name='个人简介',default='')
    created_time=models.DateTimeField(auto_now_add=True)
    upadate_tome=models.DateTimeField(auto_now=True)

    class Meta:
        db_table='user_user_profile'