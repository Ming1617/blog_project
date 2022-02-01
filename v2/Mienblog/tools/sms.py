
#发短信业务
import base64
import datetime
import hashlib
import json

import requests #发http/https

class YunTongXin():
    base_url='https://app.cloopen.com:8883'

    def __init__(self,accountSid,accountToken,appId,templateId):
        self.accountSid=accountSid  #账户ID
        self.accountToken=accountToken  #账户令牌
        self.appId=appId    #应用id
        self.templateId=templateId  #模板id

    def get_request_url(self,sig):
        #/2013-12-26/Accounts/{accountSid}/SMS/{funcdes}?sig={SigParameter}
        self.url=self.base_url+'/2013-12-26/Accounts/%s/SMS/TemplateSMS?sig=%s'%(self.accountSid,sig)
        return self.url

    def get_timestamp(self):
        """
        生成一个时间戳
        :return:
        """
        return datetime.datetime.now().strftime('%Y%m%d%H%M%S')

    def get_sig(self,timestamp):
        #生成业务url中的sig
        s=self.accountSid+self.accountToken+timestamp
        m=hashlib.md5()
        m.update(s.encode())
        return m.hexdigest().upper()    #转为全大写

    def get_request_header(self,timstamp):
        #生成请求头
        s=self.accountSid+':'+timstamp
        auth=base64.b64encode(s.encode()).decode()
        return {
            'Accept':'application/json',
            'Content-Type':'application/json;charset=utf-8',
            'Authorization':auth
        }

    def get_request_body(self,phone,code):
        """
        构造请求包体
        :param phone:
        :param code:
        :return:
        """
        return {
            'to':phone,
            'appId':self.appId,
            'templateId':self.templateId,
            'datas':[code,'3']
        }

    def request_api(self,url,header,body):
        res=requests.post(url,headers=header,data=body)
        return res.text

    def run(self,phone,code):
        #获取时间戳
        timestamp=self.get_timestamp()
        #生产签名
        sig=self.get_sig(timestamp)
        #生成业务url
        url=self.get_request_url(sig)
        # print(url)
        header=self.get_request_header(timestamp)
        # print(header)
        #生成请求体
        body=self.get_request_body(phone,code)
        #发请求
        data=self.request_api(url,header,json.dumps(body))
        return data

if __name__=='__main__':
    #accountSid,accountToken,appId,templateId
    config={
        'accountSid':'8a216da87e7baef8017ea9a09e7d0686',
        'accountToken':'13bbea33f6434dd29e7caff134bd9c93',
        'appId':'8a216da87e7baef8017ea9a09fc6068d',
        'templateId':'1'
    }

    yun=YunTongXin(**config)
    print(yun.run('15225726710','123456'))