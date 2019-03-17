from django.http import HttpResponse

from QieGaoWorld.views.decorator import check_post
from QieGaoWorld.views.dialog import dialog


def logout(request):
    request.session['is_login'] = False
    request.session['username'] = ''
    request.session['password'] = ''
    return HttpResponse(dialog('ok', 'success', '登出成功'))
