import re,gzip,os,json

from QieGaoWorld import parameter
from django.http import HttpResponse
from QieGaoWorld.views.decorator import check_post
from QieGaoWorld.views.decorator import check_login
from QieGaoWorld.views.dialog import dialog
from QieGaoWorld.models import Message

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

def message_list(request):
    return Message.objects.all()


def message_star(request):
    status=str( request.POST.get('status',None))
    id=request.POST.get('id',None)
    menu=Message.objects.get(id=id)
    if(status == "True"):
        menu.status=False
    else:
        menu.status=True
    menu.save()
    return HttpResponse(dialog('ok', 'success', 'ok!'))

def message_del(request):
    id=request.POST.get('id',None)
    menu=Message.objects.get(id=id)
    
    menu.delete()
    return HttpResponse(dialog('ok', 'success', '删除成功!'))

def message_edit(request):
    try:
        _id= request.POST.get('id',None)
        content=request.POST.get('content',None)
        num=int(request.POST.get('num',None))
    except ValueError:
        return HttpResponse(dialog('failed', 'danger', '时间必须为数字'))
    info=re.search(r"\[.+",content)
    conte=info.group().replace('"',"'")
    if '[切糕新闻]' in conte:
        content=conte
    else:
        content="[{'text':'[切糕新闻]','color':'gold'}"+conte[3:]
    if(_id==""):
        menu=Message(content=content,num=num,status=True)
    else:
        menu=Message.objects.get(id=_id)
        menu.content=content
        menu.num=num
        menu.status=True

    menu.save()
    return HttpResponse(dialog('ok', 'success', '编辑成功!'))
def log_list(request):

    dirs = os.listdir( parameter.SPIGOT_PATH + "/logs" )
    dirs.sort()
    html=""
    
    # 输出所有文件和文件夹
    for file in dirs:
        if len(file)<15:
            continue
        html+="<a href='/ops/log_info?name="+file[:-7]+"'>"+file[:-7]+"</a><br>"
    return HttpResponse((html))

def log_info(request):
    name=request.GET.get("name",None)
    html=""
    if name == None:
        return log_list;
    f=gzip.open(parameter.SPIGOT_PATH + "/logs/"+name+".log.gz", "rb")
    # with gzip.open(parameter.SPIGOT_PATH + "logs/"+name+".log.gz", "r") as f:
        # 读取一行
    while True:
        try:
            line=str(f.readline(), encoding = "utf-8")
            if  line == None or len(line)==0:
                break
            if "[Server thread/INFO]" in line:
                continue
            if "[User Authenticator" in line:
                continue
            if " GroupManager - INFO" in line:
                continue
            if "[QQ]" in line:
                continue
            if "[切糕报时]" in line:
                continue
            if "[切糕公告]" in line:
                continue
            if "[Spigot Watchdog Thread" in line:
                continue
            if "Server thread/WARN" in line:
                continue
            if "[Server thread/ERROR]" in line:
                continue
            if "[Craft Scheduler Thread" in line:
                continue
            if "[main/WARN]" in line:
                continue
            if "[main/INFO]" in line:
                continue
            if "[Dynmap Render" in line:
                continue
            if "/WARN]" in line:
                continue
            info=re.search(r'\[[\d]{2}:[\d]{2}:[\d]{2}\]',line)
            if(info != None):
                html =html+ ("<span style='color:#017EBC;'>"+info.group()+"</span>")
            info=re.search(u"[\u4e00-\u9fa5]+",line)
            if(info != None):
                html=html+("<span style='color:green;'>"+info.group()+"</span>")
            info=re.search(r'<.+',line)
            if(info != None):
                html=html+("<span style=''>"+info.group()+"</span><br>")
        except UnicodeDecodeError : 
            pass
        

    return HttpResponse("<a href='/ops/log_list' style='color:#000'>返回上一页</a></br>"+(html))


  