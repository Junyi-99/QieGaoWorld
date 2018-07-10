from django.http import HttpResponse
from django.shortcuts import render
from QieGaoWorld.models import DeclareAnimals
from django.views.decorators.csrf import ensure_csrf_cookie

from QieGaoWorld.views.decorator import check_post
from QieGaoWorld.views.decorator import check_login
from QieGaoWorld.views.police import username_get_avatar
from QieGaoWorld.views.police import username_get_nickname
import time

@check_login
@check_post
def animals_list(request):
    animals=[]
    animals=DeclareAnimals.objects.all()
    for i in range(0,len(animals)):
        animals[i].declare_time= time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(animals[i].declare_time))
        if(animals[i].username==animals[i].binding):
            animals[i].binding=username_get_nickname(animals[i].binding)


        animals[i].username=username_get_nickname(animals[i].username)
        if animals[i].status == 0:
            animals[i].status_label = ''
            animals[i].status_text = '未知'
        elif animals[i].status == 1:
            animals[i].status_label = 'uk-label-warning'
            animals[i].status_text = '正常'
        elif animals[i].status == 2:
            animals[i].status_label = 'uk-label-success'
            animals[i].status_text = '丢失'
        elif animals[i].status == 3:
            animals[i].status_label = 'uk-label-danger'
            animals[i].status_text = '已死亡'

    return {"list":animals}

@ensure_csrf_cookie
@check_login
@check_post
def animals_edit(request):
    try:
        if(str(request.POST.get('type', None)).strip()=="个人"):
            binding=request.session.get("username")
        else:
            binding=str(request.POST.get('binding', None)).strip()
        obj=DeclareAnimals(
            declare_time=int(time.time()),
            username=request.session.get("username"),
            binding=binding,
            license=str(request.POST.get('license', None)).strip(),
            feature=str(request.POST.get('feature', None)).strip(),
            status=str(request.POST.get('status', None)).strip()
            
        )
        obj.save()
        return HttpResponse(r'{"status": "ok", "msg": "更新成功！"}')
    except Exception as e:
        print(e)
        return HttpResponse(r'{"status": "failed", "msg": "内部错误"}')