from QieGaoWorld import parameter
from django.http import HttpResponse
from django.shortcuts import render
from QieGaoWorld.views.decorator import check_post
from QieGaoWorld.views.decorator import check_login
from QieGaoWorld.views.dialog import dialog
from QieGaoWorld.models import CmsBook,CmsChapter
from QieGaoWorld import settings,common

from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
import os,traceback,uuid,logging,time,json,sys,requests
from PIL import Image
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.core.exceptions import MultipleObjectsReturned, ObjectDoesNotExist

def url(request, s):
    return eval(s)(request)

def login(request):
    username = str(request.POST.get("username", None))
    password = str(request.POST.get("password", None))
    

    with open(parameter.SPIGOT_PATH + "/plugins/WhiteList/config.yml", "r") as f:
        plays = f.read()
        if "- " + username.lower() not in plays:
            return HttpResponse(r_json(1, '您不在白名单'))
    with open(parameter.SPIGOT_PATH + "/banned-players.json", "rb") as f:
        plays = json.loads(f.read())
        s = "%"
        for b in plays:
            s += b['name'] + "%"
        if "%" + username + "%" in s:
            return HttpResponse(r_json('1',  '登录失败！您的帐号已被此服务器封禁!'))
    try:
        user_url = "/plugins/ksptooi/fastlogin/database/"
        url = parameter.SPIGOT_PATH + user_url
        with open(url + username.lower() + ".gd", "r") as f:
            user = f.readline().strip()
            passwd = f.readline().strip()
        # user = User.objects.filter(username=username, password=password)
    except IOError:
        return HttpResponse(r_json(1, '该账号不存在'))

    if "playername=" + username != user or "password=" + password != passwd:
        return HttpResponse(r_json(1, '用户名或密码错误'))

    user = User.objects.filter(username=username)
    if len(user) == 0:
        obj = User(username=username, password=password, register_time=int(time.time()))
        obj.save()
        user = User.objects.filter(username=username, password=password)
    user = user[0]
    uuid_ = get_uuid_from_name(username)  # 这里uuid_防止与uuid库名字冲突
    nickname = get_nickname_from_uuid(uuid_)
    user.uuid = uuid_
    user.nickname = nickname
    user.save()

    # 登录成功后
    request.session["is_login"] = True
    request.session['username'] = user.username
    request.session['password'] = user.password
    request.session['nickname'] = user.nickname
    request.session['qqnumber'] = user.qqnumber
    request.session['usrgroup'] = user.usrgroup
    request.session['id'] = user.id
    request.session['register_time'] = user.register_time
    request.session['avatar'] = user.avatar
    request.session.set_expiry(3600)  # 1小时有效期

    data.status=0
    data.data=user
    return HttpResponse(r_json(0,"用户信息",data))


def r_json(status,msg='',data=''):
    result={}
    result['status']=status
    result['msg']=msg
    result['data']=data

    return json.dumps(result)
    