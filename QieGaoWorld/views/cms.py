from QieGaoWorld import parameter
from django.http import HttpResponse
from django.shortcuts import render
from QieGaoWorld.views.decorator import check_post
from QieGaoWorld.views.decorator import check_login
from QieGaoWorld.views.dialog import dialog
from QieGaoWorld.models import CmsBook,CmsChapter
from QieGaoWorld import settings,common

from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
import os,traceback,uuid,logging,time,json,sys,requests
from PIL import Image
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.core.exceptions import MultipleObjectsReturned, ObjectDoesNotExist

from qcloud_cos import CosConfig
from qcloud_cos import CosS3Client
def url(request, s):
    return eval(s)(request)

def book_list(request):
    book=CmsBook.objects.filter(author=request.session['username'])

    page=request.POST.get("page",1)
    paginator = Paginator(book, 25)
    book=paginator.get_page(page)
    for i in range(0,len(book)) :
        #1已发布 0草稿箱 -1已删除 2已下架
        if book[i].status ==1:
            book[i].status_class="uk-label-success"
            book[i].status_text="已发布"
        elif book[i].status==0:
            book[i].status_class=""
            book[i].status_text="草稿箱"
        elif book[i].status==2:
            book[i].status_class="uk-label-warning"
            book[i].status_text="已下架"
        book[i].show_time=time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(book[i].show_time))

    return render(request, 'dashboard/cms/book_list.html', {'permissions': request.session['permissions'],'list': book,"page":common.page("cms/book_list",book)})

def book_info(request):
    _id=request.POST.get("id",None);
    if _id==None or len(_id)<=0:
        return HttpResponse(dialog('failed', 'danger', '参数错误'))
    book=CmsBook.objects.get(id=_id)
    if book==None:
        return HttpResponse(dialog('failed', 'danger', '连载不存在！'))
    
    
    return HttpResponse(json.dumps({"id":book.id,"name":book.title,"img":book.img,"summary":book.summary,"status":"ok"} ))

def upload_img(request):
    file_obj = request.FILES["files[]"]
    file_name = str(file_obj)

    pos = file_name.rfind(".")
    if pos == -1:
        return HttpResponse(dialog('failed', 'danger', '文件类型错误'))

    suffix = file_name[pos:]  # 取出后缀名

    allowed_type = [".jpg", ".png", ".jpeg", ".gif"]

    flag = False
    for eachType in allowed_type:
        if suffix.lower() == eachType:
            flag = True
            break

    if flag:
        try:
            u = str(uuid.uuid1())
            save_path = "cms/book/%s" % ( u + ".png")

            path = default_storage.save(save_path, ContentFile(file_obj.read()))

            tmp_file = os.path.join(settings.MEDIA_ROOT, path)

            im = Image.open(tmp_file)
            width, height = im.size

            # resize 一下，破坏PE文件后面的附属信息（防止被当作图床）
            out = im.resize((width - 1, height - 1), Image.ANTIALIAS)
            out.save(tmp_file)

        except Exception as e:
            logging.error(e)
            return HttpResponse(dialog('failed', 'danger', '文件类型错误，请联系管理员'))

        return HttpResponse(dialog('ok', 'success', '修改成功', {'url': "static/media/%s" % save_path}))
    else:
        return HttpResponse(dialog('failed', 'danger', '文件类型错误'))

def book_add(request):
    try:
        arg_list = {'name', 'summary', 'type'}

        lis = {key: str(request.POST.get(key, '')).strip() for key in arg_list}
        lis['time'] = int(time.time())
        lis['author'] = request.session.get('username', None)
        _id=request.POST.get("id", None)
        for l in lis:
            if len(str(lis[l])) == 0:
                return HttpResponse(dialog('failed', 'danger', '%s为空！请检查！' % l))
        # lis['pic_perspective'] = str(request.POST.get('pic_perspective', '')).strip()
        if(lis['type']=='0'):
            lis['show_time']=int(time.time())
        else:
            lis['show_time']=0
        lis['img'] = request.POST.get('img', "")
        if _id==None or len(_id)<=0:
            obj = CmsBook(
                title=lis['name'],
                summary=lis['summary'],
                img=lis['img'],
                status=1,
                show_time=lis['show_time'],
                time=lis['time'],
                author=lis['author']
            )
        else:
            obj=CmsBook.objects.get(id=_id)
            obj.title=lis['name']
            obj.summary=lis['summary']
            if lis['img'] != None:
                obj.img=lis['img']
            if obj.show_time==0 and lis['type']=='0':
                obj.show_time=int(time.time())
        obj.save()
        return HttpResponse(dialog('ok', 'success', '编辑成功'))
    except ValueError as e:
        print(e)
        return HttpResponse(dialog('failed', 'danger', '数值错误'))
    except Exception as e:
        logging.error(e)
        return HttpResponse(dialog('failed', 'danger', '内部错误，请联系管理员'))


@check_login
def book_del(request):
    try:
        id_ = int(request.POST.get('id', None))
        username = request.session.get('username', None)
    except ValueError:
        return HttpResponse(dialog('failed', 'danger', '参数错误'))

    try:
        obj =  CmsBook.objects.get(id=id_)
        # 1、检查是否是当前用户的状态为“审核不通过”的建筑
        if  not (obj.author == username or ('%op%' in request.session.get('permissions', '%default%') ) ) :
            return HttpResponse(dialog('failed', 'danger', '可能这条记录不属于你！'))
        chapter=CmsChapter.objects.filter(book_id=obj.id)
        if len(chapter)>0:
            return HttpResponse(dialog('failed', 'danger', '当前连载下还有未删除的章节'))
        imgpath=os.path.join(os.getcwd(),obj.img)
        if  os.path.exists(imgpath) and not os.path.isdir(imgpath) :
            os.unlink(imgpath)
        obj.delete()
        return HttpResponse(dialog('ok', 'success', '删除连载成功'))
    except MultipleObjectsReturned as e:
        logging.error(e)
        return HttpResponse(dialog('failed', 'danger', '内部错误，请联系管理员'))
    except ObjectDoesNotExist:
        return HttpResponse(dialog('failed', 'danger', '可能这条记录不属于你！'))


def chapter_list(request):
    _id=request.POST.get("id",0)
    if _id==0:
        # return book_list(request)
        return HttpResponse(dialog('failed', 'danger', '参数错误'))
    
    chapter=CmsChapter.objects.filter(book_id=_id)

    page=request.POST.get("page",1)
    paginator = Paginator(chapter, 25)
    chapter=paginator.get_page(page)
    for i in range(0,len(chapter)) :
        #1已发布 0草稿箱 -1已删除 2已下架
        if chapter[i].status ==1:
            chapter[i].status_class="uk-label-success"
            chapter[i].status_text="已发布"
        elif chapter[i].status==0:
            chapter[i].status_class=""
            chapter[i].status_text="草稿箱"
        elif chapter[i].status==2:
            chapter[i].status_class="uk-label-warning"
            chapter[i].status_text="已下架"

        if chapter[i].show_time!=0:
            chapter[i].show_time=time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(chapter[i].show_time))
        else:
            chapter[i].show_time=time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())

    return render(request, 'dashboard/cms/chapter_list.html', {'permissions': request.session['permissions'],'list': chapter,"page":common.page("cms/chapter_list",chapter)})
def chapter(request):
    _id=int(request.POST.get("_get",0)[3:])
    if _id==0:
        return book_list(request)
    
    book=CmsBook.objects.get(id=_id)

    return render(request, 'dashboard/cms/chapter.html', {'permissions': request.session['permissions'],'book': book})


def chapter_add(request):
    # try:
    arg_list = {'name', 'summary', 'book_id','type'}

    lis = {key: str(request.POST.get(key, '')).strip() for key in arg_list}
    lis['time'] = int(time.time())
    _id=request.POST.get("id", None)
    for l in lis:
        if len(str(lis[l])) == 0:
            return HttpResponse(dialog('failed', 'danger', '%s为空！请检查！' % l))
    # lis['pic_perspective'] = str(request.POST.get('pic_perspective', '')).strip()
    if(lis['type']==0):
        lis['show_time']=int(time.time())
    else:
        lis['show_time']=0
    if _id==None or len(_id)==0:
        obj = CmsChapter(
            title=lis['name'],
            content=lis['summary'],
            status=1,
            show_time=lis['show_time'],
            time=lis['time'],
            book_id=lis['book_id']
        )
    else:
        obj=CmsChapter.objects.get(id=_id)
        obj.title=lis['name']
        obj.content=lis['summary']
    obj.save()
    return HttpResponse(dialog('ok', 'success', '添加成功'))
    # except ValueError as e:
    #     print(e)
    #     return HttpResponse(dialog('failed', 'danger', '数值错误'))
    # except Exception as e:
    #     logging.error(e)
    #     return HttpResponse(dialog('failed', 'danger', '内部错误，请联系管理员'))
def chapter_info(request):
    _id=request.POST.get("id",None);
    if _id==None or len(_id)<=0:
        return HttpResponse(dialog('failed', 'danger', '参数错误'))
    book=CmsChapter.objects.get(id=_id)
    if book==None:
        return HttpResponse(dialog('failed', 'danger', '章节不存在！'))
    
    
    return HttpResponse(json.dumps({"id":book.id,"name":book.title,"summary":book.content,"status":"ok"} ))
def chapter_change_show_time(request):
    try:
        _id=request.POST.get("id",None);
        _time=request.POST.get("time",None);
        if _id==None or len(_id)<=0:
            return HttpResponse(dialog('failed', 'danger', '参数错误'))
        book=CmsChapter.objects.get(id=_id)
        if book==None:
            return HttpResponse(dialog('failed', 'danger', '章节不存在！'))
        book.show_time=time.mktime(time.strptime(_time, "%Y-%m-%d %H:%M:%S"))
        book.save()
        return HttpResponse(dialog('ok', 'success', '编辑成功'))
    except Exception as e:
        return HttpResponse(dialog('failed', 'danger', '内部错误，请联系管理员'))

@check_login
def chapter_del(request):
    try:
        id_ = int(request.POST.get('id', None))
    except ValueError:
        return HttpResponse(dialog('failed', 'danger', '参数错误'))

    try:
        obj =  CmsChapter.objects.get(id=id_)
        book=CmsBook.objects.get(id=obj.book_id)
        # 1、检查是否是当前用户的状态为“审核不通过”的建筑
        if  not (book.author == username or ('%op%' in request.session.get('permissions', '%default%') ) ) :
            return HttpResponse(dialog('failed', 'danger', '可能这条记录不属于你！'))
        imgpath=os.path.join(os.getcwd(),obj.img)
        if  os.path.exists(imgpath) and not os.path.isdir(imgpath) :
            os.unlink(imgpath)
        obj.delete()
        return HttpResponse(dialog('ok', 'success', '删除章节成功'))
    except MultipleObjectsReturned as e:
        logging.error(e)
        return HttpResponse(dialog('failed', 'danger', '内部错误，请联系管理员'))
    except ObjectDoesNotExist:
        return HttpResponse(dialog('failed', 'danger', '可能这条记录不属于你！'))

def index(request):

    book=CmsBook.objects.all()
    page=request.POST.get("page",1)
    paginator = Paginator(book, 25)
    book=paginator.get_page(page)
    for i in range(0,len(book)):
        book[i].show_time=time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(book[i].show_time))

    return render(request, 'index/cms/book.html', {'permissions': request.session['permissions'],'book': book,"page":common.page("cms/index",book)})
def list(request):
    _id=request.GET.get('id',None)
    if _id==None or len(_id)<=0:
        return index(request)
    
    book=CmsBook.objects.get(id=_id)
    if book == None:
        return index(request)
    book.show_time=time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(book.show_time))
    chapter=CmsChapter.objects.filter(book_id=_id)
    # page=request.POST.get("page",1)
    # paginator = Paginator(chapter, 25)
    # chapter=paginator.get_page(page)
    for i in range(0,len(chapter)):
        chapter[i].show_time=time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(chapter[i].show_time))

    return render(request, 'index/cms/list.html', {'permissions': request.session['permissions'],'book': book,"list":chapter})
def info(request):
    _id=request.GET.get('id',None)
    if _id==None or len(_id)<=0:
        return index(request)
    
    info=CmsChapter.objects.get(id=_id)
    if info == None:
        return index(request)
    # book.show_time=time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(book.show_time))
    chapter=CmsChapter.objects.filter(book_id=info.book_id)
    # book=CmsBook.objects.get(id=_id)
    # page=request.POST.get("page",1)
    # paginator = Paginator(chapter, 25)
    # chapter=paginator.get_page(page)
    for i in range(0,len(chapter)):
        chapter[i].show_time=time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(chapter[i].show_time))

    return render(request, 'index/cms/info.html', {'permissions': request.session['permissions'],'book': info,"list":chapter})
