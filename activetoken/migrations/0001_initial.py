# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Token'
        db.create_table(u'activetoken_token', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('token', self.gf('django.db.models.fields.CharField')(max_length=36, blank=True)),
            ('value', self.gf('django.db.models.fields.CharField')(max_length=80)),
        ))
        db.send_create_signal(u'activetoken', ['Token'])


    def backwards(self, orm):
        # Deleting model 'Token'
        db.delete_table(u'activetoken_token')


    models = {
        u'activetoken.token': {
            'Meta': {'object_name': 'Token'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'token': ('django.db.models.fields.CharField', [], {'max_length': '36', 'blank': 'True'}),
            'value': ('django.db.models.fields.CharField', [], {'max_length': '80'})
        }
    }

    complete_apps = ['activetoken']