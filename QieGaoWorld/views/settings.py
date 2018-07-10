import time

from django.shortcuts import render


def page_settings(request):
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
    return render(request, "dashboard/settings/account.html", context)
