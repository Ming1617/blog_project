import json

from django.http import JsonResponse
from django.shortcuts import render
from tools.login_check import login_check
from topic.models import Topic
from message.models import Message

# Create your views here.
@login_check('POST')
def messages(request,topic_id):

    if request.method !='POST':
        result={'code':401,'error':'Please use POST'}
        return JsonResponse(result)

    #发表留言/回复
    #获取用户
    user=request.user
    json_str=request.body
    #load回python obj
    json_obj=json.loads(json_str)
    content=json_obj.get('content')
    if not content:
        result={'code':402,'error':'Please give me content'}
        return JsonResponse(result)
    parent_id=json_obj.get('parent_id',0)

    try:
        topic=Topic.objects.get(id=topic_id)
    except:
        #topic 被删除 or 当前topic_id 不真实
        result={'code':403,'error':'No No topic!'}
        return JsonResponse(result)

    #私有博客 只能 博主留言
    if topic.limit=='private':
        #检查身份
        if user.username!=topic.author.username:
            result={'code':404,'error':'Please get out!'}
            return JsonResponse(result)

    #创建数据
    Message.objects.create(content=content,publisher=user,
                           topic=topic,parent_message=parent_id)
    return JsonResponse({'code':200,'data':{}})
