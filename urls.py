from django.conf.urls.defaults import *

from django.contrib import admin
admin.autodiscover()

handler500 = 'djangotoolbox.errorviews.server_error'

urlpatterns = patterns('',
    (r'^pixnet/$', 'pixnet.views.index'),
    (r'^pixnet/authorized/$', 'pixnet.views.authorized'),
    (r'^pixnet/authorize/$', 'pixnet.views.authorize'),

    url(r'^admin/', include(admin.site.urls)),

    ('^_ah/warmup$', 'djangoappengine.views.warmup'),
#    ('^$', 'django.views.generic.simple.direct_to_template',
#     {'template': 'home.html'}),
    ('^$', 'home.views.index'),
)
