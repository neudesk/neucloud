import logging
from django import forms
from django.conf import settings
from django.core.urlresolvers import reverse_lazy
from django.utils.translation import ugettext_lazy as _
from django.utils.html import mark_safe
from mailer.views import Mailer
from .api import KeystoneCli

from activetoken.models import Token

LOG = logging.getLogger(__name__)


class UtilsMixin(object):

    def cli(self):
        cli = KeystoneCli()
        return cli

    def create_token(self, value):
        token = Token(value=value)
        token.save()
        return token.token

    def build_url(self, unreverse_url=None, token=None):
        url = "http://%s%s?token=%s" % (getattr(settings, 'OPENSTACK_APP_HOST', None),
                                        reverse_lazy(unreverse_url),
                                        token)
        return url

    def get_default_mail(self):
        return settings.DEFAULT_MAIL

    def send_mail(self, subject, msg, to):
        mail = Mailer(subject=subject,
                      message=msg,
                      fr=self.get_default_mail(),
                      recipients=[to])
        return mail.send()

class ChangePassword(forms.Form, UtilsMixin):
    password_regex = "((?=.*\\d)(?=.*[a-z])(?=.*[A-Z])(?=.*[@#$%]).{6,20})"
    regex_error = """
    Must contains one lowercase and uppercase characters,
    must contains one special symbols in the list '@#$%'
    """
    password = forms.RegexField(password_regex, max_length=30, min_length=8,
                                widget=forms.PasswordInput(),
                                error_message=regex_error)
    confirm_password = forms.CharField(max_length=30, min_length=8, widget=forms.PasswordInput())

    def clean_confirm_password(self):
        data = self.cleaned_data
        p1 = data.get('password')
        p2 = data.get('confirm_password')
        if p1 != p2:
            raise forms.ValidationError("Password did not match!")
        return p2

    def change_password(self, user):
        cli = self.cli()
        cli.client.users.update_password(user,
                                         self.cleaned_data.get('password'))
        to = user.email
        subject = "Password Changed"
        url = self.build_url(unreverse_url="splash")
        msg = """
        You password has been changed successfully.<br />
        You may <a href='%s'>sign in here</a>.
        """ % url
        self.send_mail(subject, msg, to)

class RequestForgotPassword(forms.Form, UtilsMixin):
    email = forms.EmailField()

    def get_user(self):
        cli = self.cli()
        users = cli.client.users.list()
        return users

    def clean_email(self):
        data = self.cleaned_data
        exists = False
        for u in self.get_user():
            if u.email == data['email']:
                exists = True
        if not exists:
            msg = """
            This email address is not a registered account.<br />
            Please <a href='%s'>click here to join</a>.
            """ % reverse_lazy("register")
            raise forms.ValidationError(mark_safe(msg))
        return data['email']

    def get_user_id(self):
        email = self.cleaned_data.get('email')
        cli = self.cli()
        users = cli.client.users.list()
        for u in users:
            if u.email == email:
                return u.id

    def forgot_pass(self):
        value = self.get_user_id()
        token = self.create_token(value)
        if token:
            to = self.cleaned_data.get('email')
            subj = "Reset Password"
            url = self.build_url(unreverse_url="change_password",
                                 token=token)
            msg = """
            Please follow the link below to update your password.<br />
            <a href='%s'>%s</a>
            """ % (url,
                   url)
            self.send_mail(subj, msg, to)


class RequestActivationForm(forms.Form, UtilsMixin):

    email = forms.EmailField()

    def get_user(self):
        cli = self.cli()
        users = cli.client.users.list()
        return users

    def clean_email(self):
        data = self.cleaned_data
        exists = False
        for u in self.get_user():
            if u.email == data['email']:
                exists = True
        if not exists:
            msg = """
            This email address is not a registered account.<br />
            Please <a href='%s'>click here to join</a>.
            """ % reverse_lazy("register")
            raise forms.ValidationError(mark_safe(msg))
        return data['email']

    def get_tenant_id(self, email):
        for u in self.get_user():
            if email == u.email:
                return u.tenantId

    def send_mail(self, tenant_id):
        data = self.cleaned_data
        url = "http://%s%s?token=%s" % (getattr(settings, 'OPENSTACK_APP_HOST', None),
                                        reverse_lazy("activate"),
                                        self.create_token(tenant_id))
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


class RegistrationForm(forms.Form, UtilsMixin):

    password_regex = "((?=.*\\d)(?=.*[a-z])(?=.*[A-Z])(?=.*[@#$%]).{6,20})"
    regex_error = """
    Must contains one lowercase and uppercase characters,
    must contains one special symbols in the list '@#$%'
    """
    email = forms.EmailField()
    password = forms.RegexField(password_regex, max_length=30, min_length=8,
                                widget=forms.PasswordInput(),
                                error_message=regex_error)
    # password = forms.CharField(max_length=30, min_length=8, widget=forms.PasswordInput(), regex=password_regex)
    confirm_password = forms.CharField(max_length=30, min_length=8, widget=forms.PasswordInput())

    def __init__(self, *args, **kwargs):
        super(RegistrationForm, self).__init__(*args, **kwargs)
        self.cli = KeystoneCli()

    def clean_confirm_password(self):
        data = self.cleaned_data
        p1 = data.get("password")
        p2 = data.get("confirm_password")

        if p1 and p1 != p2:
            raise forms.ValidationError("Password did not match")
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


    def register(self):
        data = self.cleaned_data
        tenant = self.cli.make_tenant(tenant_name=self.tenant_name(),
                                      description="Default Description",
                                      enabled=False)
        user = self.cli.make_user(name=data.get("email"),
                                  password=data.get("password"),
                                  email=data.get("email"),
                                  tenant_id=tenant.id,
                                  enabled=True)
        if user:
            url = "http://%s%s?token=%s" % (getattr(settings, 'OPENSTACK_APP_HOST', None),
                                            reverse_lazy("activate"),
                                            self.create_token(tenant.id))
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




