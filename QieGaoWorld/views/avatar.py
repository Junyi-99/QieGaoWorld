import os
import logging
import time

from PIL import Image
from django.http import HttpResponse
from django.core.exceptions import MultipleObjectsReturned
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage


from QieGaoWorld import settings
from QieGaoWorld.models import User
from QieGaoWorld.views.decorator import check_login, check_post
from QieGaoWorld.views.dialog import dialog


def avatar_update(request, new_avatar_url):
    username = request.session.get('username', "N/A")
    try:
        obj = User.objects.filter(username=username)
    except MultipleObjectsReturned:
        return HttpResponse(dialog('failed', 'danger', '内部错误，请联系管理员'))
    if len(obj) == 0:
        return HttpResponse(dialog('failed', 'danger', '更新头像失败'))
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
        return HttpResponse(dialog('failed', 'danger', '文件类型错误'))
    suffix = file_name[pos:]

    allowed_type = [".jpg", ".png", ".jpeg", ".gif"]

    flag = False
    for eachType in allowed_type:
        if suffix.lower() == eachType:
            flag = True
            break

    if flag:
        save_path = "face/%s_%d_%s" % (request.session.get('username', 'N/A'), int(time.time()), file_name)
        path = default_storage.save(save_path, ContentFile(file_obj.read()))
        tmp_file = os.path.join(settings.MEDIA_ROOT, path)

        try:
            im = Image.open(tmp_file)
        except Exception as e:
            logging.error(e)
            return HttpResponse(dialog('failed', 'danger', '服务器内部错误，请联系管理员'))

        out = im.resize((128, 128), Image.ANTIALIAS)
        out.save(tmp_file)

        avatar_update(request, 'static\\media\\' + str(path))
        return HttpResponse(dialog('ok', 'success', '修改成功，刷新页面后生效'))
    else:
        return HttpResponse(dialog('failed', 'danger', '文件类型错误'))
