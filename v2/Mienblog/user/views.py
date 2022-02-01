import json

from django.conf import settings
from django.http import JsonResponse
from django.shortcuts import render
from django.utils.decorators import method_decorator
from django.views import View
from .models import UserProfile
import hashlib
from tools.logging_dec import logging_check
import random
from django.core.cache import cache
from tools.sms import YunTongXin
from .tasks import send_sms_c

# Create your views here.

#异常码 10100 - 10199

#django提供了一个装饰器 method_decorator , 可以将函数的装饰器转换成方法装饰器

#FBV
@logging_check
def users_views(request,username):
    if request.method!='POST':
        result={'code':10103,'error':'Please use POST'}
        return JsonResponse(result)
    user=request.myuser

    avatar=request.FILES['avatar']
    user.avatar=avatar
    user.save()
    return JsonResponse({'code':200})



#CBV
#更灵活[可继承]
#对未定义的http method请求返回405相应
class UserViews(View):

    def get(self,request,username=None):
        if username:
            # /v2/user/jcm
            try:
                user=UserProfile.objects.get(username=username)
            except Exception as e:
                result={'code':10102,"error":'The username is wrong'}
                return JsonResponse(result)
            result={'code':200,'username':username,'data':{
                'info':user.info,'sign':user.sign,'nickname':user.nickname,'avatar':str(user.avatar)
            }}
            return JsonResponse(result)
        else:
            # /v2/users
            pass


        return JsonResponse({'code':200,'msg':'test'})

    def post(self,request):

        json_str=request.body
        json_obj=json.loads(json_str)
        username=json_obj['username']
        email=json_obj['email']
        password_1=json_obj['password_1']
        password_2=json_obj['password_2']
        phone=json_obj['phone']
        sms_num=int(json_obj['sms_num'])

        #参数的基本检查
        if password_1 !=password_2:
            result={'code':10100,'error':'The password is not same'}
            return JsonResponse(result)

        #验证码检查
        old_code=cache.get('sms_%s'%(phone))
        if not  old_code:
            result={'code':10110,'error':'The code is wrong'}
            return JsonResponse(result)
        if sms_num!=old_code:
            result= {'code':10111,'error':'The code is wrong'}
            return JsonResponse(result)


        #检查用户名是否可用
        old_user=UserProfile.objects.filter(username=username)
        if old_user:
            result={'code':10101,'error':'The username is already existed'}
            return JsonResponse(result)
        #YserProfile插入数据（密码md5存储）
        p_m=hashlib.md5()
        p_m.update(password_1.encode())
        UserProfile.objects.create(username=username,nickname=username,
                                    password=p_m.hexdigest(),email=email,phone=phone)

        result={'code':200,'username':username,'data':{}}

        return JsonResponse(result)

    @method_decorator(logging_check)
    def put(self,request,username=None):
        #更新用户数据（昵称，个人签名，个人描述）
        json_str=request.body
        json_obj=json.loads(json_str)

        user=request.myuser

        user.sign=json_obj['sign']
        user.info=json_obj['info']
        user.nickname=json_obj['nickname']

        user.save()
        return JsonResponse({'code':200})

def sms_view(request):
    if request.method!='POST':
        result={'code':10108,'error':'Please use POST'}
        return JsonResponse(result)

    json_str=request.body
    json_obj=json.loads(json_str)
    phone=json_obj['phone']
    #生成随机码
    code=random.randint(1000,9999)
    #存储随机码 django-redis
    cache_key='sms_%s'%(phone)
    #检查是否已经有发过的且未过期的验证码
    old_code=cache.get(cache_key)
    if old_code:
        return JsonResponse({'code':10111,'error':'The sms is send repeatedly'})
    cache.set(cache_key,code,180)
    #发送随机码-->短信
    send_str=send_sms_c.delay(phone,code)
    return JsonResponse({'code': 200})

# def send_sms(phone,code):
#     # accountSid,accountToken,appId,templateId
#     yun = YunTongXin(**settings.SMS_CONFIG)
#     res=yun.run(phone, code)
#     return res