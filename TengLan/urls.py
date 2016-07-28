"""TengLan URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.9/topics/http/urls/
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
from django.conf.urls import url,include
from django.contrib import admin
from analyse import views

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^$', views.index,name='overview'),
    url(r'^real_time_analysis/(\d+)/$', views.real_time_analysis,name='real_time_analysis'),
    url(r'^real_time_contry_view/(\d+)/$', views.real_time_contry_view,name='real_time_contry_view'),
    url(r'^region_realtime_watching/(\d+)/$', views.region_realtime_watching,name="region_realtime_watching"),
    url(r'^api/',include('analyse.api_urls')),
]
