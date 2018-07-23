from django.shortcuts import render


# 使用此装饰器，请保证函数的第一个参数为request
def check_login(func):
    def wrapper(*args, **kw):
        if not args[0].session.get('is_login', False):
            return render(args[0], "error.html", {"error_message": "您还未登录或登录状态已失效，请重新登录！"})
        else:
            args[0].session.set_expiry(3600)  # 1小时有效期
        return func(*args, **kw)

    return wrapper


# 使用此装饰器，请保证函数的第一个参数为request
def check_post(func):
    def wrapper(*args, **kw):
        if args[0].method != "POST":
            return render(args['request'], "error.html", {"error_message": "Request method invalid"})
        else:
            return func(*args, **kw)

    return wrapper
