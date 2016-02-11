from django.conf.urls import patterns, url
from . import views

urlpatterns = [
    url(r'^$',
        views.email_registration_form,
        name='email_registration_form'),
    url(r'^(?P<code>[^/]+)/$',
        views.email_registration_confirm,
        name='email_registration_confirm'),
]
