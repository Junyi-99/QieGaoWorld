from django.http import HttpResponse
from django.shortcuts import render
from django.views.decorators.csrf import requires_csrf_token
from django.views.decorators.csrf import ensure_csrf_cookie
from django.conf import settings

import json
import time
import logging
from .views.decorator import check_login, check_post
from .views.police import page_police_hall
from .views.settings import page_settings
from .views.declare import animals_list, buildings_list


# 使用协议
def agreement(request):
    return render(request, "agreement.html", {})


# 忘记密码
def forgotten(request):
    return render(request, "forgotten.html", {})


def global_settings(request):
    return {"PROJECT_VERSION": settings.PROJECT_VERSION,
            'AUTHOR': settings.PROJECT_VERSION}


def handle_uploaded_file(f):
    with open(f.name, "wb+") as destination:
        for chunk in f.chunks():
            destination.write(chunk)


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

        if status.players.sample is not None:
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
            'permissions': request.session['permissions'],
        }
        logging.debug(context)
    except Exception as e:
        logging.error(e)
        context = {}

    logging.debug(context['permissions'])
    return render(request, "dashboard/user_center.html", context)


@check_login
def page_announcement(request):
    return render(request, "dashboard/announcement/announcement.html", {})


@check_login
def page_declaration_center(request):
    return render(request, "dashboard/declaration/center.html", {})


@check_login
def page_call_the_police(request):
    return render(request, "dashboard/police/call_the_police.html", {})


@check_login
def page_declare_animals(request):
    my_animals = animals_list(request)
    content = {
        'my_animals': my_animals,
        'permissions': request.session['permissions'],
    }
    return render(request, "dashboard/declaration/animals.html", content)


@check_login
def page_declare_buildings(request):
    my_building = buildings_list(request)
    print(my_building)
    content = {
        'buildings': my_building,
        'permissions': request.session['permissions'],
    }
    return render(request, "dashboard/declaration/buildings.html", content)


@check_login
def page_papers(request):
    return render(request, "dashboard/papers/papers.html", {})


@check_login
def page_community(request):
    return render(request, "dashboard/papers/community.html", {})


@check_login
def page_project_plan(request):
    return render(request, "dashboard/papers/plans.html", {})


@check_login
def page_call_the_police(request):
    return render(request, "dashboard/police/call_the_police.html", {})


@check_login
def page_world_map(request):
    return render(request, "dashboard/world_map/map.html", {})


@check_login
def page_rookies(request):
    return render(request, "dashboard/rookies/rookies.html", {})


@check_login
def dashboard(request):
    context = {
        'avatar': request.session['avatar'],
        'nickname': request.session['nickname']
    }

    return render(request, "dashboard/dashboard.html", context)


@ensure_csrf_cookie
@check_login
@check_post
def dashboard_page(request):
    ensure_csrf_cookie(request)
    logging.info("Page Changed: " + request.POST.get("page", None))
    if request.POST.get("page", None) == "user_center":
        return user_center(request)

    if request.POST.get("page", None) == "announcement":
        return page_announcement(request)

    if request.POST.get("page", None) == "news":
        return render(request, "dashboard/settings/account.html", {})

    if request.POST.get("page", None) == "papers":
        return page_papers(request)

    if request.POST.get("page", None) == "project_plan":
        return page_project_plan(request)

    if request.POST.get("page", None) == "community":
        return page_community(request)

    if request.POST.get("page", None) == "declaration_center":
        return page_declaration_center(request)

    if request.POST.get("page", None) == "declare_buildings":
        return page_declare_buildings(request)

    if request.POST.get("page", None) == "declare_animals":
        return page_declare_animals(request)

    if request.POST.get("page", None) == "police_hall":
        return page_police_hall(request)

    if request.POST.get("page", None) == "call_the_police":
        return page_call_the_police(request)

    if request.POST.get("page", None) == "world_map":
        return page_world_map(request)

    if request.POST.get("page", None) == "rookies":
        return page_rookies(request)

    if request.POST.get("page", None) == "settings":
        return page_settings(request)

    return HttpResponse("Response: " + request.POST.get("page", None))
