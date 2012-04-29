from django.conf.urls import patterns, url, include
from django.contrib import admin
from django.contrib import databrowse
from django.db.models import get_models

admin.autodiscover()

databrowse.site.register(*get_models())
urlpatterns = patterns('',
    url(r'^admin/', include(admin.site.urls)),
    url(r'^(.*)', databrowse.site.root),
)
