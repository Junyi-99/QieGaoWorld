from django.http import HttpResponse


def logout(request):
    if request.method != 'POST':
        return HttpResponse(r'{"status": "failed", "msg": "request method invalid"}')

    request.session['is_login'] = False
    request.session['username'] = ''
    request.session['password'] = ''
    return HttpResponse(r'{"status": "ok", "msg": "logout successfully."}')
