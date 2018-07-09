from django.http import HttpResponse
from django.shortcuts import render
from django.core.exceptions import MultipleObjectsReturned

from QieGaoWorld.models import User

import re
import time


def register(request):
    return render(request, "register.html", {})


def register_verify(request):
    if request.method != "POST":
        return HttpResponse(r'{"status": "failed", "msg": "request method invalid"}')
    username = str(request.POST.get("username", None))
    password = str(request.POST.get("password", None))
    nickname = str(request.POST.get("nickname", None))

    print(username, password, nickname)

    # 检测username是否合法
    pattern = re.compile(r'[^\w]')
    match = pattern.match(username)
    if match:
        return HttpResponse(r'{"status": "failed", "msg": "username invalid"}')

    # 检测password是否合法
    match = pattern.match(password)
    if match:
        return HttpResponse(r'{"status": "failed", "msg": "password invalid"}')

    l = ["SYSTEM", "N/A", "ADMIN", "管理员", "版主", "vip", ".com", ".cn", "官方", "京东", "淘宝", "SELECT", "FROM", "WHERE",
         "INSERT", "黑社会", "性爱", "操", "肏", "你妈", "YY", "攻击", "黄网", "迷药", "匿名", "NULL", "公司", "经理", "投资商", "迅雷", "XUNLEI",
         "百度"]
    for eachL in l:
        if eachL in username.upper():
            return HttpResponse(r'{"status": "failed", "msg": "用户名包含非法字符"}')

    for eachL in l:
        if eachL in nickname.upper():
            return HttpResponse(r'{"status": "failed", "msg": "昵称包含非法字符"}')

    # pattern = re.compile(r'^([a-zA-Z0-9_-])+@([a-zA-Z0-9_-])+(\.[a-zA-Z0-9_-])+')
    # match = pattern.match(email)  # 检测email是否合法
    # if not match:
    #     return HttpResponse(r'{"status": "failed", "msg": "email invalid"}')

    # pattern = re.compile(r'[^0-9]')  # 检测qq是否合法
    # match = pattern.match(qq)
    # if match:
    #     qq = "0"

    # ===================================数据过滤部分结束

    # password_md5 = hashlib.md5(password.encode("utf-8")).hexdigest()
    # username_md5 = hashlib.md5(username.encode("utf-8")).hexdigest()

    # ===================================检测重复用户部分开始
    try:
        user = User.objects.filter(username=username)
    except MultipleObjectsReturned:
        return HttpResponse(r'{"status": "failed", "msg": "用户名已存在"}')
    finally:
        pass
    if len(user) != 0:
        return HttpResponse(r'{"status": "failed", "msg": "用户名已存在"}')
    # ===================================检测重复用户部分结束

    obj = User(username=username, password=password, nickname=nickname, register_time=int(time.time()))
    obj.save()
    return HttpResponse(r'{"status": "ok", "msg": "注册成功"}')
