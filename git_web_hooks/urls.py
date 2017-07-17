"""git_web_hooks URL Configuration

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
# from django.contrib import admin
from apps.views import *
import apps.views_admin
import apps.my_views.views_ddl

urlpatterns = [
    # url(r'^admin/', admin.site.urls),
    url(r'^web_hook/push', push),
    url(r'^web_hook/login', login),
    url(r'^web_hook/check_code', check_code),
    url(r'^admin/index', apps.views_admin.index),
    url(r'^admin/welcome', apps.views_admin.welcome),
    url(r'^admin/projects', apps.views_admin.projects_list),
    url(r'^admin/project\.action', apps.views_admin.project_action),
    url(r'^admin/project\.to_test_env', apps.views_admin.to_test_env),
    url(r'^admin/project_action_to_test_env', apps.views_admin.to_test_env_action),
    url(r'^admin/project\.to_produce_env', apps.views_admin.to_produce_env),
    url(r'^admin/project_action_to_produce_env', apps.views_admin.to_produce_env_action),
    url(r'^admin/project_rollback', apps.views_admin.project_rollback),
    url(r'^admin/ddl/lists', apps.my_views.views_ddl.ddl_lists),
]
