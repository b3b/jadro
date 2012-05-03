from django.conf.urls import patterns, url
from django.conf import settings
from views import APIHandler, APIFormView

droid = settings.DROID_CONNECTION

urlpatterns = patterns('',
    url(r'^api/$', APIHandler.as_view(droid=droid)),
    url(r'^api/(?P<method>\w+)/$', APIHandler.as_view(droid=droid)),
    url(r'^form/$', APIFormView.as_view(droid=droid)),
    url(r'^form/(?P<method>\w+)/$', APIFormView.as_view(droid=droid)),
)
