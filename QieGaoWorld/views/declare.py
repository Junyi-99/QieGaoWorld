from django.core.exceptions import MultipleObjectsReturned, ObjectDoesNotExist
from django.http import HttpResponse
from django.shortcuts import render
from QieGaoWorld.models import DeclareAnimals
from django.views.decorators.csrf import ensure_csrf_cookie

from QieGaoWorld.views.decorator import check_post
from QieGaoWorld.views.decorator import check_login
from QieGaoWorld.views.police import username_get_nickname
import time


def url(request,s):
    return eval(s)(request)



@check_login
@check_post
def animals_list(request):
    my_animals = []

    animals = DeclareAnimals.objects.filter(username=request.session.get('username', None))
    for i in range(0, len(animals)):
        animals[i].declare_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(animals[i].declare_time))
        animals[i].username=username_get_nickname(animals[i].username)

        if animals[i].status == 0:
            animals[i].status_label = ''
            animals[i].status_text = '未知'
        elif animals[i].status == 1:
            animals[i].status_label = 'uk-label-success'
            animals[i].status_text = '正常'
        elif animals[i].status == 2:
            animals[i].status_label = 'uk-label-warning'
            animals[i].status_text = '丢失'
        elif animals[i].status == 3:
            animals[i].status_label = 'uk-label-danger'
            animals[i].status_text = '死亡'

    return animals


@ensure_csrf_cookie
@check_login
@check_post
def animals_add(request):
    try:
        declare_time = int(time.time())
        username = request.session.get('username', None)

        license_ = str(request.POST.get('license', None)).strip()
        feature = str(request.POST.get('feature', None)).strip()

        if len(license_) == 0:
            return HttpResponse(r'{"status": "failed", "msg": "牌照号不能为空！"}')
        if len(feature) == 0:
            return HttpResponse(r'{"status": "failed", "msg": "特征不能为空！"}')

        try:
            binding = int(str(request.POST.get('binding', None)).strip())
            status = int(str(request.POST.get('status', None)).strip())
        except ValueError:
            return HttpResponse(r'{"status": "failed", "msg": "数值错误！"}')

        if animals_check_license_exist(license_):
            return HttpResponse(r'{"status": "failed", "msg": "牌照已存在！"}')

        if binding == 0:
            binding = username_get_nickname(username)
        else:
            binding = '公共'

        print("binding: " + binding)
        print("license: " + license_)
        print("feature: " + feature)
        print("status: " + str(status))

        obj = DeclareAnimals(
            declare_time=declare_time,
            username=username,
            binding=binding,
            license=license_,
            feature=feature,
            status=status
        )
        obj.save()
        return HttpResponse(r'{"status": "ok", "msg": "更新成功！"}')
    except Exception as e:
        print(e)
        return HttpResponse(r'{"status": "failed", "msg": "内部错误"}')


# 检查牌照是否存在，存在返回True，不存在返回False
def animals_check_license_exist(license_):
    try:
        obj = DeclareAnimals.objects.get(license=license_)
        return True
    except MultipleObjectsReturned:
        return True
    except ObjectDoesNotExist:
        return False


def animals_change_status(request):
    try:
        try:
            id = int(str(request.POST.get('id', None)).strip())
            status = int(str(request.POST.get('status', None)).strip())
        except ValueError:
            return HttpResponse(r'{"status": "failed", "msg": "数值错误！"}')

        obj = DeclareAnimals.objects.get(id=id)
        obj.status=status
        obj.save()
        return HttpResponse(r'{"status": "ok", "msg": "更新成功！"}')
    except Exception as e:
        print(e)
        return HttpResponse(r'{"status": "failed", "msg": "内部错误"}')