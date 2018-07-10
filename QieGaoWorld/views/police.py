from django.core.exceptions import MultipleObjectsReturned
from django.http import HttpResponse
from django.shortcuts import render
from django.views.decorators.csrf import ensure_csrf_cookie

from QieGaoWorld.views.decorator import check_post
from QieGaoWorld.models import Cases
from QieGaoWorld.models import User

import time


@ensure_csrf_cookie
@check_post
# CALL THE POLICE
def report(request):
    try:
        position = str(request.POST.get('position', None)).strip()
        try:
            coordinate_x = int(request.POST.get('coordinate_x', None))
            coordinate_y = int(request.POST.get('coordinate_y', None))
            coordinate_z = int(request.POST.get('coordinate_z', None))
        except ValueError:
            return HttpResponse(r'{"status": "failed", "msg": "坐标请填入整数"}')

        summary = str(request.POST.get('summary', None)).strip()
        detail = str(request.POST.get('detail', None)).strip()

        flag = False
        if len(position) == 0:
            flag = True
        if len(summary) == 0:
            flag = True
        if len(detail) == 0:
            flag = True
        if flag:
            return HttpResponse(r'{"status": "failed", "msg": "请确认没有留空项目！"}')

        obj = Cases(
            report_time=int(time.time()),
            position=position,
            coordinate='%d, %d, %d' % (coordinate_x, coordinate_y, coordinate_z),
            summary=summary,
            detail=detail,
            username=request.session.get('username', None),
            progress='等待受理',
            status=0,
            picture=''
        )
        obj.save()

        # TODO: 报警可以上传案发现场截图的功能

    except Exception as e:
        print(e)
        return HttpResponse(r'{"status": "failed", "msg": "内部错误"}')

    return HttpResponse(r'{"status": "ok", "msg": "报警成功！"}')


def username_get_avatar(username):
    try:
        obj = User.objects.filter(username=username)
        if len(obj) == 0:
            return 'static\\face\\default.jpg'
        return obj[0].avatar
    except MultipleObjectsReturned:
        return 'static\\face\\default.jpg'
    except Exception as e:
        print(e)
        return 'static\\face\\default.jpg'


def username_get_nickname(username):
    try:
        obj = User.objects.filter(username=username)
        if len(obj) == 0:
            return 'Unknown Username'
        return obj[0].nickname
    except MultipleObjectsReturned:
        return 'Internal Error'
    except Exception as e:
        print(e)
        return 'Internal Error'


def page_police_hall(request):
    my_cases = []
    cases = Cases.objects.all()

    for i in range(0, len(cases)):

        cases[i].avatar = username_get_avatar(cases[i].username)
        cases[i].nickname = username_get_nickname(cases[i].username)
        cases[i].report_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(cases[i].report_time))

        if cases[i].status == 0:
            cases[i].status_label = ''
            cases[i].status_text = '等待调查'
        elif cases[i].status == 1:
            cases[i].status_label = 'uk-label-warning'
            cases[i].status_text = '正在调查'
        elif cases[i].status == 2:
            cases[i].status_label = 'uk-label-success'
            cases[i].status_text = '处理成功'
        elif cases[i].status == 3:
            cases[i].status_label = 'uk-label-danger'
            cases[i].status_text = '处理失败'
        else:
            cases[i].status_label = ''
            cases[i].status_text = '未知状态'

        if cases[i].username == request.session.get('username', None):
            my_cases.append(cases[i])

    content = {
        'cases': cases,
        'my_cases': my_cases
    }

    return render(request, "dashboard/police/police_hall.html", content)
