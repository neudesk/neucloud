from django.conf.urls import url, patterns
from .views import *

urlpatterns = patterns('',
    url(r'^$', RegistrationView.as_view(), name='register'),

    url(r'^request/activation/$', RequestActivation.as_view(), name='request_activation'),
    url(r'^activate/$', ActivationView.as_view(), name='activate'),

    url(r'^request/change/password$', ForgotPasswordView.as_view(), name='change_password_request'),
    url(r'^change/password', ChangePasswordView.as_view(), name='change_password'),
)