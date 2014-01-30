import requests, os
from django.template.loader import get_template
from django.template import Context
from django.conf import settings

class Mailer(object):

    def __init__(self, subject=None, message=None, fr=None, recipients=[]):
        self.html = get_template("htmlmail.djhtml")
        self.txt = get_template("textmail.txt")
        self.message = message
        self.fr = fr
        self.recipients = recipients
        self.subject = subject

    def get_context_data(self):
        data = Context({"message": self.message})
        return data

    def render(self):
        html = self.html.render(self.get_context_data())
        text = self.txt.render(self.get_context_data())
        return text, html

    def send(self):
        text, html = self.render()
        r = requests.post(settings.MAIL_API_ENDPOINT,
                          auth=("api", settings.MAIL_API_KEY),
                          data={"from": self.fr,
                                "to": [self.recipients],
                                "subject": self.subject,
                                "text": text,
                                "html": html})
        return r.status_code
