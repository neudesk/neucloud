import logging
from django import forms
from django.conf import settings
from django.core.urlresolvers import reverse_lazy
from django.utils.html import mark_safe
from mailer.views import Mailer
from .api import KeystoneCli

LOG = logging.getLogger(__name__)

class RequestActivationForm(forms.Form):

    email = forms.EmailField()

    def __init__(self, *args, **kwargs):
        super(RequestActivationForm, self).__init__(*args, **kwargs)
        self.cli = KeystoneCli()

    def get_user(self):
        users = self.cli.client.users.list()
        return users

    def clean_email(self):
        data = self.cleaned_data
        exists = False
        for u in self.get_user():
            if u.email == data['email']:
                exists = True
        if not exists:
            msg = """
            This email address is not registered yet.<br />
            Please click <a href='%s'>here</a> to register.
            """ % reverse_lazy("register")
            raise forms.ValidationError(mark_safe(msg))
        return data['email']

    def get_tenant_id(self, email):
        for u in self.get_user():
            if email == u.email:
                return u.tenantId

    def get_default_mail(self):
        return settings.DEFAULT_MAIL

    def send_mail(self, tenant_id):
        data = self.cleaned_data
        url = "http://%s%s?token=%s" % (getattr(settings, 'OPENSTACK_HOST', None),
                                        reverse_lazy("activate"),
                                        tenant_id)
        msg = """
            Please follow the link below to activate your account.<br />
            <a href='%s'>%s</a>
            """ % (url, url)
        mail = Mailer(subject="Activate",
                      message=msg,
                      fr=self.get_default_mail(),
                      recipients=[data['email']])
        mail.send()

    def request_activation(self):
        data = self.cleaned_data
        email = data['email']
        tenant_id = self.get_tenant_id(email)
        self.send_mail(tenant_id)


class RegistrationForm(forms.Form):

    email = forms.EmailField()
    password = forms.CharField(max_length=30, widget=forms.PasswordInput())
    confirm_password = forms.CharField(max_length=30, widget=forms.PasswordInput())

    def __init__(self, *args, **kwargs):
        super(RegistrationForm, self).__init__(*args, **kwargs)
        self.cli = KeystoneCli()

    def clean_confirm_password(self):
        data = self.cleaned_data
        p1 = data.get("password")
        p2 = data.get("confirm_password")

        if p1 and p1 != p2:
            raise forms.ValidationError("Password did not match!")
        return p2

    def clean_email(self):
        data = self.cleaned_data
        users = self.cli.client.users.list()
        for u in users:
            if u.email == data['email']:
                raise forms.ValidationError("email address is already been taken!")
        return data['email']

    def tenant_name(self):
        email = self.cleaned_data['email']
        return email

    def get_default_mail(self):
        return settings.DEFAULT_MAIL

    def register(self):
        data = self.cleaned_data
        tenant = self.cli.make_tenant(tenant_name=self.tenant_name(),
                                      description="Default Description",
                                      enabled=False)
        user = self.cli.make_user(name=data.get("email"),
                                  password=data.get("password"),
                                  email=data.get("email"),
                                  tenant_id=tenant.id,
                                  enabled=False)
        if user:
            url = "http://%s%s?token=%s" % (getattr(settings, 'OPENSTACK_HOST', None),
                                            reverse_lazy("activate"),
                                            tenant.id)
            msg = """
            Please follow the link below to activate your account.<br />
            <a href='%s'>%s</a>
            """ % (url,
                   url)
            mail = Mailer(subject="Activate",
                          message=msg,
                          fr=self.get_default_mail(),
                          recipients=[data['email']])
            mail.send()
        return user




