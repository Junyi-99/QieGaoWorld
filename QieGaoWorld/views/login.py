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
from QieGaoWorld import common

# ajax (ensure csrf cookie)
@ensure_csrf_cookie
def login(request):
    if request.session.get("is_login", False):
        return redirect("/dashboard")
    return render(request, "login.html", {})


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
        row = common.filter("select * from playertable where playername='"+username+"'"  )
        if row ==None:
            return HttpResponse(dialog('failed', 'danger', '该账号不存在'))

        if  password != row[1]:
            return HttpResponse(dialog('failed', 'danger', '用户名或密码错误'))

        user = User.objects.filter(username=username, password=password)
        if len(user) == 0:
            obj = User(username=username, password=password, register_time=int(time.time()))
            obj.save()
            user = User.objects.filter(username=username, password=password)
        user = user[0]
        uuid_ = get_uuid_from_name(username)  # 这里uuid_防止与uuid库名字冲突
        nickname = get_nickname_from_uuid(uuid_)
        user.uuid = uuid_
        common.logs(user.uuid)
        user.nickname = nickname
        user.save()
    else:
        user = User.objects.filter(username=username, password=password)
        if len(user) == 0:
            return HttpResponse(dialog('failed', 'danger', '用户名或密码错误'))
        else:
            user = user[0]

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
            else:
                if username == "Junyi99":  # 硬核编码（hhh
                    request.session['permissions'] = settings.OP_PERMISSIONS
                else:
                    request.session['permissions'] = user.permissions
    else:
        request.session['permissions'] = user.permissions

    return HttpResponse(dialog('ok', 'success', '登录成功'))


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
        with open("../plugins/Essentials/userdata/%s.yml" % uuid) as f:
            lines = f.readlines()
            for l in lines:
                if "nickname: " in l:
                    return l[9:len(l) - 1]
            return ""
    except IOError:
        return ""
