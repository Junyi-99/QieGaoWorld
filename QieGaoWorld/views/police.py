from django.core.exceptions import MultipleObjectsReturned, ObjectDoesNotExist
from django.http import HttpResponse
from django.shortcuts import render
from django.views.decorators.csrf import ensure_csrf_cookie

from QieGaoWorld.views.decorator import check_post
from QieGaoWorld.models import Cases
from QieGaoWorld.models import User

import time
import logging

from QieGaoWorld.views.dialog import dialog


@ensure_csrf_cookie
def case_detail(request):
    error_msg = '<div class="uk-modal-header"><h2 class="uk-modal-title" style="color: #cc3947">%s</h2></div>'

    if '%police_cases_watch%' not in request.session.get('permissions', ''):
        return HttpResponse(error_msg % "您没有查看案件详情的权限！")

    try:
        id_ = int(request.GET.get('id', None))
    except ValueError:
        return HttpResponse(error_msg % "参数错误！")

    try:
        obj = Cases.objects.get(id=id_)
        obj.report_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(int(obj.report_time)))
        obj.nickname = username_get_nickname(obj.username)
        if obj.status == 0:
            obj.status_label = ''
            obj.status_text = '等待调查'
        elif obj.status == 1:
            obj.status_label = 'uk-label-warning'
            obj.status_text = '正在调查'
        elif obj.status == 2:
            obj.status_label = 'uk-label-success'
            obj.status_text = '处理成功'
        elif obj.status == 3:
            obj.status_label = 'uk-label-danger'
            obj.status_text = '处理失败'
        else:
            obj.status_label = ''
            obj.status_text = '未知状态'
        return render(request, "dashboard/police/cases_detail.html", {'case': obj})
    except MultipleObjectsReturned as e:
        logging.error(e)
        return HttpResponse(error_msg % "内部错误，请联系管理员！")
    except ObjectDoesNotExist:
        return HttpResponse(error_msg % "报案不存在！")


@ensure_csrf_cookie
@check_post
# 更改案件状态
def change_status(request):
    if '%police_cases_modify%' not in request.session.get('permissions', ''):
        return HttpResponse(dialog('failed', 'danger', '权限不足'))

    try:
        id_ = int(request.POST.get('id', None))
        new_status = int(request.POST.get('new_status', None))
        logging.debug("更改案件状态： id=%d, new_status=%d" % (id_, new_status))
    except ValueError:
        return HttpResponse(dialog('failed', 'danger', '参数错误'))

    try:
        obj = Cases.objects.get(id=id_)
        if 0 <= new_status <= 3:
            obj.status = new_status
            obj.save()
            return HttpResponse(dialog('ok', 'success', '更新案件信息成功，刷新页面后生效'))
        else:
            return HttpResponse(dialog('failed', 'danger', '状态值错误'))
    except MultipleObjectsReturned as e:
        logging.error(e)
        return HttpResponse(dialog('failed', 'danger', '内部错误，请联系管理员'))
    except ObjectDoesNotExist:
        return HttpResponse(dialog('failed', 'danger', '报案不存在'))


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
            return HttpResponse(dialog('failed', 'danger', '坐标请填入整数'))

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
            return HttpResponse(dialog('failed', 'danger', '请确认没有留空项目'))

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
        logging.error(e)
        return HttpResponse(dialog('failed', 'danger', '内部错误，请联系管理员'))

    return HttpResponse(dialog('ok', 'success', '报案成功！您可以在警署大厅看到自己的报案'))


def username_get_avatar(username):
    try:
        obj = User.objects.filter(username=username)
        if len(obj) == 0:
            return 'static\\face\\default.jpg'
        return obj[0].avatar
    except MultipleObjectsReturned:
        return 'static\\face\\default.jpg'
    except Exception as e:
        logging.error(e)
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
        logging.error(e)
        return 'Internal Error'

def id_get_nickname(id):
    try:
        obj = User.objects.filter(id=id)
        if len(obj) == 0:
            return 'Unknown Username'
        return obj[0].nickname
    except MultipleObjectsReturned:
        return 'Internal Error'
    except Exception as e:
        logging.error(e)
        return 'Internal Error'


def page_police_hall(request):
    my_cases = []
    cases = Cases.objects.all()
    cases = sorted(cases, key=lambda c: c.report_time, reverse=True)
    for i in range(0, len(cases)):

        cases[i].avatar = username_get_avatar(cases[i].username)
        cases[i].nickname = username_get_nickname(cases[i].username)
        cases[i].report_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(cases[i].report_time))
        if len(cases[i].detail) > 30:
            cases[i].detail = cases[i].detail[:30] + "..."
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

        if cases[i].username == request.session.get('username', ''):
            my_cases.append(cases[i])

    content = {
        'cases': cases,
        'my_cases': my_cases,
        'permissions': request.session.get('permissions', '')
    }

    return render(request, "dashboard/police/police_hall.html", content)
