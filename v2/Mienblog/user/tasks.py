from django.conf import settings
from Mienblog.celery import app
from tools.sms import YunTongXin

@app.task
def send_sms_c(phone,code):
    # accountSid,accountToken,appId,templateId
    yun = YunTongXin(**settings.SMS_CONFIG)
    res=yun.run(phone, code)
    return res