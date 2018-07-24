from django.http import HttpResponse
from django.shortcuts import render
from django.core.exceptions import MultipleObjectsReturned

from QieGaoWorld.models import User

import re
import time
import logging

from QieGaoWorld.views.decorator import check_post
from QieGaoWorld.views.dialog import dialog


def register(request):
    return render(request, "register.html", {})


@check_post
def register_verify(request):
    username = str(request.POST.get("username", None))
    password = str(request.POST.get("password", None))
    nickname = str(request.POST.get("nickname", None))

    logging.info("用户注册： 用户名：[%s] 密码：[%s] 昵称：[%s]" % (username, password, nickname))

    # 检测username是否合法
    pattern = re.compile(r'[^\w]')
    match = pattern.match(username)
    if match:
        return HttpResponse(dialog('failed', 'danger', '用户名不合法'))

    # 检测password是否合法
    match = pattern.match(password)
    if match:
        return HttpResponse(dialog('failed', 'danger', '密码不合法'))

    lis = ["SYSTEM", "N/A", "ADMIN", "管理员", "版主", "vip", ".com", ".cn", "官方", "京东", "淘宝", "SELECT", "FROM", "WHERE",
           "INSERT", "黑社会", "性爱", "操", "肏", "你妈", "YY", "攻击", "黄网", "迷药", "匿名", "NULL", "公司", "经理", "投资商", "迅雷",
           "XUNLEI",
           "百度"]
    for eachL in lis:
        if eachL in username.upper():
            return HttpResponse(dialog('failed', 'danger', '用户名包含非法字符'))

    for eachL in lis:
        if eachL in nickname.upper():
            return HttpResponse(dialog('failed', 'danger', '昵称包含非法字符'))

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
    user = User.objects.filter(username=username)
    if len(user) != 0:
        return HttpResponse(dialog('failed', 'danger', '用户名已存在'))
    # ===================================检测重复用户部分结束

    obj = User(username=username, password=password, nickname=nickname, register_time=int(time.time()))
    obj.save()
    return HttpResponse(dialog('ok', 'success', '注册成功！赶快去登录吧！'))
