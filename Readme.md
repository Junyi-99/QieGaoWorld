# 切糕世界平台

基于 Django 2.0, Python 3.6

针对1.13版本优化，有特定的插件要求。

点击这里进入切糕世界：[https://hall.qiegaoshijie.club/](https://hall.qiegaoshijie.club/)

前端框架：
[UIKit](https://getuikit.com/docs/introduction)

UI设计：
[Junyi](https://github.com/Military-Doctor)

后期开发（鸣谢）：
[chiaki](https://github.com/difuer-yl)

依赖安装：
`pip install -r requirements.txt`

运行服务端：
`python manage.py runserver 0.0.0.0:8000`


 
更新Models：

`python manage.py makemigrations`

`python manage.py migrate`


## Virtual Environments

### 创建venv环境：
`virtualenv --no-site-packages venv`

.

### 进入venv环境：

Windows:
`venv\Scripts\activate.bat`

Linux: 
`source venv/bin/activate`

### 安装依赖
`pip install -r requirements.txt`
