from django.conf.urls import patterns, url
from django.contrib import databrowse
from django.db.models import get_models

databrowse.site.register(*get_models())
urlpatterns = patterns('',
    url(r'^(.*)', databrowse.site.root),
)
