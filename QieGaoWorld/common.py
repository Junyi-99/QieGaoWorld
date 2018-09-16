from QieGaoWorld.models import Logs
import time
def logs(text,code='info'):
    logs = Logs(text=text,code=code,time=time.time())
    logs.save()

def filter(sql):
    from django.db import connection, transaction
    cursor = connection.cursor()
    cursor.execute(sql)
    row = cursor.fetchone()
    return row

def page(url,count,index=1):
    li=""
    for i in range(1,int(count)+1):
        # if(i==1):
        #      _type="uk-pagination-previous"
        # if(i==1):
        #      _type="uk-pagination-previous"
        if i == index :
            lc="disabled"
        else:
            lc=""
        li+='<li ><a href="#%s?%d"><button %s class="uk-button uk-button-small uk-button-default" style="border-radius:5px" data-page="%d">%d</button></a></li>' % (url,i,lc,i,i)
        
    return '<ul class="uk-pagination uk-flex-center" id="page" uk-margin>%s</ul><script>$("#page a").click(function(){window.location.reload()})</script>' % li