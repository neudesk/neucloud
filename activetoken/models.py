from django.db import models
from django_extensions.db.fields import UUIDField

class Token(models.Model):
    token = UUIDField()
    value = models.CharField(max_length=80)

    def __unicode__(self):
        return self.token