## Mien博客

#### **前后端分离流程图**

![请求流程【分离】](image/请求流程【分离】.jpg)

**1.后端环境**

**Python3.6 + django2.2.12 + mysql8.0.26 + Ubuntu + vim+redis**

**2.通信协议**

**http**

**3.通信格式**

**json**

**API设计一定程度的遵循了RESTful设计风格**

**4状态码**

**返回结构如{ ' code ' ：200， ' data ' ：{}， ' error ' : ' xxx ' }**

**1、创建Django项目为Mienblog**

`django-admin startproject Mienblog`

**2、进入mysql数据库-创建mysql数据库为Mienblog**

`create database Mienblog default charset utf8;`

**3、配置settings.py**

​	1）注释 MIDDLEWARE 中的  'django.middleware.csrf.CsrfViewMiddleware',

```python
2）DATABASES = {
'default': {
    'ENGINE': 'django.db.backends.mysql',
    'NAME': 'Mienblog',#数据库名字
    'USER':'root',#用户
    'PASSWORD':'17',#密码
    'HOST':'127.0.0.1',
    'PORT':'3306'#端口号
}
}
```
3）配置时区

```python
LANGUAGE_CODE = 'zh-Hans'

TIME_ZONE = 'Asia/Shanghai'

USE_TZ=False  #不用django的时区功能  与当前时间保持一致
```

**4、配置cors**

1）、INSTALLED_APPS 中添加 corsheaders

2）、MIDDLEWARE 中添加 corsheaders.middleware.CorsMiddleware
		   位置尽量靠前，官方建议 ‘django.middleware.common.CommonMiddleware’ 上方

3）、CORS_ORIGIN_ALLOW_ALL  布尔值  如果为True 白名单不启用

​			正式环境应为false与4相结合使用

4）、白名单

```python
			CORS_ORIGIN_WHITELIST =[
			"https://example.com"
		]
```

5）、预检请求

```python
 CORS_ALLOW_METHODS = (
				'DELETE',
				'GET',
				'OPTIONS',
				'PATCH',
				'POST',
				'PUT',
				)
```

6)、遇见请求请求头

```python
 CORS_ALLOW_HEADERS = (
				'accept-encoding',
				'authorization',
				'content-type',
				'dnt',
				'origin',
				'user-agent',
				'x-csrftoken',
				'x-requested-with',
			)
```

7）、请求缓存时间

​		CORS_PREFLIGHT_MAX_AGE  默认 86400s

8）、特殊响应头

​		`CORS_EXPOSE_HEADERS=[]`

9）、是否要跨域的cookie

​		CORS_ALLOW_CREDENTIALS  布尔值， 默认False

7/8/9不用配置

10)、#上传设置

```
MEDIA_URL='/media/' 
MEDIA_ROOT=os.path.join(BASE_DIR,'media') 
```

​			在项目文件夹下创建文件夹’media‘

​			在Mienblog/urls.py

			from django.conf.urls.static import static
			from django.conf import settings									 			urlpatterns+=static(settings.MEDIA_URL,document_root=settings.MEDIA_ROOT)




### 用户模块

#### **数据库结构：**

| 字段名       | 类型         | 作用     | 备注1                        | 备注2 |
| ------------ | ------------ | -------- | ---------------------------- | ----- |
| username     | varchar(11)  | 用户名   | 注册时填写的用户名，不可修改 | 主键  |
| nickname     | varchar(30)  | 昵称     | 在博客中显示的名字，可修改   | 无    |
| email        | varchar(50)  | 邮箱     | 预留                         | 无    |
| phone        | varchar(11)  | 手机号   | 无                           | 无    |
| password     | varchar(32)  | 密码     | 用户密码，已散列存储         | 无    |
| sign         | varchar(50)  | 个人签名 | 无                           | 无    |
| info         | varchar(150) | 个人描述 | 无                           | 无    |
| avatar       | varchar(100) | 头像     | 无                           | 无    |
| created_time | datetime     | 创建时间 | 无                           | 无    |
| updated_time | datetime     | 更新时间 | 无                           | 无    |

**1、创建用户模块**

创建用户应用python3 manage.py startapp user

注册app：早settings.py的INSTALLED_APPS中添加   'user',

user/models.py

```python
class UserProfile(models.Model):

    username=models.CharField(max_length=11,verbose_name='用户名',primary_key=True)
    nickname=models.CharField(max_length=30,verbose_name='昵称')
    password=models.CharField(max_length=32)
    email=models.EmailField()
    phone=models.CharField(max_length=11)
    avatar=models.ImageField(upload_to='avatar',null=True)
    sign=models.CharField(max_length=50,verbose_name='个人签名',default='')
    info=models.CharField(max_length=150,verbose_name='个人简介',default='')
    created_time=models.DateTimeField(auto_now_add=True)
    upadate_tome=models.DateTimeField(auto_now=True)

    class Meta:
        db_table='user_user_profile'
```

**迁移数据库**

```shell
python3 manage.py makemigrations   #生成当前模型类的迁移文件

python3 manage.py migrate

```

### **用户状态验证**

**JWT - json-web-token**

json-web-token（JWT）是为了在网络应用环境建传递声明而执行的一种基于JSON的开放标准，JWT的声明一般被用来在身份提供者和服务提供者间传递被**认证的用户身份信息**，以便从资源服务器获取资源

#### 三大组成部分

1，header

​		格式为字典-元数据格式如下

```python
{'alg':'HS256', 'typ':'JWT'}
#alg代表要使用的 算法
#typ表明该token的类别 - 此处必须为 大写的 JWT
```

​		 该部分数据需要转成json串并用base64 加密

​	2，payload

​		格式为字典-此部分分为公有声明和私有声明

  	  公共声明：JWT提供了内置关键字用于描述常见的问题

此部分均为**可选项**，用户根据自己需求 按需添加key，常见公共声明如下：

```python
{'exp':xxx, # Expiration Time 此token的过期时间的时间戳
 'iss':xxx，# (Issuer) Claim 指明此token的签发者
 'aud':xxx, #(Audience) Claim 指明此token的
 'iat':xxx, # (Issued At) Claim 指明此创建时间的时间戳
 'aud':xxx, # (Audience) Claim	指明此token签发面向群体
}
```

​		私有声明：用户可根据自己业务需求，添加自定义的key，例如如下：

```python
{'username': 'guoxiaonao'}
```

​		公共声明和私有声明均在同一个字典中；转成json串并用base64加密

​	3，signature 签名

​		签名规则如下：

​		根据header中的alg确定 具体算法，以下用 HS256为例

​		HS256(自定义的key ,   base64后的header + '.' + base64后的payload)

​        解释：用自定义的key, 对base64后的header + '.' + base64后的payload进行hmac计算

#### 校验jwt规则

​		1，解析header, 确认alg

​		2，签名校验 - 根据传过来的header和payload按 alg指明的算法进行签名，将签名结果和传过来的sign进行对比，若对比一致，则校验通过

​		3，获取payload自定义内容

​		**pip3 install pyjwt==1.7.1**

```python
#生成

In [2]: S=jwt.encode({'username':'jcm'},'123456',algorithm='HS256
   ...: ')

In [3]: S
Out[3]: b'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2VybmFtZSI6ImpjbSJ9.NDI73Vv2pUv2i_AYqTzgl9Ucx1Gc3gT__rBhld1aH2E'

#解出用户名                    
In [4]: jwt.decode(S,'123456')
Out[4]: {'username': 'jcm'}

```

**特殊说明**

若encode得时候 payload中添加了exp字段; 则exp字段得值需为 当前时间戳+此token得有效期时间， 例如希望token 300秒后过期  {'exp': time.time() + 300};  在执行decode时，若检查到exp字段，且token过期，则抛出jwt.ExpiredSignatureError

```python
S=jwt.encode({'username':'jcm','exp':time.time()+3},'123456',algorithm='HS256')
```

#### 前后端分离场景下 使用JWT

原则

​		1、JWT签发后，交由浏览器保存

​		2、浏览器可将其存储在‘本地存储’中

​		3、需要用户登录才能使用的功能，前端ajax中需要将jwt传至后端；可放在请求头中发送

#### 前后端分离token流程图

![前后端分离token](image/前后端分离token.jpg)

### 发短信业务

第三方短信平台

发短信业务–需要接入其他平台【第三方平台】，让短信平台帮助我们发送短信，该服务通常为有偿服务

容联云：https://www.yuntongxun.com/

文档：https://doc.yuntongxun.com/p/5a533de33b8496dd00dce07c

验证码功能流程

1、前端页面点击“免费获取验证码”，发送Ajax请求到后端

2、后端接到请求后

​		1、生成随机验证码

​		2、存储验证码

​			安装`django-redis  sudo pip3 install django-redis`

​			settings.py并配置

```python
CACHES = {
    "default": {
            "BACKEND": "django_redis.cache.RedisCache",
            "LOCATION": "redis://127.0.0.1:6379",
            "OPTIONS": {
                "CLIENT_CLASS": "django_redis.client.DefaultClient",
            }
        }
}

```

​		3、发送验证码

3、注册时，需要提交验证码，并在注册逻辑中对比验证码是否正确

### Celery

Celery是一个简单、灵活且可靠的，处理大量消息的分布式系统它是一个专注于实时处理的任务队列，同时也支持任务调度（生产者消费者模型）

中文官网: http://docs.jinkan.org/docs/celeryl

在线安装 sudo pip3 install Celery

名词解释

broker -消息传输的中间件，生产者一旦有消息发送，将发至broker; 【RQ,redis】

backend -用于存储消息/任务结果，如果需要跟踪和查询任务状态，则需添加要配置相关

worker -工作者–消费/执行broker中消息/任务的进程

![celery_img](image/celery_img.png)

判断当前业务是否使用生产者消费者模型（Celery）

1、是否当前阶段会有阻塞（有阻塞可以用）

2、实时反馈不能用

**使用 - 创建woker**

```python
from celery import Celery
app=Celery('jcm',broker='redis://:password@127.0.0.1:6379/1')#有密码
#app=Celery('jcm',broker='redis://:@127.0.0.1:6379/1')#没密码

#创建任务函数
@app.task
def task_test():
    print('task is running....')
```

**使用 - 启动woker**

#Ubuntu终端中，tasks.py文件同级目录下执行

```shell
celery -A tasks worker --loglevel=info
```

此模式默认为前台启动，终端中会输出相关日志

**使用 - 创建生产者 - 推送任务**

在tasks.py文件的同级目录进入ipython3执行 如下代码

```python
from tasks import task_test
task_test.delay()
```

执行完毕后，观察worker的日志

**使用 - 存储执行结果**

Celery提供存储任务执行结果的方案，需借助redis或 mysql或Memcached等

```python
from celery import Celery
app=Celery('demo',
				broker='redis://@127.0.0.1:6379/1',
				backend='redis://@127.0.0.1:6379/2',)

```

#创建任务函数

```python
@app.task
def task_test(a,b):
    print('task is running....')
    return a+b
```

**django中使用celery**

1,创建celery配置文件
				项目同名目录下创建celery.py（跟settings.py同级）

2,应用下创建tasks.py集中定义对应worker函数

3,视图函数充当生产者，推送具体worker函数

4.项目目录下启动worker

​				celery -A项目同名目录名worker -l info

**正式环境后台启动celery**

`nohup celery -A proj worker -P gevent -c 1000 > celery.log2>&1&`
#1, nohup:忽略所有挂断(SIGHUP)信号
#2，标准输入是文件描述符0。它是命令的输入，缺省是键盘，也可以是文件或其他命令的输出。
#标准输出是文件描述符1。它是命令的输出，缺省是屏幕
也可以
是文件。
#标准错误是文件描述符2。这是命令错误的输出，缺省是屏幕，同样也可以是文件。
#3，&符号:代表将命令在后台执行

### 文章系统

#### 数据库结构

| 字段名       | 类型            | 作用         | 备注1                               | 备注2 |
| ------------ | --------------- | ------------ | ----------------------------------- | ----- |
| id           | int             | 主键自增     | 无                                  | 无    |
| title        | varchar(50)     | 文章主题     | 无                                  | 无    |
| category     | varchar(20)     | 博客的分类   | 1，tec 技术类型2，no-tec 非技术类型 | 无    |
| limit        | varchar(10)     | 权限         | 1，public- 公开2，private-私有      | 无    |
| introduce    | varchar(90)     | 博客简介     | 博客内容的前三十个字符              | 无    |
| content      | text            | 博客内容     | 无                                  | 无    |
| created_time | datetime        | 博客创建时间 | 无                                  | 无    |
| updated_time | datetime        | 博客修改时间 | 无                                  | 无    |
| author       | UserProfile外键 | 无           | 无                                  | 无    |

创建app    	`python3 manage.py startapp topic`

注册app    

topic/models.py

```python
class Topic(models.Model):

    title=models.CharField(max_length=50,verbose_name='文章标题')
    category=models.CharField(max_length=20,verbose_name='文章分类')
    limit=models.CharField(max_length=20,verbose_name='文章权限')
    introduce=models.CharField(max_length=90,verbose_name='文章简介')
    content=models.TextField(verbose_name='文章内容')
    created_time=models.DateTimeField(auto_now_add=True)
    updated_time=models.DateTimeField(auto_now=True)
    author=models.ForeignKey(UserProfile,on_delete=models.CASCADE)
```

解决标题xxs注入攻击

```python
#解决xss注入
import html
进行转义
title = html.escape(title)
```

上一篇文章&&&下一篇文章

sql语句实现

```sql
博主访问自己当前文章id 1 next

select  * from topic where topic.id > 1 and topic.author=jcm order by topic.id ASC limit 1
```

```mysql
博主访问自己当前文章id 4 last
select * from topic where topic.id < 4 and topic.author=jcm order by topic.id DESC limit 1
```

python  ORM实现

```python
#下一篇
next_topic=Topic.objects.filter(id__gt=author_topic.id,author=author).first()
#上一篇
last_topic=Topic.objects.filter(id__lt=author_topic.id,author=author).last()
```

#### 缓存问题

文章列表页

缓存 - 把高频读取的数据，放置到更快的存储介质里

缓存方案1

​			cache_page（过期时间s）:django提供，直接用装饰器方法放在整个请求方法上面

​						优点：简单

​						缺点：1、无法按照具体的访客身份，进行针对性的存储，例如存储的是博主访问自身博客的数据，访客到访时可能会读取到博主触发的缓存

​									2、删除缓存成本过高【出现新旧数据不一致】

缓存方案2 

​				局部-cache.set/get等方法

​						优点：灵活，存储成本最优，删除成本低

​						缺点：代码实现成本较高

​						案例：

​									模型类中定义classmethod

```python
class Topic
	@classmethod
	def get_topic_list(cls，)：
    	if cache:
            return cache
        data=cls.objects.filter()
        #cache in
        return data
```

缓存方案3

​					自己设计

### 留言系统

数据库结构

| 字段名         | 类型        | 作用                                       | 备注1            | 备注2 |
| -------------- | ----------- | ------------------------------------------ | ---------------- | ----- |
| id             | int         | 主键自增                                   | 无               | 无    |
| content        | varchar(50) | 留言内容                                   | 无               | 无    |
| created_time   | date        | 留言创建时间                               | 无               | 无    |
| parent_message | int         | 该留言的父留言，此ID若存在证明该留言为回复 | int              | 无    |
| publisher_id   | varchar(10) | 留言的发布者                               | user_profile外键 | 无    |
| topic_id       | varchar(10) | 文章                                       | topic 外键       | 无    |

创建message应用

message/models.py

```python
from django.db import models
from user.models import UserProfile
from topic.models import Topic
# Create your models here.
class Message(models.Model):
    content=models.CharField(max_length=50)
    created_time=models.DateTimeField(auto_now_add=True)
    parent_message=models.IntegerField(verbose_name='回复的留言id')
    publisher=models.ForeignKey(UserProfile,on_delete=models.CASCADE)
    topic=models.ForeignKey(Topic,on_delete=models.CASCADE)
    
```

