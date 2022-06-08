"""frozen_brothers URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
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
from django.urls import re_path as url
from django.contrib import admin
from django.urls import path, include
from price_promotion import views

urlpatterns = [
    path('admin/', admin.site.urls),
    # path('price_promotion/', include('price_promotion.urls')),
    url(r'^login$', views.get_token, name='login_user'),
    url(r'^logout$', views.user_logout, name='logout_user'),
    url(r'^upload$', views.upload, name='upload video'),
    url(r'^price_tag$', views.create_price_tag, name='create price_tag'),
    path("download",views.download,name="downlaod")
]
