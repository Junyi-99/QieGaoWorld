
import re,json
from QieGaoWorld import parameter
from django.http import HttpResponse
from QieGaoWorld.views.decorator import check_post
from QieGaoWorld.views.decorator import check_login
from QieGaoWorld.views.dialog import dialog
from QieGaoWorld.models import SkullCustomize

@check_login
@check_post
def url(request, s):
    return eval(s)(request)


def skull_del(request):
    id=request.POST.get('id',None)
    menu=SkullCustomize.objects.get(id=id)
    
    menu.delete()
    return HttpResponse(dialog('ok', 'success', '删除成功!'))

def skull_add(request):
    name=request.POST.get('name',None)
    number=request.POST.get('number',None)
    content=request.POST.get("content",None)
    info=re.search(r'Id:"[\d\w-]+',content)
    id=info.group()[4:]
    info=re.search(r'Value:"[\d\w]+',content)
    value=info.group()[7:]

    menu=SkullCustomize(name=name,user_id=int(request.session['id']),number=number,status=False,content=id+':'+value)
    menu.save()
    return HttpResponse(dialog('ok', 'success', '添加成功!'))

