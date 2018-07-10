from django.http import HttpResponse
from django.shortcuts import render
from django.views.decorators.csrf import requires_csrf_token
from django.views.decorators.csrf import ensure_csrf_cookie
from django.conf import settings

import json
import time
from .views.decorator import check_login, check_post
from .views.police import police_hall
from .views.settings import page_settings


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

    if username != b"root":
        return HttpResponse(r'{"status": "failed", "msg": "Access denied.1"}')
    if password != b"admin":
        return HttpResponse(r'{"status": "failed", "msg": "Access denied.2"}')

    request.session["admin_is_login"] = True
    request.session.set_expiry(3600)  # 1小时有效期
    return HttpResponse(r'{"status": "ok", "msg": "Login Successfully."}')


def admin(request):
    context = {}
    return render(request, "admin/login.html", context)


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


@check_login
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

    context['permissions'] = request.session['permissions']
    # context['permissions'] = '%publish_announcement% %call_the_police%'
    return render(request, "dashboard/user_center.html", context)


@check_login
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


@check_login
def page_declaration_center(request):
    return render(request, "dashboard/declaration/center.html", {})


@check_login
def page_call_the_police(request):
    return render(request, "dashboard/police/call_the_police.html", {})


@ensure_csrf_cookie
@check_login
@check_post
def dashboard_page(request):
    ensure_csrf_cookie(request)
    print(request.POST.get("page", None))

    if request.POST.get("page", None) == "user_center":
        return user_center(request)

    if request.POST.get("page", None) == "announcement":
        return page_announcement(request)

    if request.POST.get("page", None) == "news":
        return render(request, "dashboard/settings/account.html", {})

    if request.POST.get("page", None) == "papers":
        return render(request, "dashboard/cards/card_list.html", dashboard_page_cards_list(request))

    if request.POST.get("page", None) == "project_plan":
        return render(request, "dashboard/cards/card_add.html", dashboard_page_cards_add(request))

    if request.POST.get("page", None) == "community":
        return render(request, "dashboard/settings/account.html", {})

    if request.POST.get("page", None) == "declaration_center":
        return page_declaration_center(request)

    if request.POST.get("page", None) == "declare_buildings":
        return render(request, "dashboard/declaration/buildings.html", {})

    if request.POST.get("page", None) == "declare_animals":
        return render(request, "dashboard/declaration/animals.html", {})

    if request.POST.get("page", None) == "police_hall":
        return police_hall(request)

    if request.POST.get("page", None) == "call_the_police":
        return render(request, "dashboard/police/call_the_police.html", {})

    if request.POST.get("page", None) == "world_map":
        return render(request, "dashboard/world_map/map.html", {})

    if request.POST.get("page", None) == "rookies":
        return render(request, "dashboard/cards/card_list.html", {})

    if request.POST.get("page", None) == "settings":
        return page_settings(request)

    return HttpResponse("Response: " + request.POST.get("page", None))


@check_login
def dashboard(request):
    context = {
        'avatar': request.session['avatar'],
        'nickname': request.session['nickname']
    }

    return render(request, "dashboard/dashboard.html", context)


# 使用协议
def agreement(request):
    return render(request, "agreement.html", {})


# 忘记密码
def forgotten(request):
    return render(request, "forgotten.html", {})
