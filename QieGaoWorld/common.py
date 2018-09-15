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