import re,gzip,os,json

from QieGaoWorld import parameter
from django.http import HttpResponse
from QieGaoWorld.views.decorator import check_post
from QieGaoWorld.views.decorator import check_login
from QieGaoWorld.views.dialog import dialog
from QieGaoWorld.models import Message
from django.shortcuts import render

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
    dirs.sort(reverse=True)
    html=[]
    
    # 输出所有文件和文件夹
    for file in dirs:
        if len(file)<15:
            continue
        html.append(file[:-7])
    return render(request, 'dashboard/ops/log_list.html', {'permissions': request.session.get("permissions","default"),'list': html})

def log_info(request):
    name=request.POST.get("name",None)
    html=[]
    _group=[]
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
            if "/" == line[0:1] or "login" in line.lower() :
                continue
            ht={}
            time=""
            _type=""
            area=""
            user=""
            content=""
            info=re.search(r'\[[\d]{2}:[\d]{2}:[\d]{2}\]',line)
            if(info != None):
                time=info.group()
            info=re.search('\[[a-zA-z /\-0-9#]+\]',line)
            if(info != None):
                _type=info.group()
                if _type not in _group:
                    _group.append(_type)
            content=line[line.find(']:')+2:]
            info=re.search(u"\[[Q\u4e00-\u9fa5]+\]",line)
            if(info != None):
                area=info.group()
                content=content[len(area)+1:]
                # if '[QQ]' in area:
                #     area="<span style='color:#%s'>%s</span>" %('FF5555',area)
            info=re.search(u"<.*>",content)
            if(info != None):
                user=info.group()
                content=content[len(user):]
                # user="<span style='color:#%s'>%s</span>" %('00AA00',user)
            
            html.append({'time':time,"type":_type,"area":area,"content":content,"area":area,"user":user})
            # info=re.search(r'<.+',line)
            # if(info != None):
                # html=html+("<span style=''>"+info.group()+"</span><br>")
        except UnicodeDecodeError : 
            pass
    

    return render(request, 'dashboard/ops/log_info.html', {'permissions': request.session.get("permissions","default"),'list': html,"title":name,"group":_group})


  