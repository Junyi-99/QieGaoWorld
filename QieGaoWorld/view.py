from django.http import HttpResponse
from django.shortcuts import render
from django.views.decorators.csrf import requires_csrf_token
from django.views.decorators.csrf import ensure_csrf_cookie
from django.conf import settings

import json
import time
from .views.decorator import check_login, check_post


def global_settings(request):
    return {"PROJECT_VERSION": settings.PROJECT_VERSION,
            'PROJECTVERSION': settings.PROJECT_VERSION}


def admin_dashboard(request):
    pass
    context = {}
    return render(request, "admin/login.html", context)


@check_post
def admin_login_verify(request):
    username = str(request.POST.get("username", None)).encode("utf-8")
    password = str(request.POST.get("password", None)).encode("utf-8")

    if username != b"Junyi":
        return HttpResponse(r'{"status": "failed", "msg": "Access denied.1"}')
    if password != b"houjunyi12797848":
        return HttpResponse(r'{"status": "failed", "msg": "Access denied.2"}')

    request.session["admin_is_login"] = True
    request.session.set_expiry(3600)  # 1小时有效期
    return HttpResponse(r'{"status": "ok", "msg": "Login Successfully."}')


def admin(request):
    context = {}
    return render(request, "admin/login.html", context)


@check_post
@check_login
def save_changes(request):
    pass

    type = str(request.POST.get("type", None))

    if ("settings_meo" in type):

        nickname = str(request.POST.get("nickname", "N/A"))
        qqnumber = str(request.POST.get("qqnumber", "N/A"))
        email = str(request.POST.get("email", "N/A"))
        sex = str(request.POST.get("sex", "N/A"))

        flag = False

        if "N/A" in nickname:
            flag = True
        if "N/A" in qqnumber:
            flag = True
        if "N/A" in email:
            flag = True
        if "N/A" in sex:
            flag = True

        if flag:
            return HttpResponse(r'{"status": "failed", "msg": "项目出错 或 包含非法字符：“N/A” "}')

        decode = json.loads(get_userdata_json(request))
        decode["nickname"] = nickname
        decode["qqnumber"] = qqnumber
        decode["email"] = email
        decode["sex"] = sex
        print(decode)
        if set_userdata_json(request, json.dumps(decode)):
            return HttpResponse(r'{"status": "ok", "msg": "保存成功"}')
        else:
            return HttpResponse(r'{"status": "failed", "msg": "保存失败"}')

    return HttpResponse(r'{"status": "failed", "msg": "未经处理的保存"}')


def handle_uploaded_file(f):
    print("Name")
    print(f.name)
    with open(f.name, "wb+") as destination:
        for chunk in f.chunks():
            destination.write(chunk)


def dashboard_page_cards_add(request):
    context = {}
    return context


def dashboard_page_cards_list(request):
    context = {}
    return context


def dashboard_page_settings_meo(request):
    username = request.session.get('username', 'N/A')
    nickname = request.session.get('nickname', 'N/A')
    qqnumber = request.session.get('qqnumber', 'N/A')
    avatar = request.session.get('avatar', 'static\\face\\default.jpg')
    register_time = request.session.get('register_time', 0)
    register_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(register_time))

    context = {
        'username': username,
        'nickname': nickname,
        'qqnumber': qqnumber,
        'register_time': register_time,
        'avatar': avatar
    }
    return context


def user_center(request):
    try:
        from mcstatus import MinecraftServer

        server_address = 'mc.qiegaoshijie.club:21182'

        server = MinecraftServer.lookup(server_address)
        status = server.status()

        latency = server.ping()
        mot = status.description['text']
        motd = str(mot)
        pos = motd.find('§')
        while pos != -1:
            motd = motd[:pos] + motd[pos + 2:]
            pos = motd.find('§')

        ver = status.version.name
        fav = status.favicon
        mpn = status.players.max
        opn = status.players.online
        user = []

        for e in status.players.sample:
            user.append({'name': e.name, 'id': e.id})

        context = {
            'motd': motd,
            'favicon': fav,
            'version': ver,
            'server_address': server_address,
            'max_players_number': mpn,
            'online_players_list': user,
            'online_players_number': opn,
            'ping': latency,
        }
        print(context)
    except Exception:
        context = {}

    return render(request, "dashboard/user_center.html", context)


def page_announcement(request):
    pass

    import requests

    # data = {
    #     'j_username': request.session["username"],
    #     'j_password': request.session["password"]
    # }
    # ret = requests.post('http://map.qiegaoshijie.club/up/login', data)
    # print(ret.text)
    # print(ret.cookies['JSESSIONID'])
    # response = render_to_response("dashboard/map.html", {})
    # #P3P Header
    # response["P3P"] = 'CP="CAO PSA OUR"'
    # response.set_cookie(key='JSESSIONID', value=ret.cookies['JSESSIONID'], domain='map.qiegaoshijie.club', path='/')
    return render(request, "dashboard/announcement/announcement.html", {})


def page_declaration_center(request):
    return render(request, "dashboard/declaration/center.html", {})


def page_call_the_police(request):
    return render(request, "dashboard/police/call_the_police.html", {})



@ensure_csrf_cookie
@check_login
@check_post
def dashboard_page(request):
    ensure_csrf_cookie(request)

    if request.POST.get("page", None) == "user_center":
        return user_center(request)

    if request.POST.get("page", None) == "announcement":
        return page_announcement(request)

    if request.POST.get("page", None) == "news":
        return render(request, "dashboard/settings/account.html", dashboard_page_settings_meo(request))

    if request.POST.get("page", None) == "papers":
        return render(request, "dashboard/cards/card_list.html", dashboard_page_cards_list(request))

    if request.POST.get("page", None) == "project_plan":
        return render(request, "dashboard/cards/card_add.html", dashboard_page_cards_add(request))

    if request.POST.get("page", None) == "community":
        return render(request, "dashboard/settings/account.html", dashboard_page_settings_meo(request))

    if request.POST.get("page", None) == "declaration_center":
        return page_declaration_center(request)

    if request.POST.get("page", None) == "declare_buildings":
        return render(request, "dashboard/declaration/buildings.html", {})

    if request.POST.get("page", None) == "declare_animals":
        return render(request, "dashboard/declaration/animals.html", {})

    if request.POST.get("page", None) == "police_hall":
        return render(request, "dashboard/police/police_hall.html", {})

    if request.POST.get("page", None) == "call_the_police":
        return render(request, "dashboard/police/call_the_police.html", {})

    if request.POST.get("page", None) == "world_map":
        return render(request, "dashboard/world_map/map.html", {})

    if request.POST.get("page", None) == "rookies":
        return render(request, "dashboard/cards/card_list.html", dashboard_page_cards_list(request))

    if request.POST.get("page", None) == "settings":
        return render(request, "dashboard/cards/card_add.html", dashboard_page_cards_add(request))

    return HttpResponse("Response: " + request.POST.get("page", None))


@check_login
def dashboard(request):
    context = {
        'avatar': request.session['avatar'],
        'nickname': request.session['nickname']
    }

    return render(request, "dashboard/dashboard.html", context)


def agreement(request):
    return render(request, "agreement.html", {})


def forgotten(request):
    return render(request, "forgotten.html", {})
