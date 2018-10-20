import os,traceback,uuid,logging
from PIL import Image
from django.core.files.base import ContentFile
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator

from django.http import HttpResponse
from django.shortcuts import render

from django.views.decorators.csrf import ensure_csrf_cookie
from django.core.files.storage import default_storage

# from nbt import nbt
from nbt.nbt import *
import   json
from django.core.exceptions import MultipleObjectsReturned, ObjectDoesNotExist
from QieGaoWorld.views.decorator import check_post
from QieGaoWorld.views.decorator import check_login
from QieGaoWorld.views.dialog import dialog
from QieGaoWorld.views.police import username_get_nickname,id_get_nickname
from QieGaoWorld.models import DeclareAnimals, DeclareBuildings,Conf,Maps,SkullCustomize
from QieGaoWorld import settings,common
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

    pos = file_name.rfind(".")
    if pos == -1:
        return HttpResponse(dialog('failed', 'danger', '文件类型错误'))

    suffix = file_name[pos:]  # 取出后缀名

    allowed_type = [".jpg", ".png", ".jpeg", ".gif"]

    flag = False
    for eachType in allowed_type:
        if suffix.lower() == eachType:
            flag = True
            break

    if flag:
        try:
            u = str(uuid.uuid1())
            save_path = "buildings/%s/%s" % (upload_type, u + ".png")
            thumb_path = "buildings/%s/%s_thumb" % (upload_type, u )+ ".png"

            path = default_storage.save(save_path, ContentFile(file_obj.read()))
            path_thu = default_storage.save(thumb_path, ContentFile(file_obj.read()))

            tmp_file = os.path.join(settings.MEDIA_ROOT, path)
            thu_file = os.path.join(settings.MEDIA_ROOT, path_thu)

            im = Image.open(tmp_file)
            width, height = im.size

            # resize 一下，破坏PE文件后面的附属信息（防止被当作图床）
            out = im.resize((width - 1, height - 1), Image.ANTIALIAS)
            out.save(tmp_file)

            make_thumb(tmp_file, thu_file)
            # if width < height:
            #     print("resize")
            #     out = im.resize((width, width), Image.ANTIALIAS)
            #     out.save(tmp_file)
            # else:
            #     out = im.resize((height, height), Image.ANTIALIAS)
            #     out.save(tmp_file)

        except Exception as e:
            logging.error(e)
            return HttpResponse(dialog('failed', 'danger', '文件类型错误，请联系管理员'))

        return HttpResponse(dialog('ok', 'success', '修改成功', {'url': "static/media/%s" % save_path}))
    else:
        return HttpResponse(dialog('failed', 'danger', '文件类型错误'))


def buildings_change_status(request):
    try:
        id_ = int(request.POST.get('id', None))
        new_status = int(request.POST.get('status', None))
        username = request.session.get('username', None)
    except ValueError:
        return HttpResponse(dialog('failed', 'danger', '参数错误'))

    try:
        obj = DeclareBuildings.objects.get(id=id_)
        # 1、检查是否是当前用户的状态为“审核通过”的建筑，再检查修改状态是否为“正在建设”和“完工”  如果不是，检查是否是管理员
        if (obj.username != username or obj.status not in [3,4] or new_status not in [4,5]) and '%declaration_buildings_modify%' not in request.session.get('permissions', '%default%')  :
            return HttpResponse(dialog('failed', 'danger', '权限不足'))

        if 0 <= new_status <= 6:
            old_status=obj.status
            obj.status = new_status
            obj.save()
            common.logs("用户:%s(%d) 将建筑申请：%s(id:%s,user:%s)状态由%s更改为%s" % (request.session['username'],request.session['id'],obj.name,obj.id,obj.username,old_status,str(new_status)),"建筑申报管理")
            return HttpResponse(dialog('ok', 'success', '更新建筑申报信息成功！刷新页面生效！'))
        else:
            return HttpResponse(dialog('failed', 'danger', '状态值错误'))
    except MultipleObjectsReturned as e:
        logging.error(e)
        return HttpResponse(dialog('failed', 'danger', '内部错误，请联系管理员'))
    except ObjectDoesNotExist:
        return HttpResponse(dialog('failed', 'danger', '可能这个建筑不属于你！'))

@check_login
def buildings_del(request):
    try:
        id_ = int(request.POST.get('id', None))
        username = request.session.get('username', None)
    except ValueError:
        return HttpResponse(dialog('failed', 'danger', '参数错误'))

    try:
        obj = DeclareBuildings.objects.get(id=id_)
        # 1、检查是否是当前用户的状态为“审核不通过”的建筑
        if  (obj.username != username or obj.status != 2 ) :
            return HttpResponse(dialog('failed', 'danger', '权限不足'))

        obj.delete()
        common.logs("用户:%s(%d) 删除建筑申请：%s(id:%s,user:%s)" % (request.session['username'],request.session['id'],obj.name,obj.id,obj.username),"建筑申报管理")
        return HttpResponse(dialog('ok', 'success', '更新建筑申报信息成功！刷新页面生效！'))
    except MultipleObjectsReturned as e:
        logging.error(e)
        return HttpResponse(dialog('failed', 'danger', '内部错误，请联系管理员'))
    except ObjectDoesNotExist:
        return HttpResponse(dialog('failed', 'danger', '可能这个建筑不属于你！'))

@check_login
def animals_del(request):
    try:
        id_ = int(request.POST.get('id', None))
        username = request.session.get('username', None)
    except ValueError:
        return HttpResponse(dialog('failed', 'danger', '参数错误'))

    try:
        obj =  DeclareAnimals.objects.get(id=id_)
        # 1、检查是否是当前用户的状态为“审核不通过”的建筑
        if  not (obj.username == username or ('%op%' in request.session.get('permissions', '%default%') ) ) :
            return HttpResponse(dialog('failed', 'danger', '可能这个牌照不属于你！'))

        obj.delete()
        common.logs("用户:%s(%d) 删除了牌照：%s(id:%s,user:%s)" % (request.session['username'],request.session['id'],obj.license,obj.id,obj.username),"动物牌照管理")
        return HttpResponse(dialog('ok', 'success', '更新动物牌照成功！刷新页面生效！'))
    except MultipleObjectsReturned as e:
        logging.error(e)
        return HttpResponse(dialog('failed', 'danger', '内部错误，请联系管理员'))
    except ObjectDoesNotExist:
        return HttpResponse(dialog('failed', 'danger', '可能这个牌照不属于你！'))

@ensure_csrf_cookie
@check_login
@check_post
def animals_change_status(request):
    try:
        id_ = int(request.POST.get('id', None))
        new_status = int(request.POST.get('status', None))
        username = request.session.get('username', None)
    except ValueError:
        return HttpResponse(dialog('failed', 'danger', '参数错误'))

    try:
        obj = DeclareAnimals.objects.get(id=id_)
        # 判断id为id_的动物是否属于当前用户，如果不属于，检查其是否是管理员
        if obj.username != username and '%declaration_animals_modify%' \
                not in request.session.get('permissions', '%default%'):
            return HttpResponse(dialog('failed', 'danger', '这个动物并不属于你'))

        if 0 <= new_status <= 3:
            old_status=obj.status
            obj.status = new_status
            obj.save()
            common.logs("用户:%s(%d) 将动物信息：%s(id:%s,user:%s)状态由%s更改为%s" % (request.session['user'],request.session['id'],obj.license,obj.id,obj.username,old_status,str(new_status)),"动物申报管理")
            return HttpResponse(dialog('ok', 'success', '更新动物信息成功！刷新页面生效！'))
        else:
            return HttpResponse(dialog('failed', 'danger', '状态值错误'))
    except MultipleObjectsReturned as e:
        logging.error(e)
        return HttpResponse(dialog('failed', 'danger', '内部错误，请联系管理员'))
    except ObjectDoesNotExist:
        return HttpResponse(dialog('failed', 'danger', '这个动物并不属于你'))


# 创建缩略图 pic 为原始图片地址, path_ 为目标缩略图存放地址
def make_thumb(pic_, path_):
    try:
        im = Image.open(settings.BASE_DIR+"/"+ pic_)
        out = im.resize((40, 40), Image.ANTIALIAS)  # 缩略图大小为40x40
        out.save(settings.BASE_DIR+"/"+path_)
    except Exception as e:
        logging.error(e)


# operation 参数用来选择，是获取所有用户的obj，还是获取当前登录用户的obj
@check_login
@check_post
def buildings_list(request):
    # global buildings
    operation="all"
    if 'all' in operation:
        buildings = DeclareBuildings.objects.order_by("-declare_time").all()
    elif 'user' in operation:
        buildings = DeclareBuildings.objects.order_by("-declare_time").filter(username=request.session.get('username', None))

    # 按照时间由新到旧排序
    # buildings = sorted(buildings, key=lambda b: b.declare_time, reverse=True)
    page=request.POST.get("page",1)
    paginator = Paginator(buildings, 25)
    buildings=paginator.get_page(page)
    for i in range(0, len(buildings)):
        buildings[i].declare_time = time.strftime("%Y-%m-%d", time.localtime(buildings[i].declare_time))
        buildings[i].nickname = username_get_nickname(buildings[i].username)

        buildings[i].predict_start_time = time.strftime("%Y-%m-%d", time.localtime(buildings[i].predict_start_time))
        buildings[i].predict_end_time = time.strftime("%Y-%m-%d", time.localtime(buildings[i].predict_end_time))

        # 设置logo为缩略图的路径
        logo = buildings[i].concept
        
        pos = logo.rfind(".")
        if pos == -1:
            return []
        buildings[i].logo = logo[:pos] + '_thumb' + logo[pos:]

        # 如果缩略图不存在，我们创建
        
        if not os.path.exists(buildings[i].logo):
            make_thumb(buildings[i].concept, buildings[i].logo)

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
        elif buildings[i].status == 6:
            buildings[i].status_label = 'uk-label-danger'
            buildings[i].status_text = '弃坑'
    # return buildings
    return render(request, 'dashboard/declaration/building_list.html', {'permissions': request.session['permissions'],'buildings': buildings,"page":common.page("declare/buildings_list",buildings)})


# operation 参数用来选择，是获取所有用户的obj，还是获取当前登录用户的obj
@check_login
@check_post
def animals_list(request):
    global animals
    operation='all'
    if 'all' in operation:
        animals = DeclareAnimals.objects.order_by("-declare_time").all()
    elif 'user' in operation:
        animals = DeclareAnimals.objects.order_by("-declare_time").filter(username=request.session.get('username', None)) 

    # 按照时间由新到旧排序
    # animals = sorted(animals, key=lambda a: a.declare_time, reverse=True)
    page=request.POST.get("page",1)
    paginator = Paginator(animals, 25)
    animals=paginator.get_page(page)
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

    return render(request, 'dashboard/declaration/animals_list.html', {'permissions': request.session['permissions'],'animals': animals,"page":common.page("declare/animals_list",animals)})
    


# 添加一个建筑申报
@ensure_csrf_cookie
@check_login
@check_post
def buildings_add(request):
    try:
        arg_list = {'name', 'english_name', 'summary', 'detail', 'coordinate', 'area', 'predict_start_time',
                    'predict_end_time', 'type', 'pic_concept', 'pic_plan'}

        lis = {key: str(request.POST.get(key, '')).strip() for key in arg_list}
        print(lis)
        print(lis['type'])
        lis['declare_time'] = int(time.time())
        lis['username'] = request.session.get('username', None)

        for l in lis:
            if len(str(lis[l])) == 0:
                return HttpResponse(dialog('failed', 'danger', '%s为空！请检查！' % l))
        lis['pic_perspective'] = str(request.POST.get('pic_perspective', '')).strip()
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
            status=1,
            type=int(str(lis['type'])),
        )
        obj.save()
        return HttpResponse(dialog('ok', 'success', '申报成功！请等待管理员审核！'))
    except ValueError as e:
        print(e)
        return HttpResponse(dialog('failed', 'danger', '数值错误'))
    except Exception as e:
        logging.error(e)
        return HttpResponse(dialog('failed', 'danger', '内部错误，请联系管理员'))


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
            return HttpResponse(dialog('failed', 'danger', '牌照号不能为空'))
        if len(feature) == 0:
            return HttpResponse(dialog('failed', 'danger', '特征不能为空'))

        try:
            binding = int(str(request.POST.get('binding', None)).strip())
            status = int(str(request.POST.get('status', None)).strip())
        except ValueError:
            return HttpResponse(dialog('failed', 'danger', '数值错误'))

        if animals_check_license_exist(license_):
            return HttpResponse(dialog('failed', 'danger', '牌照已存在'))

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
        return HttpResponse(dialog('ok', 'success', '更新成功'))
    except Exception as e:
        logging.error(e)
        return HttpResponse(dialog('failed', 'danger', '内部错误，请联系管理员'))


# 检查牌照是否存在，存在返回True，不存在返回False
def animals_check_license_exist(license_):
    try:
        obj = DeclareAnimals.objects.get(license=license_)
        return True
    except MultipleObjectsReturned:
        return True
    except ObjectDoesNotExist:
        return False


@ensure_csrf_cookie
def buildings_detail(request):
    error_msg = '<div class="uk-modal-header"><h2 class="uk-modal-title" style="color: #cc3947">%s</h2></div>'

    if '%declaration_watch%' not in request.session.get('permissions', ''):
        return HttpResponse(error_msg % "您没有查看建筑详情的权限！")

    try:
        id_ = int(request.GET.get('id', None))
    except ValueError:
        return HttpResponse(error_msg % "参数错误！")

    try:
        obj = DeclareBuildings.objects.get(id=id_)
        obj.declare_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(int(obj.declare_time)))
        obj.predict_start_time = time.strftime("%Y-%m-%d", time.localtime(int(obj.predict_start_time)))
        obj.predict_end_time = time.strftime("%Y-%m-%d", time.localtime(int(obj.predict_end_time)))
        obj.nickname = username_get_nickname(obj.username)
        if obj.type == 0:
            obj.type = '公共建筑'
        else:
            obj.type = '私有建筑'

        if obj.status == 0:
            obj.status_label = 'uk-label-warning'
            obj.status_text = '审核挂起'
        elif obj.status == 1:
            obj.status_label = 'uk-label-warning'
            obj.status_text = '正在审核'
        elif obj.status == 2:
            obj.status_label = 'uk-label-danger'
            obj.status_text = '审核不通过'
        elif obj.status == 3:
            obj.status_label = ''
            obj.status_text = '审核通过'
        elif obj.status == 4:
            obj.status_label = ''
            obj.status_text = '正在建设'
        elif obj.status == 5:
            obj.status_label = 'uk-label-success'
            obj.status_text = '完工'
        return render(request, "dashboard/declaration/building_detail.html", {'building': obj})
    except MultipleObjectsReturned as e:
        logging.error(e)
        return HttpResponse(error_msg % "内部错误，请联系管理员！")
    except ObjectDoesNotExist:
        return HttpResponse(error_msg % "建筑不存在！")

def maps_add(request):

    data=request.POST.get("data",None)
    _height=int(request.POST.get("height",1))
    _width=int(request.POST.get("width",1))
    if data == None:
        return HttpResponse(dialog('failed', 'danger', '请上传图片'))
    
    maps=data.split(";")
    map=[]
    for m in maps:
        a=m.split(":")
        if len(a)<2:
            continue
        map.insert(int(a[0]),json.loads(a[1]))
    conf=Conf.objects.filter(key="maps_path")
    if len(conf) == 0:
        return HttpResponse(dialog('failed', 'danger', '请联系管理员配置地图路径'))
    path=conf[0].content
    conf=Conf.objects.filter(key="maps_default_number")
    if len(conf) == 0:
        return HttpResponse(dialog('failed', 'danger', '请联系管理员配置基础编号'))
    
    number=int(conf[0].content)
    if not os.path.exists(path+"map_%d.dat"%number):
        return HttpResponse(dialog('failed', 'danger', '基础地图不存在，请联系管理员修改'))
    nbt =NBTFile(path+"map_%d.dat"%number)
    for a in map:
        all_maps_data=a
        map_item=[]
        for k in range(0,128):
            for l in range(0,128):
                co = all_maps_data[l +  128 * k]
                if (co<0) :
                    co = co + 256
                map_item.append(co)

        nbt['data']['colors'].value=(map_item)
        
        number=get_map_id(path,number)
        if not number:
            return HttpResponse(dialog('failed', 'success', '编号生成失败'))
        im2=Image.new("RGB",(128,128))
        
        
            
        
        im2.putdata(common.genimage(map_item),0,0)
        if not os.path.exists(os.path.join(settings.MEDIA_ROOT, "maps")):
            os.mkdir(os.path.join(settings.MEDIA_ROOT, "maps"))
        im2=im2.resize((64,64))
        im2.save(os.path.join(settings.MEDIA_ROOT, "maps/maps_%d.jpg"%number),"JPEG")

        nbt.write_file(path+("map_%d.dat"%number))
        
        maps=Maps(username=request.session['username'],mapid=number,status=False,img="static/media/maps/maps_%d.jpg"%number)
        maps.save()
            
    return HttpResponse(dialog('ok', 'success', '添加成功'))

@check_login
@check_post
def maps_list(request):
    operation=request.POST.get("type","user");
    if 'all' in operation and "%op%" in request.session.get("permissions",""):
        maps = Maps.objects.order_by("-id")
    elif 'user' in operation:
        maps = Maps.objects.filter(username=request.session.get('username', None)).order_by("-id")
    page=request.POST.get("page",1)
    paginator = Paginator(maps, 25)
    maps=paginator.get_page(page)
    # maps=sorted(maps, key=lambda a: a.declare_time, reverse=True)
    for i in range(0, len(maps)):
        maps[i].nickname = username_get_nickname(maps[i].username)

        if maps[i].status:
            maps[i].status_label = 'uk-label-success'
            maps[i].status_text = '已领取'
        else:
            maps[i].status_label = ''
            maps[i].status_text = '未领取'

    return render(request, 'dashboard/declaration/maps_list.html', {'permissions': request.session['permissions'],'list': maps,"page":common.page("declare/maps_list",maps)})
    
def get_map_id(path,number):
    while os.path.exists(path+"map_%d.dat"%number):
        number+=1
        if number >9999:
            return false

    return number

@check_login
def maps_del(request):
    try:
        id_ = int(request.POST.get('id', None))
        username = request.session.get('username', None)
    except ValueError:
        return HttpResponse(dialog('failed', 'danger', '参数错误'))

    try:
        obj =  Maps.objects.get(id=id_)
        # 1、检查是否是当前用户的状态为“审核不通过”的建筑
        if  not (obj.username == username or ('%op%' in request.session.get('permissions', '%default%') ) ) :
            return HttpResponse(dialog('failed', 'danger', '可能这条记录不属于你！'))
        if obj.status:
            return HttpResponse(dialog('failed', 'danger', '已领取地图画无法删除！'))
        if  os.path.exists(os.path.join(os.getcwd(),obj.img)):
            os.unlink(os.path.join(os.getcwd(),obj.img))
        obj.delete()
        common.logs("用户:%s(%d) 删除了地图画：%s(id:%s,user:%s)" % (request.session['username'],request.session['id'],obj.mapid,obj.id,obj.username),"地图画管理")
        return HttpResponse(dialog('ok', 'success', '删除地图画成功'))
    except MultipleObjectsReturned as e:
        logging.error(e)
        return HttpResponse(dialog('failed', 'danger', '内部错误，请联系管理员'))
    except ObjectDoesNotExist:
        return HttpResponse(dialog('failed', 'danger', '可能这条记录不属于你！'))



def skull_del(request):
    id=request.POST.get('id',None)
    menu=SkullCustomize.objects.get(id=id,user_id=request.session['id'])
    
    menu.delete()
    return HttpResponse(dialog('ok', 'success', '删除成功!'))

def skull_add(request):
    try:
        name=request.POST.get('name',None)
        number=int(request.POST.get('number',None))
        content=request.POST.get("content",None)
    except ValueError:
        return HttpResponse(dialog('failed', 'danger', '参数错误'))

    info=re.search(r'Id:"[\d\w-]+',content)
    if info==None or info.group()==None or len(info.group())<4 :
        return HttpResponse(dialog('failed', 'danger', '头颅代码格式错误'))
    id=info.group()[4:]
    info=re.search(r'Value:"[\d\w]+',content)
    if info==None or info.group()==None or len(info.group())<7 :
        return HttpResponse(dialog('failed', 'danger', '头颅代码格式错误'))
    value=info.group()[7:]

    menu=SkullCustomize(name=name,user_id=int(request.session['id']),number=number,status=False,content=id+':'+value)
    menu.save()
    return HttpResponse(dialog('ok', 'success', '添加成功!'))

def skull_list(request,_all=False):
    if _all:
        skull=SkullCustomize.objects.all()
    else:
        skull=SkullCustomize.objects.filter(user_id=request.session['id'])

    page=request.POST.get("page",1)
    paginator = Paginator(skull, 25)
    skull=paginator.get_page(page)
    for i in range(0,len(skull)) :
        if skull[i].status:
            skull[i].status_class="uk-label-success"
            skull[i].status_text="已取货"
        else:
            skull[i].status_class=""
            skull[i].status_text="未取货"
        skull[i].nickname=id_get_nickname(skull[i].user_id)

    return render(request, 'dashboard/declaration/skull_list.html', {'permissions': request.session['permissions'],'list': skull,"page":common.page("declare/skull_list",skull)})