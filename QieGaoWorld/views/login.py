import logging
from django.core.exceptions import MultipleObjectsReturned
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.views.decorators.csrf import ensure_csrf_cookie
from QieGaoWorld.models import User
from QieGaoWorld.views.decorator import check_post


# ajax (ensure csrf cookie)
@ensure_csrf_cookie
def login(request):
    if request.session.get("is_login", False):
        return redirect("/dashboard")
    return render(request, "login.html", {})


@check_post
def login_verify(request):

    username = str(request.POST.get("username", None))
    password = str(request.POST.get("password", None))

    logging.debug("Login Verify: [%s] [%s]" % (username, password))

    try:
        user = User.objects.filter(username=username, password=password)
    except MultipleObjectsReturned:
        return HttpResponse(r'{"status": "failed", "msg": "内部错误"}')
    finally:
        pass
    if len(user) == 0:
        return HttpResponse(r'{"status": "failed", "msg": "用户名或密码错误"}')

    request.session["is_login"] = True
    request.session['username'] = user[0].username
    request.session['password'] = user[0].password
    request.session['nickname'] = user[0].nickname
    request.session['qqnumber'] = user[0].qqnumber
    request.session['usrgroup'] = user[0].usrgroup
    request.session['register_time'] = user[0].register_time
    request.session['avatar'] = user[0].avatar
    request.session['permissions'] = user[0].permissions
    request.session.set_expiry(3600)  # 1小时有效期
    return HttpResponse(r'{"status": "ok", "msg": "登录成功"}')
