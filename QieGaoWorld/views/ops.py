import re

from QieGaoWorld import parameter
from django.http import HttpResponse
from QieGaoWorld.views.decorator import check_post
from QieGaoWorld.views.decorator import check_login
from QieGaoWorld.views.dialog import dialog

def url(request, s):
    return eval(s)(request)

def whitelist(request):
    a=[]
    with open(parameter.SPIGOT_PATH + "/plugins/WhiteList/config.yml", "r") as f:
            plays = f.readlines()
            for p in plays:
                b=p.split('- ')
                if(len(b)==2 ):
                    a.append(b[1])
                pass
    return a

@check_login
@check_post
def whitelist_add(request):
    if "%whitelist%" not in request.session['permissions']:
        return HttpResponse(dialog('failed', 'danger', '权限不足'))
    name=str(request.POST.get('name', None))
    white_list=whitelist(request)
    if(name in white_list):
        return HttpResponse(dialog('failed', 'danger', '该用户已存在'))

    if(re.match(r'[0-9a-z]+',name) == None):
        return HttpResponse(dialog('failed', 'danger', '该用户id格式错误'))

    with open(parameter.SPIGOT_PATH + "/plugins/WhiteList/config.yml", "a") as w:
        w.write("\n - "+name)
        return HttpResponse(dialog('ok', 'success', '添加成功！'))

    return HttpResponse(dialog('failed', 'error', '添加失败！'))

@check_login
@check_post
def whitelist_del(request):
    if "%whitelist%" not in request.session['permissions']:
        return HttpResponse(dialog('failed', 'danger', '权限不足'))

    name=str(request.POST.get('name', None))
    # white_list=whitelist()
    # if(name not in white_list):
    #     return HttpResponse(dialog('failed', 'danger', '该用户不存在'))


    with open(parameter.SPIGOT_PATH + "/plugins/WhiteList/config.yml", "r") as r:
        fs=r.readlines()
        with open(parameter.SPIGOT_PATH + "/plugins/WhiteList/config.yml", "w") as w:
            for f in fs:
                if( "- "+name not in f):
                    w.write(f)
            return HttpResponse(dialog('ok', 'success', '删除成功！'))

