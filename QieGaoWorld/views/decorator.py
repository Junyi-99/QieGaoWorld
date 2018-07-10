from django.shortcuts import render


def check_login(func):
    def wrapper(request):
        if not request.session.get('is_login', False):
            return render(request, "error.html", {"error_message": "您还未登录或登录状态已失效，请重新登录！"})

        request.session.set_expiry(3600)  # 1小时有效期
        return func(request)
    return wrapper


def check_post(func):
    def wrapper(request):
        if request.method != "POST":
            return render(request, "error.html", {"error_message": "Request method invalid"})
        return func(request)
    return wrapper
