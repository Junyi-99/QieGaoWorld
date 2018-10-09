
import re,json
from QieGaoWorld import parameter
from django.http import HttpResponse
from QieGaoWorld.views.decorator import check_post
from QieGaoWorld.views.decorator import check_login
from QieGaoWorld.views.dialog import dialog
from QieGaoWorld.views.police import id_get_nickname
from QieGaoWorld.models import SkullCustomize

@check_login
@check_post
def url(request, s):
    return eval(s)(request)


def skull_del(request):
    id=request.POST.get('id',None)
    menu=SkullCustomize.objects.get(id=id,user_id=request.session['id'])
    
    menu.delete()
    return HttpResponse(dialog('ok', 'success', '删除成功!'))

def skull_add(request):
    try:
        name=request.POST.get('name',None)
        number=int(request.POST.get('number',None))
        content=request.POST.get("content",None)
    except ValueError:
        return HttpResponse(dialog('failed', 'danger', '参数错误'))

    info=re.search(r'Id:"[\d\w-]+',content)
    if info==None or info.group()==None or len(info.group())<4 :
        return HttpResponse(dialog('failed', 'danger', '头颅代码格式错误'))
    id=info.group()[4:]
    info=re.search(r'Value:"[\d\w]+',content)
    if info==None or info.group()==None or len(info.group())<7 :
        return HttpResponse(dialog('failed', 'danger', '头颅代码格式错误'))
    value=info.group()[7:]

    menu=SkullCustomize(name=name,user_id=int(request.session['id']),number=number,status=False,content=id+':'+value)
    menu.save()
    return HttpResponse(dialog('ok', 'success', '添加成功!'))

def skull_list(request,_all=False):
    # if _all:
    if '%op%' not in request.session.get('permissions', ''):
        skull=SkullCustomize.objects.all()
    else:
        skull=SkullCustomize.objects.filter(user_id=request.session['id'])
    for i in range(0,len(skull)) :
        if skull[i].status:
            skull[i].status_class="uk-label-success"
            skull[i].status_text="已取货"
        else:
            skull[i].status_class=""
            skull[i].status_text="未取货"
        skull[i].nickname=id_get_nickname(skull[i].user_id)

    return skull