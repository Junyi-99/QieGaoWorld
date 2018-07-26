import json
import logging
import os
import time

from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.views.decorators.csrf import ensure_csrf_cookie

from QieGaoWorld import settings
from QieGaoWorld.models import User
from QieGaoWorld.views.decorator import check_post
from QieGaoWorld.views.dialog import dialog


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
    ON_SERVER = False

    username = str(request.POST.get("username", None))
    password = str(request.POST.get("password", None))

    logging.debug("Login Verify: [%s] [%s]" % (username, password))
    if ON_SERVER:
        with open("../plugins/WhiteList/config.yml", "r") as f:
            plays = f.read()
            if "- " + username.lower() not in plays:
                return HttpResponse(dialog('failed', 'danger', '您不在白名单'))
        with open("../banned-players.json", "r") as f:
            plays = json.loads(f.read())
            s = "%"
            for b in plays:
                s += b['name'] + "%"
            if "%" + username + "%" in s:
                return HttpResponse(dialog('failed', 'danger', '登录失败！您的帐号已被此服务器封禁!'))
        try:
            user_url = "../plugins/ksptooi/fastlogin/database/"
            url = os.getcwd() + "/" + user_url
            with open(url + username.lower() + ".gd", "r") as f:
                user = f.readline().strip()
                passwd = f.readline().strip()
            # user = User.objects.filter(username=username, password=password)
        except IOError:
            return HttpResponse(dialog('failed', 'danger', '该账号不存在'))

        if "playername=" + username != user or "password=" + password != passwd:
            return HttpResponse(dialog('failed', 'danger', '用户名或密码错误'))

        user = User.objects.filter(username=username, password=password)
        if len(user) == 0:
            obj = User(username=username, password=password, nickname=username, register_time=int(time.time()))
            obj.save()
            user = User.objects.filter(username=username, password=password)
    else:
        user = User.objects.filter(username=username, password=password)
        if len(user) == 0:
            return HttpResponse(dialog('failed', 'danger', '用户名或密码错误'))

    # 登录成功后
    request.session["is_login"] = True
    request.session['username'] = username
    request.session['password'] = password
    request.session['nickname'] = user[0].nickname
    request.session['qqnumber'] = user[0].qqnumber
    request.session['usrgroup'] = user[0].usrgroup
    request.session['register_time'] = user[0].register_time
    request.session['avatar'] = user[0].avatar
    request.session.set_expiry(3600)  # 1小时有效期

    if ON_SERVER:
        with open("../ops.json", "r") as f:
            user = f.read()
            a = (json.loads(user))
            s = "%"
            for b in a:
                s += b['name'] + "%"
            if username in s:
                request.session['permissions'] = settings.OP_PERMISSIONS
    else:
        request.session['permissions'] = user[0].permissions

    return HttpResponse(dialog('ok', 'success', '登录成功'))
