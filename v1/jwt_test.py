import base64
import json
import time
import copy
import hmac

class Jwt():
    def __init__(self):
        pass

    @staticmethod
    def b64encode(content):
        return base64.urlsafe_b64encode(content).replace(b'=',b'')

    @staticmethod
    def b64decode(b):
        #如何把去掉的=号加回来，base64串有某种规律可以实现该需求
        #base64 长度能被4整除
        sem=len(b)%4
        if sem>0:
            b+=b'='*(4-sem)
        return base64.urlsafe_b64decode(b)

    @staticmethod
    def encode(payload,key,exp=300):

        #init header
        header={
            'typ':'JWT',
            'alg':'HS256'
        }
        header_json=json.dumps(header,separators=(',',':'),sort_keys=True)
        header_bs=Jwt.b64encode(header_json.encode())

        #init payload
        payload_self=copy.deepcopy(payload)
        if not isinstance(exp,int) and not isinstance(exp,str):
            raise TypeError('exp is must int or str')
        # print(type(payload_self))
        payload_self['exp']=time.time()+int(exp)
        payload_js=json.dumps(payload_self,separators=(',',':'),sort_keys=True)
        payload_bs=Jwt.b64encode(payload_js.encode())

        #init sign
        if isinstance(key,str):
            key=key.encode()
        hm=hmac.new(key,header_bs+b'.'+payload_bs,digestmod='SHA256')
        sign_bs=Jwt.b64encode(hm.digest())

        return header_bs+b'.'+payload_bs+b'.'+sign_bs

    @staticmethod
    def decode(token,key):
        #校验签名
        #检查exp是否过期
        #return payload部分的解码
        header_bs,payload_bs,sign_bs=token.split(b'.')
        #校验sign_bs
        if isinstance(key,str):
            key=key.encode()
        hm=hmac.new(key,header_bs+b'.'+payload_bs,digestmod='SHA256')
        #比对两次的sign结果
        # print(sign_bs)
        # print('//////')
        # print(Jwt.b64encode(hm.digest()))
        if sign_bs != Jwt.b64encode(hm.digest()):
            raise
        #检查是否过期
        payload_js=Jwt.b64decode(payload_bs)
        payload=json.loads(payload_js)

        if 'exp' in payload:
            now=time.time()
            print()
            if now >payload['exp']:
                raise
            return payload


if __name__=='__main__':
    token=Jwt.encode({'username':'admin'},'12345',300)
    print(token)

    print(Jwt.decode(token,'12345'))