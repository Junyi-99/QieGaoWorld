
import re,json
from QieGaoWorld import parameter
from django.http import HttpResponse
from QieGaoWorld.views.decorator import check_post
from QieGaoWorld.views.decorator import check_login
from QieGaoWorld.views.dialog import dialog
from QieGaoWorld.views.police import username_get_nickname
from QieGaoWorld.models import Task

@check_login
@check_post
def url(request, s):
    return eval(s)(request)


def task_del(request):
    id=request.POST.get('id',None)
    menu=Task.objects.get(id=id,username=request.session['username'])
    if menu != None:
        menu.delete()
    return HttpResponse(dialog('ok', 'success', '删除成功!'))

def task_add(request):
    try:
        title=request.POST.get('title',None)
        content=request.POST.get("content",None)
    except ValueError:
        return HttpResponse(dialog('failed', 'danger', '参数错误'))
    if title == None :
        return HttpResponse(dialog('failed', 'danger', '请填写标题'))
    if content == None :
        return HttpResponse(dialog('failed', 'danger', '请填写任务详情'))

    menu=Task(title=title,username=(request.session['username']),content=content,status=0)
    menu.save()
    return HttpResponse(dialog('ok', 'success', '任务发布成功!'))

def task_list(request,_all=False):
    if _all:
        task=Task.objects.all()
    else:
        task=Task.objects.filter(username=request.session['username'])
    for i in range(0,len(task)) :
        if task[i].status == 0:
            task[i].status_label="uk-label-success"
            task[i].status_text="悬赏中"
        elif task[i].status == 1:
            task[i].status_label="uk-label-warning"
            task[i].status_text="已完成"
        else:
            task[i].status_label="uk-label-danger"
            task[i].status_text="已结束"
        task[i].nickname=username_get_nickname(task[i].username)

    return task

def task_change_status(request):
    try:
        id_ = int(request.POST.get('id', None))
        new_status = int(request.POST.get('status', None))
        username = request.session.get('username', None)
    except ValueError:
        return HttpResponse(dialog('failed', 'danger', '参数错误'))

    try:
        obj = Task.objects.get(id=id_)
        # 1、检查是否是当前用户的状态为“审核通过”的建筑，再检查修改状态是否为“正在建设”和“完工”  如果不是，检查是否是管理员
        if (obj.username != username )  :
            return HttpResponse(dialog('failed', 'danger', '可能这个任务不属于你！'))

        
        old_status=obj.status
        obj.status = new_status
        obj.save()
        return HttpResponse(dialog('ok', 'success', '更新任务状态成功！刷新页面生效！'))
        
    except MultipleObjectsReturned as e:
        logging.error(e)
        return HttpResponse(dialog('failed', 'danger', '内部错误，请联系管理员'))
    except ObjectDoesNotExist:
        return HttpResponse(dialog('failed', 'danger', '可能这个任务不属于你！'))