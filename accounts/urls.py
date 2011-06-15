from django.conf.urls.defaults import *
from django.contrib.auth.views import password_reset, password_reset_done

urlpatterns = patterns('',
    ('^login/$', 'django.contrib.auth.views.login'),
    ('^logout/$', 'django.contrib.auth.views.logout'),
    ('^signup/$', 'accounts.views.signup'),

    (r'^password_change/$', 
      'django.contrib.auth.views.password_change', 
      {'template_name': 'registration/password_change_form.html'}),

    (r'^password_change/done/$', 
      'django.contrib.auth.views.password_change_done', 
      {'template_name': 'registration/password_change_done.html'}),

    (r'^password_reset/$', 
      'django.contrib.auth.views.password_reset', 
      {'template_name': 'registration/password_reset_form.html',
       'email_template_name': 'registration/password_reset_email.html',
      }),

    (r'^password_reset/done/$', 
      'django.contrib.auth.views.password_reset_done', 
      {'template_name': 'registration/password_reset_done.html'}),

    (r'^reset/(?P<uidb36>[0-9A-Za-z]+)-(?P<token>.+)/$', 
      'django.contrib.auth.views.password_reset_confirm', 
      {'template_name': 'registration/password_reset_confirm.html'}),

    (r'^reset/done/$', 
      'django.contrib.auth.views.password_reset_complete', 
      {'template_name': 'registration/password_reset_complete.html'}),
)

