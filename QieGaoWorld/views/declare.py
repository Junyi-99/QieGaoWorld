import os
import logging
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
from QieGaoWorld.models import DeclareAnimals, DeclareBuildings
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

            path = default_storage.save(save_path, ContentFile(file_obj.read()))
            tmp_file = os.path.join(settings.MEDIA_ROOT, path)

            im = Image.open(tmp_file)
            width, height = im.size

            if width < height:
                print("resize")
                out = im.resize((width, width), Image.ANTIALIAS)
                out.save(tmp_file)
            else:
                out = im.resize((height, height), Image.ANTIALIAS)
                out.save(tmp_file)

        except Exception as e:
            logging.error(e)
            return HttpResponse(r'{"status": "failed", "msg": "Internal Server Error 服务器内部错误"}')

        return HttpResponse(r'{"status": "ok", "msg": "修改成功", "url":"static\\media\\%s"}' % save_path)
    else:
        return HttpResponse(r'{"status": "failed", "msg": "文件类型错误"}')


def buildings_change_status(request):
    try:
        id_ = int(request.POST.get('id', None))
        new_status = int(request.POST.get('status', None))
        username = request.session.get('username', None)
    except ValueError:
        return HttpResponse(r'{"status": "failed", "msg": "参数错误！"}')

    try:
        obj = DeclareBuildings.objects.get(id=id_)
        # 判断id为id_的动物是否属于当前用户，如果不属于，检查其是否是管理员
        if obj.username != username and '%declaration_buildings_modify%' \
                not in request.session.get('permissions', '%default%'):
            return HttpResponse(r'{"status": "failed", "msg": "权限不足！"}')

        if 0 <= new_status <= 5:
            obj.status = new_status
            obj.save()
            return HttpResponse(r'{"status": "ok", "msg": "更新建筑申报信息成功！刷新页面生效！"}')
        else:
            return HttpResponse(r'{"status": "failed", "msg": "状态值错误！"}')
    except MultipleObjectsReturned as e:
        logging.error(e)
        return HttpResponse(r'{"status": "failed", "msg": "内部错误！请联系管理员"}')
    except ObjectDoesNotExist:
        return HttpResponse(r'{"status": "failed", "msg": "可能这个动物不属于你！"}')


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
        logging.error(e)
        return HttpResponse(r'{"status": "failed", "msg": "内部错误！请联系管理员"}')
    except ObjectDoesNotExist:
        return HttpResponse(r'{"status": "failed", "msg": "可能这个动物不属于你！"}')


# operation 参数用来选择，是获取所有用户的obj，还是获取当前登录用户的obj
@check_login
@check_post
def buildings_list(request, operation):
    global buildings
    if 'all' in operation:
        buildings = DeclareBuildings.objects.all()
    elif 'user' in operation:
        buildings = DeclareBuildings.objects.filter(username=request.session.get('username', None))

    for i in range(0, len(buildings)):
        buildings[i].declare_time = time.strftime("%Y-%m-%d", time.localtime(buildings[i].declare_time))
        buildings[i].nickname = username_get_nickname(buildings[i].username)

        buildings[i].predict_start_time = time.strftime("%Y-%m-%d", time.localtime(buildings[i].predict_start_time))
        buildings[i].predict_end_time = time.strftime("%Y-%m-%d", time.localtime(buildings[i].predict_end_time))

        buildings[i].logo = buildings[i].concept

        if buildings[i].status == 0:
            buildings[i].status_label = 'uk-label-warning'
            buildings[i].status_text = '审核挂起'
        elif buildings[i].status == 1:
            buildings[i].status_label = 'uk-label-warning'
            buildings[i].status_text = '正在审核'
        elif buildings[i].status == 2:
            buildings[i].status_label = 'uk-label-danger'
            buildings[i].status_text = '审核不通过'
        elif buildings[i].status == 3:
            buildings[i].status_label = ''
            buildings[i].status_text = '审核通过'
        elif buildings[i].status == 4:
            buildings[i].status_label = ''
            buildings[i].status_text = '正在建设'
        elif buildings[i].status == 5:
            buildings[i].status_label = 'uk-label-success'
            buildings[i].status_text = '完工'
    return buildings


# operation 参数用来选择，是获取所有用户的obj，还是获取当前登录用户的obj
@check_login
@check_post
def animals_list(request, operation):
    global animals
    if 'all' in operation:
        animals = DeclareAnimals.objects.all()
    elif 'user' in operation:
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


# 添加一个建筑申报
@ensure_csrf_cookie
@check_login
@check_post
def buildings_add(request):
    try:
        arg_list = {'name', 'english_name', 'summary', 'detail', 'coordinate', 'area', 'predict_start_time',
                    'predict_end_time', 'type', 'pic_concept', 'pic_plan', 'pic_perspective'}

        lis = {key: str(request.POST.get(key, '')).strip() for key in arg_list}
        print(lis)
        print(lis['type'])
        lis['declare_time'] = int(time.time())
        lis['username'] = request.session.get('username', None)

        for l in lis:
            if len(str(lis[l])) == 0:
                return HttpResponse(r'{"status": "failed", "msg": "%s为空！请检查！"}' % l)

        obj = DeclareBuildings(
            declare_time=lis['declare_time'],
            username=lis['username'],
            coordinate=lis['coordinate'],
            area=lis['area'],
            concept=lis['pic_concept'],
            plan=lis['pic_plan'],
            name=lis['name'],
            english_name=lis['english_name'],
            summary=lis['summary'],
            detail=lis['detail'],
            perspective=lis['pic_perspective'],
            predict_start_time=time.mktime(time.strptime(lis['predict_start_time'], "%Y-%m-%d")),
            predict_end_time=time.mktime(time.strptime(lis['predict_end_time'], "%Y-%m-%d")),
            actually_end_time=0,
            status=0,
            type=int(str(lis['type'])),
        )
        obj.save()
        return HttpResponse(r'{"status": "ok", "msg": "申报成功！请等待管理员审核！"}')
    except ValueError as e:
        print(e)
        return HttpResponse(r'{"status": "failed", "msg": "数值错误！"}')
    except Exception as e:
        logging.error(e)
        return HttpResponse(r'{"status": "failed", "msg": "内部错误 -7 ！请联系管理员！"}')


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

        logging.debug("binding: " + binding)
        logging.debug("license: " + license_)
        logging.debug("feature: " + feature)
        logging.debug("status: " + str(status))

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
        logging.error(e)
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
