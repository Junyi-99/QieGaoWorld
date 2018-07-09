from django.http import HttpResponse
from django.views.decorators.csrf import ensure_csrf_cookie

from QieGaoWorld.views.decorator import check_post
from QieGaoWorld.models import Cases

import time


@ensure_csrf_cookie
@check_post
def report(request):
    try:
        position = str(request.POST.get('position', None))
        coordinate_x = str(request.POST.get('coordinate_x', None)).strip()
        coordinate_y = str(request.POST.get('coordinate_y', None)).strip()
        coordinate_z = str(request.POST.get('coordinate_z', None)).strip()
        summary = str(request.POST.get('summary', None))
        detail = str(request.POST.get('detail', None))
        print(position, coordinate_x, coordinate_y, coordinate_z, summary, detail)

        obj = Cases(
            report_time=int(time.time()),
            position=position,
            coordinate=coordinate_x + ", " + coordinate_y + ", " + coordinate_z,
            summary=summary,
            detail=detail,
            username=request.session['username'],
            progress='等待受理',
            status=0,
            picture=''
        )
        obj.save()

        # TODO: 报警可以上传案发现场截图的功能

    except Exception as e:
        print(e)
        return HttpResponse(r'{"status": "failed", "msg": "内部错误"}')

    return HttpResponse(r'{"status": "ok", "msg": "报警成功！"}')
