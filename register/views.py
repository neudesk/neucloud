from django.core.urlresolvers import reverse_lazy
from django.contrib import messages
from django.views.generic import FormView, TemplateView
from django.http import HttpResponseRedirect
from register.api import KeystoneCli
from .forms import *

class FormSubmissionMixin(FormView):
    form_class = None
    template_name = None
    success_url = None
    action = None

    def get_context_data(self, **kwargs):
        context = super(FormSubmissionMixin, self).get_context_data(**kwargs)
        context['pagedesc'] = self.pagedesc
        context['action'] = self.action
        return context

class ForgotPasswordView(FormSubmissionMixin):
    form_class = RequestForgotPassword
    template_name = "registrationindex.djhtml"
    pagedesc = "Reset Password"
    success_url = reverse_lazy("splash")
    action = "Reset"

    def form_valid(self, form):
        form.forgot_pass()
        msg = "Please check your email to reset your password."
        messages.info(self.request, msg)
        return super(ForgotPasswordView, self).form_valid(form)

class ChangePasswordView(FormSubmissionMixin):
    form_class = ChangePassword
    template_name = "registrationindex.djhtml"
    pagedesc = "Update Password"
    success_url = reverse_lazy("splash")
    action = "Send"
    client = KeystoneCli()
    cli = client.client
    error = None

    def get_user_id(self):
        try:
            token_value = Token.objects.get(token=self.request.GET.get('token'))
            return token_value.value
        except:
            msg = """
            There was an invalid token, unable to to associate token to any user.<br />
            Please click <a href='%s'>here</a> and try to reset your account again.
            """ % reverse_lazy("change_password_request")
            self.error = mark_safe(msg)

    def get_user(self, user_id=None):
        try:
            user = self.cli.users.get(self.get_user_id())
        except:
            user = None
        if user:
            return user
        else:
            msg = """
            There was an invalid token, unable to to associate token to any user.<br />
            Please click <a href='%s'>here</a> and try to reset your account again.
            """ % reverse_lazy("change_password_request")
            self.error = mark_safe(msg)

    def form_valid(self, form):
        form.change_password(self.get_user())
        msg = """
        Your password has been successfully changed. You may <a href='%s'>sign in here</a>.
        """ % reverse_lazy('splash')
        messages.info(self.request,
                      mark_safe(msg))
        return super(ChangePasswordView, self).form_valid(form)

    def render_to_response(self, context, **response_kwargs):
        self.get_user_id()
        if self.error:
            messages.error(self.request, self.error)
            return HttpResponseRedirect(reverse_lazy('splash'))
        else:
            return super(ChangePasswordView, self).render_to_response(context, **response_kwargs)

class RegistrationView(FormSubmissionMixin):
    form_class = RegistrationForm
    template_name = "registrationindex.djhtml"
    pagedesc = "Create an Account"
    success_url = reverse_lazy("splash")
    action = "Join"

    def form_valid(self, form):
        form.register()
        msg = """
        Congratulations, you have successfully created your account.
        To activate it, please check your email and click the activation link in the email.
        If you did not receive the email, please check your junk or spam folder.<br />
        Back to <a href='%s'>Sign in</a>.
        """ % reverse_lazy('splash')
        messages.info(self.request, mark_safe(msg))
        return super(RegistrationView, self).form_valid(form)

class RequestActivation(FormSubmissionMixin):
    form_class = RequestActivationForm
    template_name = "registrationindex.djhtml"
    pagedesc = "Request Account Activation"
    success_url = reverse_lazy("request_activation")
    action = "Request"

    def form_valid(self, form):
        form.request_activation()
        msg = "Please check your email to activate your account."
        messages.info(self.request, msg)
        return super(RequestActivation, self).form_valid(form)

class ActivationView(TemplateView):
    template_name = "activate.djhtml"
    pagedesc = "Account Activation"

    def __init__(self, *args, **kwargs):
        super(ActivationView, self).__init__(*args, **kwargs)
        self.client = KeystoneCli()
        self.cli = self.client.client
        self.result = None

    def get_token_value(self):
        token = self.request.GET.get('token')
        if token:
            try:
                token_obj = Token.objects.get(token=token)
                return token_obj.value
            except:
                self.result = """
                Invalid token.<br />
                Please click <a href="%s">here</a> to request for a new activation key.
                """ % reverse_lazy("request_activation")
        else:
            self.result = """
                Activation failed.<br />
                Token is missing.
            """
        return None

    def get_tenant_id(self):
        id = self.get_token_value()
        return id

    def activate(self):
        tenant = None
        if self.get_tenant_id():
            try:
                tenant = self.cli.tenants.get(self.get_tenant_id())
            except:
                self.result = """
                Invalid token, Token is not associated to any projects or tenants.
                Click <a href='%s'>here</a> to generate a new one.
                """ % reverse_lazy("request_activation")
            if tenant:
                if not tenant.enabled:
                    self.cli.tenants.update(tenant.id, enabled=True)
                    # users = self.cli.tenants.list_users(tenant)
                    # for u in users:
                    #     self.cli.users.update_enabled(u, True)
                    self.result = """
                    Congratulations,<br />
                    Your account is now activated.<br />
                    You may <a href='%s'>Sign in here</a>
                    """ % reverse_lazy("splash")
                else:
                    msg = """
                    Your account is already activated.
                    Please <a href='%s'>sign in</a>.
                    """ % reverse_lazy('splash')
                    self.result = mark_safe(msg)
        result = self.result
        return result


    def get_context_data(self, **kwargs):
        context = super(ActivationView, self).get_context_data(**kwargs)
        context['pagedesc'] = self.pagedesc
        context['result'] = self.activate()
        return context