import re,json
from django.shortcuts import render
from django.http import HttpResponse
from django.contrib.auth.models import Group,Permission

from QieGaoWorld import parameter
from QieGaoWorld.views.decorator import check_post
from QieGaoWorld.views.decorator import check_login
from QieGaoWorld.views.dialog import dialog
from QieGaoWorld.models import User

@check_login
@check_post
def url(request, s):
    return eval(s)(request)

def user_list(request):
    user=User.objects.all()

    return user

def group_list(request):

    group=Group.objects.all()
    for i in range(0,len(group)):
        group[i].value=group[i].name
    return group

def user_info(request):
    _id=request.POST.get("id",None)
    usre=User.objects.get(id=_id)
    return render(request, "dashboard/user/info.html", {})

def user_edit(request):
    _id=int(request.POST.get("id",None))
    user=User.objects.get(id=_id)
    return render(request, "dashboard/user/edit.html", {"info":user,"group":group_list(request)})

def group_add(request):
    _id=request.POST.get("id",None)
    name=request.POST.get("title")
    if _id==None:
        group=Group(name=name)
    else:
        group=Group.objects.get(id=_id)
        group.name=name
    group.save()
    
    return HttpResponse(dialog('ok', 'success', '添加成功'))
def group_info(request):
    _id=request.POST.get("id",None)
    if _id == None:
        return HttpResponse(dialog('ok', 'danger', '参数错误'))
    per=Permission.objects.filter()
