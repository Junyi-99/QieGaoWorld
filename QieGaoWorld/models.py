from django.db import models

from QieGaoWorld import settings


class User(models.Model):
    username = models.CharField(max_length=100)  # 用户名
    password = models.CharField(max_length=100)  # 密码
    nickname = models.CharField(max_length=100, default='没有昵称')  # 昵称
    uuid = models.CharField(max_length=32, default='')  # uuid
    qqnumber = models.IntegerField(default=0)  # QQ号
    usrgroup = models.IntegerField(default=0)  # 用户组
    register_time = models.IntegerField(default=0)  # 注册时间
    avatar = models.CharField(max_length=1024, default='static\\media\\face\\default.jpg')  # 头像
    permissions = models.CharField(max_length=2048,
                                   default=settings.DEFAULT_PERMISSIONS)  # 权限


# 报案记录
class Cases(models.Model):
    report_time = models.IntegerField(default=0)  # 报案时间
    position = models.CharField(max_length=1024)  # 案发地点
    coordinate = models.CharField(max_length=64)  # 精确坐标
    summary = models.CharField(max_length=1024)  # 案件简述
    detail = models.CharField(max_length=1024)  # 案件详细信息
    username = models.CharField(max_length=100)  # 报案者
    progress = models.CharField(max_length=100)  # 处理进度
    status = models.IntegerField(default=0)  # 案件结果（0:等待调查, 1:正在调查, 2:处理成功, 3:处理失败）
    picture = models.CharField(max_length=1024)  # 案发现场截图


# 建筑申报记录
class DeclareBuildings(models.Model):
    declare_time = models.IntegerField(default=0)  # 申请时间
    username = models.CharField(max_length=100, default='')  # 申请人用户名
    coordinate = models.CharField(max_length=64, default='')  # 建筑坐标
    area = models.CharField(max_length=64, default='')  # 建筑面积
    concept = models.CharField(max_length=1024, default='')  # 概念图
    plan = models.CharField(max_length=1024, default='')  # 平面图
    name = models.CharField(max_length=64, default='')  # 建筑名
    english_name = models.CharField(max_length=64, default='')  # 英文名
    summary = models.CharField(max_length=128, default='')  # 建筑简介
    detail = models.CharField(max_length=2048, default='')  # 建筑详细介绍
    perspective = models.CharField(max_length=1024, default='')  # 透视图
    predict_start_time = models.IntegerField(default=0)  # 预计开始时间
    predict_end_time = models.IntegerField(default=0)  # 预计结束时间
    actually_end_time = models.IntegerField(default=0)  # 实际结束时间
    status = models.IntegerField(default=0)  # 申报状态（0:挂起, 1:正在审核, 2:审核不通过, 3:审核通过, 4: 正在建设, 5:完工）
    type = models.IntegerField(default=0)  # 建筑类型（0:公共建筑, 1:私有建筑）


# 动物申报记录
class DeclareAnimals(models.Model):
    declare_time = models.IntegerField(default=0)  # 申请时间
    username = models.CharField(max_length=100)  # 申请人
    binding = models.CharField(max_length=100)  # 隶属于（public为公共）
    license = models.CharField(max_length=64)  # 牌照号码
    feature = models.CharField(max_length=64)  # 特征
    status = models.IntegerField(default=0)  # 状态（0:未知, 1:存活, 2:丢失, 3:已死亡）


# 公告
class Announcement(models.Model):
    publish_time = models.IntegerField(default=0)  # 公告发布时间
    username = models.CharField(max_length=100)  # 公告发布者
    title = models.CharField(max_length=100)  # 公告标题
    content = models.CharField(max_length=512)  # 公告内容
    type = models.IntegerField(default=0)  # 公告类型（0:通知, 1:重要, 2:严重）
    visible = models.BooleanField(default=True)  # 公告是否可见

#
class Logs(models.Model):
    code=models.CharField(max_length=50) 
    text = models.TextField()

