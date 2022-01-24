# blog_project
一个内部技术文档/内容 收录平台 ；wiki
##### 产品需求 -  做一个内部技术文档/内容 收录平台 ；wiki

前端 - web产品线   +  安卓  + ios 

后端 -  前后端分离 - django +python+mysql+flask


开发模式：企业主流-前后端分离

主体功能：

	1）用户功能

	2）文章功能
	
	3）留言功能
	
	4）回复功能
	
	5）支付功能（v2）

**1.后端环境**
**Python 3.7.3  +  django 1.11.8  + mysql 5.5  +  Ubuntu19.04  +  vim**
**2.通信协议**
**http**
**3.通信格式**
**json**

问："你在新项目中遇到哪些困难/具体负责的内容"


答：我们的项目采用了前后端分离；针对http无状态的问题，我们采用了token的解决方案【jwt，base64加密了基础数据，通过hmac-SHA256签名[key]】;在自主研发jwt签发/校验
逻辑的过程中，我们发现b64转码结果中有很多‘=’占位符，严重影响了传输效率，加大了带宽成本【用户以及我们团队】，在这个问题上，我们调研了jwt官方的实现，发现jwt也
进行了相关优化，替换掉了b64结果中的‘=’【调研了b64实现原理，发现b64编码后总长度一定是4的倍数。。。。】，并很巧妙地在解析过程中，补全替换掉的‘=’；并且我们
在header上也进行了一些优化->将jwt header部分取消，减少冗余。以上成果得到了小组内全部认可

2.老板说SEO【搜索引擎优化】；我们初步的方案是根据搜索网站爬虫的user-agent返回纯静态【带内容文字】的页面，供其获取，但是这部分，可能晚辈细节把握不太到位，因为
分给了前端工程师去处理

3.csrf - token 一定程度上加大了csrf的难度

答：web版本的产品任务，我们遇到了跨域的问题；那我们调研了常规的跨域方案，script的src以及jquery的jsonp，cors；script的src实现成本高，只能发get请求；jsonp只是简化了
前端的工作，让后端成本未改变；也是只能发get请求；由于cors的灵活性【致辞各种http请求，且后端只需要进行一次通用配置，即可使用】。
PS：我们起初尝试django-cors，发现本地django版本被强制升级到了最新版本，原版本是1.11.8；此次意外升级，造成了项目有意外保存，，故我们高度统一了django版本，并且用
源码安装的方式进行django-cors安装


在URL设计上，我们也是参照了RESTful的设计规范：
	1.名词
	2.HTTP method 的语义
	3.接口版本问题 - v1v2。。。
	4.返回值-
		1.code的使用【httpresponse code/自定义code】
		2.数据的返回

#后端遇到问题：
1， cookie和session ，由于移动端的参与，我们决定采用token的方式保持会话；其中，我们调研了jwt的实现，并且基于jwt实现我们内部
优化了一个版本【自主研发token】; HS256 + {'exp':xxx,'username':xxx};

2, 改造jwt过程里，调研b64实现，发现了b64串结尾处的占位符问题，经过激烈的讨论，最终将占位符取消掉，在解密的时候，将占位符有效的补回来，从而降低传输成本；
最终得到公司高层一致的认可

3，token流程 ->   前端将用户名 密码 传至后端，后端校验成功后，签发token, 将token随此次响应返回给前端，前端接收到token后存储在浏览器本地存储中；
下次请求，前端将携带token访问后端；后端实时校验！

校验token的方式

v1 - 初级版
	`user.views.py`
	#视图函数 users
	`if request.method=='PUT':`
		#进行校验
		#取头 & decode & token中username
		#获取 user
		`pass`

v2 - 中极版
	封装方法，其他模块按需调用
	`def check_token(token):`

​		`return username`

v3 - 高级版
	装饰器/修饰器


我们在校验token的方式上采取了传参的装饰器并把需要校验http method当做参数传入负责校验的装饰器，并在
装饰器中将用户一并查出~赋值在request对象中，传入到视图函数！
为了满足RESTful api的灵活性，我们设计get方法的url上，支持按需查询【按查询字符串中指定的字段】；通过
hasattr进行反射，确定当前对象是否含有查询字符串中指定的属性【即确定了数据库中是否含有该字段】，当hasattr
（obj，‘属性’）返回True，则证明对象有该属性，即可调用getattr（obj，‘属性’）【注意，getattr取不到属性时会
抛出异常】

图片上传
`settings.py`
`MEDIA_URL='/media/'`
#媒体资源存放的服务器目录
`MEDIA_ROOT=os.path.join(BASE_DIR,'media/')`

主路由
`from django.conf.urls.static import static`
`from django.conf import settings`
`urlpatterns+=static(settings.MEDIA_URL,document_root=settings.MEDIA_ROOT)`

解决xss脚本注入攻击
1.转义
`a='<script>alert(1111)</script>'`
`import html`
`html.e`
`html.escape(a)  #转义`

答：xxs注入~产品上线一周后，我们发现内容列表出现xss注入的弹框，虽然是简单的恶作剧但是
让我们整体项目组对此事引起了高度的重视，随后，我们后端小组在所有涉及到用户提交的地方
都进行了相应的转义~解决了该隐患。
