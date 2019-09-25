'''
@Description: In User Settings Edit
@Author: your name
@Date: 2019-01-16 23:34:10
@LastEditTime: 2019-09-25 18:32:09
@LastEditors: Please set LastEditors
'''
from QieGaoWorld import parameter
from django.http import HttpResponse,JsonResponse
from django.shortcuts import render
from QieGaoWorld.views.decorator import check_post
from QieGaoWorld.views.decorator import check_login
from QieGaoWorld.views.dialog import dialog
from QieGaoWorld.views.login import get_nickname_from_uuid,get_uuid_from_name
from QieGaoWorld.views import announcement
from QieGaoWorld.models import CmsBook,CmsChapter,User,DeclareAnimals,DeclareBuildings,Cases,Announcement,User
from QieGaoWorld import parameter as Para 
from QieGaoWorld import settings,common
from django.core import serializers
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
import os,traceback,uuid,logging,time,json,sys,requests
from PIL import Image
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.core.exceptions import MultipleObjectsReturned, ObjectDoesNotExist
from django.views.decorators.csrf import csrf_exempt

# from QieGaoWorld.serializers import AnnouncementSerializer
@csrf_exempt
def url(request, s):
    return eval(s)(request)


def login(request):
    username = str(request.GET.get("username", None))
    password = str(request.GET.get("password", None))
    

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
    data={}
    data["is_login"] = True
    data['username'] = user.username
    data['password'] = user.password
    data['nickname'] = user.nickname
    data['qqnumber'] = user.qqnumber
    data['id'] = user.id
    data['avatar'] = user.avatar
    
    return JsonResponse(r_json(0,"用户信息",data))

def index(request):

    obj = Announcement.objects.order_by("-publish_time")[0:5]

    # for i in range(0, len(obj)):
    #     obj[i].publish_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(obj[i].publish_time))
        # try:
        #     user = User.objects.get(username=obj[i].username)
        #     obj[i].avatar = user.avatar
        # except ObjectDoesNotExist:
        #     obj[i].avatar = settings.DEFAULT_FACE
        # except MultipleObjectsReturned:
        #     obj[i].avatar = settings.DEFAULT_FACE




    an=AnnouncementSerializer(obj, many=True)

    # return JsonResponse(an.data,safe=False);

    na = len(DeclareAnimals.objects.all())
    nb = len(DeclareBuildings.objects.all())
    nc = len(Cases.objects.all())
    try:
        from mcstatus import MinecraftServer
        server = MinecraftServer.lookup(Para.MC_SERVER)
        status = server.status()

        mot = status.description['text']
        motd = str(mot)
        pos = motd.find('§')
        while pos != -1:
            motd = motd[:pos] + motd[pos + 2:]
            pos = motd.find('§')

        fav = status.favicon
        opn = status.players.online
        user = []

        if status.players.sample is not None:
            for e in status.players.sample:
                user.append({'name': e.name, 'id': e.id,"nickname":username_get_nickname(e.name)})


        

        context = {
            'favicon': fav,
            'server_address': Para.MC_SERVER,
            'online_players_list': user,
            'online_players_number': opn,
            'number_buildings': nb,
            'number_animals': na,
            'number_cases': nc,
            'permissions': request.session['permissions'],
            'announcements': an.data,
            "latency":status.latency
        }
    except Exception as e:
        context = {
            'favicon': '',
            'server_address': Para.MC_SERVER,
            'online_players_list': [],
            'online_players_number': '超时',
            'number_buildings': nb,
            'number_animals': na,
            'number_cases': nc,
            # 'permissions': request.session['permissions'],
            'announcements': an.data,
            "latency":-1
        }

    # return JsonResponse(r_json(0,"首页",context))
    return JsonResponse(r_json(0,"首页",context))



def r_json(status,msg='',data=''):
    result={}
    result['status']=status
    result['msg']=msg
    result['data']=data
    return (result)