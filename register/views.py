from django.core.urlresolvers import reverse_lazy
from django.contrib import messages
from django.views.generic import FormView
from .forms import *

class FormSubmissionMixin(FormView):
    form_class = None
    template_name = None
    success_url = None

    def get_context_data(self, **kwargs):
        context = super(FormSubmissionMixin, self).get_context_data(**kwargs)
        context['pagedesc'] = self.pagedesc
        return context

class RegistrationView(FormSubmissionMixin):
    form_class = RegistrationForm
    template_name = "registrationindex.djhtml"
    pagedesc = "Create Account"
    success_url = reverse_lazy("request_activation")

    def form_valid(self, form):
        form.register()
        msg = "Congratulations, You have successfully created an account, Please check your email to activate."
        messages.info(self.request, msg)
        return super(RegistrationView, self).form_valid(form)

class RequestActivation(FormSubmissionMixin):
    form_class = RequestActivationForm
    template_name = "requestactivation.djhtml"
    pagedesc = "Request Account Activation"
    success_url = reverse_lazy("request_activation")

    def form_valid(self, form):
        form.request_activation()
        msg = "Please check your email to activate your account."
        messages.info(self.request, msg)
        return super(RequestActivation, self).form_valid(form)
