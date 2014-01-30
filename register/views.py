from django.core.urlresolvers import reverse_lazy
from django.contrib import messages
from django.views.generic import FormView, TemplateView
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

class RegistrationView(FormSubmissionMixin):
    form_class = RegistrationForm
    template_name = "registrationindex.djhtml"
    pagedesc = "Create Account"
    success_url = reverse_lazy("splash")
    action = "Register"

    def form_valid(self, form):
        form.register()
        msg = "Congratulations, You have successfully created an account, Please check your email to activate."
        messages.info(self.request, msg)
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

    def get_tenant_id(self):
        id = self.request.GET.get('token')
        if not id:
            self.result = """
                Activation failed.<br />
                Token is missing.
            """
        return id

    def activate(self):
        tenant = None
        if self.get_tenant_id():
            try:
                tenant = self.cli.tenants.get(self.get_tenant_id())
            except:
                self.result = """
                Invalid token,
                Click <a href='%s'>here</a> to generate a new one.
                """ % reverse_lazy("request_activation")
            if tenant:
                if not tenant.enabled:
                    self.cli.tenants.update(tenant.id, enabled=True)
                    users = self.cli.tenants.list_users(tenant)
                    for u in users:
                        self.cli.users.update_enabled(u, True)
                    self.result = """
                    Congratulations,<br />
                    Your account is now activated.<br />
                    You may now sign in here <a href='%s'>Sign in</a>
                    """ % reverse_lazy("splash")
                else:
                    self.result = """
                    Your project and your account is already active,
                    you don't need to reactivate.
                    """
        result = self.result
        return result


    def get_context_data(self, **kwargs):
        context = super(ActivationView, self).get_context_data(**kwargs)
        context['pagedesc'] = self.pagedesc
        context['result'] = self.activate()
        return context