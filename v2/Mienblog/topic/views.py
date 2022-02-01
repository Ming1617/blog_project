import json

from django.http import JsonResponse
from django.shortcuts import render
from django.views import View
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.core.cache import cache
from tools.logging_dec import logging_check,get_user_by_request
from tools.cache_dec import cache_set
from .models import Topic
from user.models import UserProfile
from message.models import Message

# Create your views here.

#异常码  10300--10399

class TopicViews(View):

    def clear_topics_caches(self,request):
        '''
            删除缓存（发表文章/删除文章，清除缓存）
        :param request:
        :return:
        '''
        path=request.path_info
        cache_key_p=['topics_cache_self_','topics_cache_']
        cache_key_h=['','?category=tec','?category=no-tec']
        all_keys=[]
        for key_p in cache_key_p:
            for key_h in cache_key_h:
                all_keys.append(key_p+path+key_h)
        cache.delete_many(all_keys)


    def make_topic_res(self,author,author_topic,is_self):
        '''单个文章详情返回'''
        if is_self:
            #博主访问自己
            next_topic=Topic.objects.filter(id__gt=author_topic.id,author=author).first()
            last_topic=Topic.objects.filter(id__lt=author_topic.id,author=author).last()
        else:
            next_topic = Topic.objects.filter(id__gt=author_topic.id, author=author,limit='public').first()
            last_topic = Topic.objects.filter(id__lt=author_topic.id, author=author,limit='public').last()

        next_id=next_topic.id if next_topic else None
        next_title=next_topic.title if next_topic else ''
        last_id = last_topic.id if last_topic else None
        last_title = last_topic.title if last_topic else ''

        #关联留言和回复
        all_messages=Message.objects.filter(topic=author_topic).order_by('-created_time')
        msg_list=[]
        rep_dic={}
        m_count=0
        for msg in all_messages:
            if msg.parent_message:
                #回复
                rep_dic.setdefault(msg.parent_message,[])
                rep_dic[msg.parent_message].append({'msg_id':msg.id,'publisher':msg.publisher.nickname,
                                                    'publisher_avatr':str(msg.publisher.avatar),'content':msg.content,
                                                    'created_time':msg.created_time.strftime('%Y-%m-%d %H:%M:%S')})
            else:
                #留言
                m_count+=1
                msg_list.append({'id':msg.id,'publisher':msg.publisher.nickname,
                                                    'publisher_avatr':str(msg.publisher.avatar),'content':msg.content,
                                                    'created_time':msg.created_time.strftime('%Y-%m-%d %H:%M:%S'),'reply':[]})
        for m in msg_list:
            if m['id'] in rep_dic:
                m['reply']=rep_dic[m['id']]

        res={'code':200,'data':{}}
        res['data']['nickname']= author.nickname
        res['data']['title']=author_topic.title
        res['data']['category']=author_topic.category
        res['data']['created_time']=author_topic.created_time.strftime('%Y-%m-%d %H:%M:%S')
        res['data']['content']=author_topic.content
        res['data']['introduce']=author_topic.introduce
        res['data']['author']=author.nickname
        res['data']['last_id']=last_id
        res['data']['last_title']=last_title
        res['data']['next_id']=next_id
        res['data']['next_title']=next_title
        res['data']['messages']=msg_list
        res['data']['messages_count']=m_count
        return res

    def make_topics_res(self,author,author_topics):
        '''
            拼接列表返回
        '''

        res={'code':200,'data':{}}
        topic_res=[]
        for topic in author_topics:
            d={}
            d['id']=topic.id
            d['title']=topic.title
            d['category']=topic.category
            d['created_time']=topic.created_time.strftime('%Y-%m-%d %H:%M:%S')
            d['introduce']=topic.introduce
            d['author']=author.nickname
            topic_res.append(d)
        res['data']['topics']=topic_res
        res['data']['nickname']=author.nickname
        return res

    @method_decorator(logging_check)
    def post(self,request,author_id):
        '''
                {"content":"<p>222<br></p>","content_text":"222",
                "limit":"public","title":"11","category":"tec"}
        '''
        author=request.myuser
        #取出前端数据
        json_str=request.body
        json_obj=json.loads(json_str)
        title=json_obj['title']

        #解决xss注入
        import html
        # 进行转义
        title = html.escape(title)
        if len(title)>50:
            result={'code':10308,'error':'title is long'}
            return JsonResponse(result)
        if not title:
            result = {'code': 10309, 'error': 'Please give me title'}
            return JsonResponse(result)
        content = json_obj.get('content')
        if not content:
            result = {'code': 10310, 'error': 'Please give me content'}
            return JsonResponse(result)
        content_text=json_obj['content_text']
        if not content_text:
            result={'code':10311,'error':'Please give me content_text'}
            return JsonResponse(result)

        introduce=content_text[:30]
        limit=json_obj['limit']
        category=json_obj['category']
        if limit not in ['public','private']:
            result={'code':10300,'error':'The limit error'}
            return JsonResponse(result)
        if category not in ['tec','no-tec']:
            result = {'code': 10301, 'error': 'The category error'}
            return JsonResponse(result)
        #创建topic数据
        Topic.objects.create(title=title,content=content,limit=limit,category=category,
                             introduce=introduce,author=author)
        #删除缓存
        self.clear_topics_caches(request)
        return JsonResponse({'code':200})

    @method_decorator(cache_set(60))
    def get(self,request,author_id):
        print('-----view--in-----')
        #/v2/topics/jcm
        #访问者  visitor
        #当前被访问博客的博主 author
        try:
            author=UserProfile.objects.get(username=author_id)
        except Exception as e:
            result={'code':10302,'error':'The author is not existed'}
            return JsonResponse(result)

        visitor=get_user_by_request(request)
        visitor_username=None
        if visitor:
            visitor_username=visitor.username


        t_id=request.GET.get('t_id')
        if t_id:
            #/v2/topocs/jcm?t_id=1
            #获取指定文章数据
            t_id=int(t_id)
            is_self=False
            if visitor_username==author_id:
                is_self=True
                #博主访问自己文章的详情页
                try:
                    author_topic=Topic.objects.get(id=t_id,author_id=author_id)
                except Exception as e:
                    result={'code':10303,'error':'No topic'}
                    return JsonResponse(result)
            else:
                try:
                    author_topic = Topic.objects.get(id=t_id, author_id=author_id,limit='public')
                except Exception as e:
                    result = {'code': 10304, 'error': 'No topic'}
                    return JsonResponse(result)
            res=self.make_topic_res(author,author_topic,is_self)
            return JsonResponse(res)



        else:
            #获取列表页数据
            # /v2/topics/jcm
            # /v2/topics/jcm?category=[tec|no-tec]
            category=request.GET.get('category')
            if category in ['tec','no-tec']:
                if visitor_username==author_id:
                    #博主访问自己博客
                    author_topics=Topic.objects.filter(author_id=author_id,category=category)
                else:
                    author_topics=Topic.objects.filter(author_id=author_id,limit='public',category=category)
            else:
                if visitor_username == author_id:
                    # 博主访问自己博客
                    author_topics = Topic.objects.filter(author_id=author_id)
                else:
                    author_topics = Topic.objects.filter(author_id=author_id, limit='public')

            res=self.make_topics_res(author,author_topics)
            return JsonResponse(res)


    @method_decorator(logging_check)
    def delete(self,request,author_id):
        # 博主删除自己的文章
        # /v2/topics/<author_id>
        # token存储的用户
        author=request.myuser
        token_author_id = author.username
        # url中传过来的author_id 必须与token中的用户名相等
        if author_id != token_author_id:
            result = {'code': 10305, 'error': 'You can not do it'}
            return JsonResponse(result)

        topic_id = request.GET.get('t_id')

        try:
            topic = Topic.objects.get(id=topic_id)
        except:
            result = {'code': 10306, 'error': 'You can not do it!'}
            return JsonResponse(result)
        # 删除
        if topic.author.username != author_id:
            result = {'code': 10307, 'error': 'You can not do it!!'}
            return JsonResponse(result)
        topic.delete()
        # 删除缓存
        self.clear_topics_caches(request)
        res = {'code': 200}
        return JsonResponse(res)

