import logging
import time

from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned
from django.http import HttpResponse

from QieGaoWorld import settings
from QieGaoWorld.views.decorator import check_post, check_login
from QieGaoWorld.models import Announcement, User
from QieGaoWorld.views.dialog import dialog


@check_login
@check_post
def announcement_new(request):
    username = request.session.get('username', "N/A")
    title = request.POST.get('title', '')
    content = request.POST.get('content', '')
    announcement_type = request.POST.get('type', '')

    if '%publish_announcement%' not in request.session.get('permissions', '%default%'):
        return HttpResponse(dialog('failed', 'danger', '权限不足'))

    try:
        obj = Announcement(
            publish_time=int(time.time()),
            username=username,
            title=title,
            content=content,
            type=announcement_type
        )
        obj.save()

        return HttpResponse(dialog('ok', 'success', '公告发布成功'))
    except Exception as e:
        logging.error(e)
        return HttpResponse(dialog('failed', 'danger', '内部错误，请联系管理员'))


@check_login
@check_post
def announcement_delete(request):
    if '%announcement_delete%' not in request.session.get('permissions', '%default%'):
        return HttpResponse(dialog('failed', 'danger', '权限不足'))
    id = str(request.POST.get('id', '')).strip()
    try:
        obj = Announcement.objects.get(id=id)
        obj.visible = False
        obj.save()
        return HttpResponse(dialog('ok', 'success', '删除成功'))
    except ObjectDoesNotExist:
        return HttpResponse(dialog('failed', 'danger', '公告ID不存在'))
    except MultipleObjectsReturned:
        return HttpResponse(dialog('failed', 'danger', '内部错误，请联系管理员'))

    pass


def announcement_list(request):
    obj = Announcement.objects.all()
    obj = sorted(obj, key=lambda e: e.publish_time, reverse=True)
    length = len(obj)
    if length > 5:
        length = 5
    for i in range(0, length):
        obj[i].publish_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(obj[i].publish_time))
        if obj[i].type == 0:
            obj[i].color = '#F7F7F7'
            obj[i].type_text = '通知'
            obj[i].type_label = ''
        elif obj[i].type == 1:
            obj[i].color = '#FFFBF7'
            obj[i].type_text = '重要'
            obj[i].type_label = 'uk-label-warning'
        elif obj[i].type == 2:
            obj[i].color = '#FFF7F9'
            obj[i].type_text = '严重'
            obj[i].type_label = 'uk-label-danger'

        try:
            user = User.objects.get(username=obj[i].username)
            obj[i].avatar = user.avatar
        except ObjectDoesNotExist:
            obj[i].avatar = settings.DEFAULT_FACE
        except MultipleObjectsReturned:
            obj[i].avatar = settings.DEFAULT_FACE

    return obj[:length]
