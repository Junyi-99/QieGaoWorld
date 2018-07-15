from django.core.exceptions import MultipleObjectsReturned, ObjectDoesNotExist
from django.http import HttpResponse
from django.shortcuts import render
from QieGaoWorld.models import DeclareAnimals
from django.views.decorators.csrf import ensure_csrf_cookie

from QieGaoWorld.views.decorator import check_post
from QieGaoWorld.views.decorator import check_login
from QieGaoWorld.views.police import username_get_nickname
import time


@ensure_csrf_cookie
@check_login
@check_post
def animals_change_status(request):
    try:
        id_ = int(request.POST.get('id', None))
        new_status = int(request.POST.get('new_status', None))
        username = request.session.get('username', None)
    except ValueError:
        return HttpResponse(r'{"status": "failed", "msg": "参数错误！"}')

    try:
        obj = DeclareAnimals.objects.get(id=id_)
        # 判断id为id_的动物是否属于当前用户，如果不属于，检查其是否是管理员
        if obj.username != username and '%declaration_animals_modify%' \
                not in request.session.get('permissions', '%default%'):
            return HttpResponse(r'{"status": "failed", "msg": "这个动物并不属于你，且你不是管理员！"}')

        if 0 <= new_status <= 3:
            obj.status = new_status
            obj.save()
            return HttpResponse(r'{"status": "ok", "msg": "更新动物信息成功！刷新页面生效！"}')
        else:
            return HttpResponse(r'{"status": "failed", "msg": "状态值错误！"}')
    except MultipleObjectsReturned as e:
        print(e)
        return HttpResponse(r'{"status": "failed", "msg": "内部错误！请联系管理员"}')
    except ObjectDoesNotExist:
        return HttpResponse(r'{"status": "failed", "msg": "可能这个动物不属于你！"}')


@check_login
@check_post
def animals_list(request):
    my_animals = []

    animals = DeclareAnimals.objects.all()
    for i in range(0, len(animals)):
        animals[i].declare_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(animals[i].declare_time))

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

        if request.session.get('username', None) == animals[i].username:
            my_animals.append(animals[i])
    return my_animals


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
        return HttpResponse(r'{"status": "ok", "msg": "更新成功！请重载当前页面！"}')
    except Exception as e:
        print(e)
        return HttpResponse(r'{"status": "failed", "msg": "内部错误"}')


# 检查牌照是否存在，存在返回True，不存在返回False
def animals_check_license_exist(license_):
    try:
        obj = DeclareAnimals.objects.get(license=license_)
        print(obj.username, obj.license)
        return True
    except MultipleObjectsReturned:
        return True
    except ObjectDoesNotExist:
        return False
