import time,datetime

from django.http import HttpResponse
from QieGaoWorld.views.decorator import check_post
from QieGaoWorld.views.decorator import check_login
from QieGaoWorld.views.dialog import dialog



from QieGaoWorld.models import Reward,RewardMx

@check_login
@check_post
def url(request, s):
    return eval(s)(request)

def reward_list(request):
    reward=Reward.objects.all()
    for i in range(0,len(reward)):
        if reward[i].mode == "0":
            reward[i].mode_text="无限制"
        elif reward[i].mode == "1":
            reward[i].mode_text="单人去重"
        elif reward[i].mode == "2":
            reward[i].mode_text="全局去重"

        if reward[i].release_mode == 0:
            reward[i].release_mode_text="每天"
        elif reward[i].release_mode == 1:
            reward[i].release_mode_text="每周"
        elif reward[i].release_mode == 2:
            reward[i].release_mode_text="每月"
        elif reward[i].release_mode == 3:
            reward[i].release_mode_text="每年"
        elif reward[i].release_mode == 4:
            reward[i].release_mode_text="周累计"
        elif reward[i].release_mode == 5:
            reward[i].release_mode_text="月累计"
        elif reward[i].release_mode == 6:
            reward[i].release_mode_text="年累计"
        elif reward[i].release_mode == 7:
            reward[i].release_mode_text="总累计"
        elif reward[i].release_mode == 8:
            reward[i].release_mode_text="自定义"
    return reward

def reward_add(request):
    name=request.POST.get("name","")
    if name == "":
        return HttpResponse(dialog('failed', 'danger', '请填写名称!'))
    start=request.POST.get("start","")
    end=request.POST.get("end","")
    # number=request.POST.get("number","")
    # if number == "":
    #     return HttpResponse(dialog('failed', 'danger', '请填写数量!'))
    mode=request.POST.get("mode","")
    reid=request.POST.get("reid","")
    if reid == "":
        return HttpResponse(dialog('failed', 'danger', '请填写奖品id!'))
    
    if (start != "" and end == "")  or (start == "" and end != ""):
        return HttpResponse(dialog('failed', 'danger', '请填写完整时间段!'))
    release_mode=request.POST.get("release_mode","")
    release_time=request.POST.get("release_time","")
    _id=request.POST.get("id","")
    if _id == "":
        reward=Reward(name=name,status=True,type="map",reward_id=reid,number=1,mode=mode,release_mode=release_mode,release_time=release_time)
    else:
        reward=Reward.objects.get(id=_id)
        reward.name=name
        reward.reward_id=reid 
        reward.number=number 
        reward.mode=mode 
        reward.release_mode=release_mode 
        reward.release_time=release_time 
    
    reward.save()
    return HttpResponse(dialog('ok', 'success', '添加成功!'))

    
def reward_del(request):
    if "%op%" not in request.session.get('permissions', ''):
        return HttpResponse(dialog('failed', 'danger', '权限不足!'))
    id=request.POST.get('id',None)
    reward=Reward.objects.get(id=id)
    
    reward.delete()
    return HttpResponse(dialog('ok', 'success', '删除成功!'))

def reward_status(request):
    if "%op%" not in request.session.get('permissions', ''):
        return HttpResponse(dialog('failed', 'danger', '权限不足!'))
    status=str( request.POST.get('status',None))
    id=request.POST.get('id',None)
    menu=Reward.objects.get(id=id)
    
    if(status == "True"):
        menu.status=False
    else:
        menu.status=True
    menu.save()
    return HttpResponse(dialog('ok', 'success', 'ok!'))