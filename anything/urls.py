"""anything URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.10/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url
from django.contrib import admin
from any import views

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^$', views.index),
    url(r'^login', views.user_login),
    url(r'^account/logout', views.user_logout),
    url(r'^user/list', views.users_list),
    url(r'^project/list', views.project_list),
    url(r'^group/list$', views.groups_list),
    url(r'^group/add$', views.group_add),
    url(r'^group/query$', views.group_query),
    url(r'^group/modify$', views.group_modify),
    url(r'^group/del$', views.group_del),
]
