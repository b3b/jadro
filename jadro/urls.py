from django.conf.urls import patterns, url, include
from django.contrib import admin
from django.contrib import databrowse
from django.db.models import get_models
from jadro_droid import urls as droid_urls
from views import IndexView

admin.autodiscover()

index_urls = (
    {'name': 'Databrowse', 'href': '/databrowse/'},
    {'name': 'Admin', 'href': '/admin/'},
    {'name': 'API form', 'href': '/droid/form'},
    )

databrowse.site.register(*get_models())
urlpatterns = patterns('',
    url(r'^$', IndexView.as_view(urls=index_urls)),
    url(r'^admin/', include(admin.site.urls), name='xxxx'),
    url(r'^droid/', include(droid_urls)),
    url(r'^databrowse/(.*)', databrowse.site.root),
)
