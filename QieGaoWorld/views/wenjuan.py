import time,logging,json


from QieGaoWorld import parameter,common
from django.http import HttpResponse
from QieGaoWorld.views.decorator import check_post,check_login
from QieGaoWorld.views.dialog import dialog
from QieGaoWorld.models import Problem,ProblemInfo,User,Conf
from django.shortcuts import render

def url(request, s):
    return eval(s)(request)

def index(request):
    wenjuan=Problem.objects.filter(status=True)
    wenjuan=sorted(wenjuan,key=lambda w: w.list,reverse=True)
    problem_list=Conf.objects.get(key="problem_list")
    problem_list=json.loads(problem_list.content)
    wj=[]
    j=1
    for i in range(0,len(wenjuan)):
        wenjuan[i].option=option_list(wenjuan[i].id)
        n=problem_list.index(str(wenjuan[i].id))
        if wenjuan[i].type not in [4,5]:
            wenjuan[i].list=j
            j+=1
        wj.insert(n,wenjuan[i])
    
    _name=Problem(dry="你的英文游戏id是：",id="name",type=0)
    _name.list=j
    wj.insert(len(wenjuan)+1,_name)
    w=[]
    tmp=[]
    page=1
    for j in range(0,len(wj)):
        if wj[j].type == 5:
            w.append({"page":page,"list":tmp})
            tmp=[]
            page +=1
        else:
            tmp.append(wj[j])
    w.append({"page":page,"list":tmp})
    return render(request, "dashboard/wenjuan/index.html", {"wenjuan":w,"count":len(w)})


@check_login
def problem_list(request):
    wenjuan=Problem.objects.all()
    wenjuan=sorted(wenjuan,key=lambda w: w.list,reverse=True)
    type_list=Conf.objects.get(key="wenjuan_type")
    type_list=json.loads(type_list.content)
    problem_list=Conf.objects.get(key="problem_list")
    problem_list=json.loads(problem_list.content)
    wj=[]
    for i in range(0,len(wenjuan)):

        wenjuan[i].type_text=type_list[wenjuan[i].type]
        wenjuan[i].option=option_list(wenjuan[i].id)
        n=problem_list.index(str(wenjuan[i].id))
        wj.insert(n,wenjuan[i])
        
    return wj 

def option_list(id):

    wj=ProblemInfo.objects.filter(problem_id=id)
    return wj

def getoption(id,_type):

   return  render_to_string("wenjuan_option.html", {
            'type': _type,
            'list': ProblemInfo.objects.filter(problem_id=id),
            "id":id
        })


def problem_edit(request):
    id=request.POST.get("id",None)
    name=request.POST.get("name","分页符")
    _type=request.POST.get("type",None)
    type_list=Conf.objects.get(key="wenjuan_type")
    type_list=json.loads(type_list.content)
    problem_list_obj=Conf.objects.get(key="problem_list")
    problem_list=json.loads(problem_list_obj.content)
    for i in range(0,len(type_list)):
        if _type == type_list[i]:
            _type=i
            break

    if id=="" :
        wj=Problem(dry=name,type=_type,status=True)
        wj.save()
        logging.error(sort)
        problem_list.append(str(wj.id))
        problem_list_obj.content=json.dumps(problem_list)
        problem_list_obj.save()
        # ["1","2","3","4","5","7","8"]
    else:
        wj=Problem.objects.get(id=id)
        wj.dry=name
        wj.type=_type
        wj.save()

    return HttpResponse(dialog('ok', 'success', '编辑成功！'))

def answer_edit(request):
    an_id=request.POST.get("an_id",None)
    dry_id=request.POST.get("dry_id",None)
    content=request.POST.get("content",None)
    if an_id=="" :
        pi=ProblemInfo(problem_id=dry_id,content=content,status=True)
    else:
        pi=ProblemInfo.objects.get(id=an_id)
        pi.content=content

    pi.save()
    return HttpResponse(dialog('ok', 'success', '编辑成功！'))

def option_del(request):
    id=request.POST.get("id",None)
    
    ProblemInfo.objects.get(id=id).delete()
    return HttpResponse(dialog('ok', 'success', '删除成功！'))

def problem_del(requerst):
    id=requerst.POST.get("id",None)
    ProblemInfo.objects.get(problem_id=id).delete()
    Problem.objects.get(id=id).delete()
    problem_list_obj=Conf.objects.get(key="problem_list")
    problem_list=json.loads(problem_list_obj.content)
    problem_list.remove(str(id))
    problem_list_obj.content=json.dumps(problem_list)
    problem_list_obj.save()
    return HttpResponse(dialog('ok', 'success', '删除成功！'))

@check_post
def save(request):
    username=request.POST.get("id",None)
    user = User.objects.filter(username=username)
    sql=''
    if len(user) == 0:
        obj = User(username=username, register_time=int(time.time()))
        id=obj.save()
    else:
        return HttpResponse(dialog('ok', 'success', '该id已有人使用，请更换id'))
    for p in request.POST.lists():
        if p[0] == "id":
            username=p[1]
            continue
        sql+="("+p[0]+","+id+",'"+p[1]+"'),"
        pass
    if sql == None:
        return HttpResponse(dialog('ok', 'success', '请填写问卷内容'))
    
    common.filter("INSERT INTO qiegaoworld_wenjuanlog (`problem_id`,`user_id`,`content`) values"+sql[0:len(sql)-1])
    return HttpResponse(dialog('ok', 'success', '提交成功！'))

def sort(request):
    for p in request.POST.lists():
        if p[0] == "list[]":
            problem_list=Conf.objects.get(key="problem_list")
            p[1].pop()
            if (problem_list) != None:
                problem_list.content=json.dumps(p[1])
            else:
                problem_list=Conf(key="problem_list",content=json.dumps(p[1]))
            problem_list.save()
            continue
    
    return HttpResponse(dialog('ok', 'success', '提交成功！'))