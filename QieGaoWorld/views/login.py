import json
import logging
import os
import time
import hashlib, uuid
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.views.decorators.csrf import ensure_csrf_cookie

from QieGaoWorld import parameter
from QieGaoWorld import settings
from QieGaoWorld.models import User
from QieGaoWorld.views.decorator import check_post
from QieGaoWorld.views.dialog import dialog
from QieGaoWorld import common,parameter

# ajax (ensure csrf cookie)
@ensure_csrf_cookie
def login(request):
    if request.session.get("is_login", False):
        return redirect("/dashboard")
    
    return render(request, "login.html", {"type":request.GET.get("t",''),"oauth_callback":request.GET.get("oauth_callback",'')})


def test(request):
    return render(request, "dialog.html", {})


@check_post
def login_verify(request):
    url = "./"
    ON_SERVER = True

    username = str(request.POST.get("username", None))
    password = str(request.POST.get("password", None))

    logging.debug("Login Verify: [%s] [%s]" % (username, password))
    if ON_SERVER:
        with open(parameter.SPIGOT_PATH + "/plugins/WhiteList/config.yml", "r") as f:
            plays = f.read()
            if "- " + username.lower() not in plays:
                return HttpResponse(dialog('failed', 'danger', '您不在白名单'))
        with open(parameter.SPIGOT_PATH + "/banned-players.json", "rb") as f:
            plays = json.loads(f.read())
            s = "%"
            for b in plays:
                s += b['name'] + "%"
            if "%" + username + "%" in s:
                return HttpResponse(dialog('failed', 'danger', '登录失败！您的帐号已被此服务器封禁!'))
        try:
            user_url = "/plugins/ksptooi/fastlogin/database/"
            url = parameter.SPIGOT_PATH + user_url
            with open(url + username.lower() + ".gd", "r") as f:
                user = f.readline().strip()
                passwd = f.readline().strip()
            # user = User.objects.filter(username=username, password=password)
        except IOError:
            return HttpResponse(dialog('failed', 'danger', '该账号不存在'))

        if "playername=" + username != user or "password=" + password != passwd:
            return HttpResponse(dialog('failed', 'danger', '用户名或密码错误'))

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
    else:
        user = User.objects.filter(username=username, password=password)
        if len(user) == 0:
            return HttpResponse(dialog('failed', 'danger', '用户名或密码错误'))
        else:
            user = user[0]
    user.token_expired_time=int(time.time())
    md5_str=str(time.time())+user.username
    m2 = hashlib.md5()   
    m2.update(md5_str.encode('utf-8'))   
    user.token=m2.hexdigest()

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

    if ON_SERVER:
        with open("../ops.json", "r") as f:
            ops = f.read()
            a = (json.loads(ops))
            s = "%"
            for b in a:
                s += b['name'] + "%"
            if username in s:
                request.session['permissions'] = settings.OP_PERMISSIONS
                # request.session['permissions'] = user.get_all_permissions()
            else:
                if username == "Junyi99":  # 硬核编码（hhh
                    request.session['permissions'] = settings.OP_PERMISSIONS
                else:
                    request.session['permissions'] = user.permissions
    else:
        request.session['permissions'] = user.permissions

    return HttpResponse(dialog('ok', 'success', '登录成功',{"token":user.token}))


def get_uuid_from_name(name):
    player_name = "OfflinePlayer:%s" % name
    m = hashlib.md5()
    m.update(player_name.encode("utf-8"))
    d = bytearray(m.digest())
    d[6] &= 0x0f
    d[6] |= 0x30
    d[8] &= 0x3f
    d[8] |= 0x80
    return (uuid.UUID(bytes=bytes(d)))


def get_nickname_from_uuid(uuid):
    
    try:
        with open(parameter.SPIGOT_PATH+("/plugins/Essentials/userdata/%s.yml" % uuid)) as f:
            lines = f.readlines()
            for l in lines:
                if "nickname: " in l:
                    return l[9:len(l) - 1]
            return ""
    except IOError:
        return ""

def auto_login(request):
    url = "./"

    token = str(request.GET.get("token", None))

    user = User.objects.exclude(token_expired_time__gte=int(time.time()), token=token)
    if len(user) == 0:
        return HttpResponse(dialog('failed', 'danger', '用户名或密码错误'))
    else:
        user = user[0]

    # 登录成功后
    data={}
    data["is_login"] = True
    data['username'] = user.username
    data['nickname'] = user.nickname
    data['qqnumber'] = user.qqnumber
    data['usrgroup'] = user.usrgroup
    data['id'] = user.id
    data['register_time'] = user.register_time
    data['avatar'] = user.avatar
    # data.set_expiry(3600)  # 1小时有效期


    return HttpResponse(dialog('ok', 'success', '登录成功',data))

