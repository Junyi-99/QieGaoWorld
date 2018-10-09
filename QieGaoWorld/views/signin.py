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
        if reward[i].mode == 0:
            reward[i].mode_text="无限制"
        elif reward[i].mode == 1:
            reward[i].mode_text="单人去重"
        elif reward[i].mode == 2:
            reward[i].mode_text="全局去重"
    return reward

def reward_add(request):
    name=request.POST.get("name","")
    if name == "":
        return HttpResponse(dialog('failed', 'danger', '请填写名称!'))
    start=request.POST.get("start","")
    end=request.POST.get("end","")
    number=request.POST.get("number","")
    if number == "":
        return HttpResponse(dialog('failed', 'danger', '请填写数量!'))
    mode=request.POST.get("mode","")
    _id=request.POST.get("id","")
    id_array=[]
    if _id == "":
        return HttpResponse(dialog('failed', 'danger', '请填写奖品id!'))
    
    if (start != "" and end == "")  or (start == "" and end != ""):
        return HttpResponse(dialog('failed', 'danger', '请填写完整时间段!'))

    reward=Reward(name=name,status=True,count=len(id_array),type="map",reward_id=_id,number=number,mode=mode)
    reward.save()
    return HttpResponse(dialog('ok', 'success', '添加成功!'))

    
