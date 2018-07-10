"""QieGaoWorld URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.conf.urls import url
from . import view
from .views import register
from .views import login
from .views import logout
from .views import avatar
from .views import police
from .views import declare

urlpatterns = [
    # url(r'^admin/', admin.site.urls),
    url(r'^$', login.login),
    url(r"^register$", register.register),
    url(r"^register_verify$", register.register_verify),
    url(r"^forgotten$", view.forgotten),
    url(r"^login$", login.login),
    url(r"^logout$", logout.logout),
    url(r"^login_verify$", login.login_verify),
    url(r"^agreement$", view.agreement),
    url(r"^dashboard$", view.dashboard),
    url(r"^upload_face$", avatar.avatar_upload),
    url(r"^dashboard\/page$", view.dashboard_page),
    # TODO: 完善 Save Changes
    # url(r"^save_changes$", view.save_changes),
    url(r"^police_report$", police.report),
    # url(r"^admin$", view.admin),
    # url(r"^admin_login_verify$", view.admin_login_verify),
    # url(r"^admin\/dashboard$", view.admin_dashboard),
    url(r"^animals_add$", declare.animals_add),
]
