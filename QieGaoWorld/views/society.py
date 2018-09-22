

from django.http import HttpResponse
from django.shortcuts import render

from QieGaoWorld.views.decorator import check_post
from QieGaoWorld.views.decorator import check_login


from QieGaoWorld.models import Society

@check_login
@check_post
def url(request, s):
    return eval(s)(request)


def society_list():
    return Society.objects.all()


def society_info(request):
    id=request.POST.get("id",None)
    s=""
    if(id != None):
        s=Society.objects.get(id=id)

    return render(request, "dashboard/society/info.html", {"s":s,'edit': True,})