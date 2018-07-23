import os
import logging

from PIL import Image
from django.http import HttpResponse
from django.core.exceptions import MultipleObjectsReturned
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage


from QieGaoWorld import settings
from QieGaoWorld.models import User
from QieGaoWorld.views.decorator import check_login, check_post


def avatar_update(request, new_avatar_url):
    username = request.session.get('username', "N/A")
    try:
        obj = User.objects.filter(username=username)
    except MultipleObjectsReturned:
        return HttpResponse(r'{"status": "failed", "msg": "Internal Server Error 服务器内部错误 错误代码:1"}')
    if len(obj) == 0:
        return HttpResponse(r'{"status": "failed", "msg": "更新头像失败 错误代码:2"}')
    obj[0].avatar = new_avatar_url
    obj[0].save()
    request.session['avatar'] = new_avatar_url


@check_post
@check_login
def avatar_upload(request):
    file_obj = request.FILES["files[]"]
    file_name = str(file_obj)

    pos = file_name.find(".")
    if pos == -1:
        return HttpResponse(r'{"status": "failed", "msg": "File type error."}')
    suffix = file_name[pos:]

    allowed_type = [".jpg", ".png", ".jpeg", ".gif"]

    flag = False
    for eachType in allowed_type:
        if suffix.lower() == eachType:
            flag = True
            break

    if flag:
        path = default_storage.save(request.session.get('username', 'N/A') + suffix, ContentFile(file_obj.read()))
        tmp_file = os.path.join(settings.MEDIA_ROOT, path)

        try:
            im = Image.open(tmp_file)
        except Exception as e:
            logging.error(e)
            return HttpResponse(r'{"status": "failed", "msg": "Internal Server Error 服务器内部错误"}')

        out = im.resize((128, 128), Image.ANTIALIAS)
        out.save(tmp_file)

        avatar_update(request, 'static\\face\\' + str(path))
        return HttpResponse(r'{"status": "ok", "msg": "修改成功</br>刷新页面后生效"}')
    else:
        return HttpResponse(r'{"status": "failed", "msg": "文件类型错误"}')
