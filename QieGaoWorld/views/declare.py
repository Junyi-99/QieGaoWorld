import os
from PIL import Image
from django.core.files.base import ContentFile

from django.http import HttpResponse
from django.shortcuts import render

from django.views.decorators.csrf import ensure_csrf_cookie
from django.core.files.storage import default_storage
from django.core.exceptions import MultipleObjectsReturned, ObjectDoesNotExist
from QieGaoWorld.views.decorator import check_post
from QieGaoWorld.views.decorator import check_login
from QieGaoWorld.views.police import username_get_nickname
from QieGaoWorld.models import DeclareAnimals
from QieGaoWorld import settings
import time


def url(request, s):
    return eval(s)(request)


@check_post
@check_login
def upload_building_concept(request):
    return upload_building_picture(request, 'concept')


@check_post
@check_login
def upload_building_plan(request):
    return upload_building_picture(request, 'plan')


@check_post
@check_login
def upload_building_perspective(request):
    return upload_building_picture(request, 'perspective')


def upload_building_picture(request, upload_type):
    file_obj = request.FILES["files[]"]
    file_name = str(file_obj)

    pos = file_name.find(".")
    if pos == -1:
        return HttpResponse(r'{"status": "failed", "msg": "File type error."}')

    suffix = file_name[pos:]  # 取出后缀名

    allowed_type = [".jpg", ".png", ".jpeg", ".gif"]

    flag = False
    for eachType in allowed_type:
        if suffix.lower() == eachType:
            flag = True
            break

    if flag:
        try:
            save_path = "buildings/%s/%s_%d_%s" % (
                upload_type, request.session.get('username', 'N/A'), int(time.time()), file_name)
            print(save_path)

            path = default_storage.save(save_path, ContentFile(file_obj.read()))
            tmp_file = os.path.join(settings.MEDIA_ROOT, path)

            # im = Image.open(tmp_file)
        except Exception as e:
            print(e)
            return HttpResponse(r'{"status": "failed", "msg": "Internal Server Error 服务器内部错误"}')

        # out = im.resize((128, 128), Image.ANTIALIAS)
        # out.save(tmp_file)

        return HttpResponse(r'{"status": "ok", "msg": "修改成功</br>刷新页面后生效"}')
    else:
        return HttpResponse(r'{"status": "failed", "msg": "文件类型错误"}')


@ensure_csrf_cookie
@check_login
@check_post
def animals_change_status(request):
    try:
        id_ = int(request.POST.get('id', None))
        new_status = int(request.POST.get('status', None))
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

    animals = DeclareAnimals.objects.filter(username=request.session.get('username', None))
    for i in range(0, len(animals)):
        animals[i].declare_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(animals[i].declare_time))
        animals[i].nickname = username_get_nickname(animals[i].username)

        if animals[i].status == 0:
            animals[i].status_label = ''
            animals[i].status_text = '未知'
        elif animals[i].status == 1:
            animals[i].status_label = 'uk-label-success'
            animals[i].status_text = '存活'
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
