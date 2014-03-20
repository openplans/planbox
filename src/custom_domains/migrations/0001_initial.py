# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'DomainMapping'
        db.create_table(u'custom_domains_domainmapping', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('domain', self.gf('django.db.models.fields.CharField')(max_length=250)),
            ('root_path', self.gf('django.db.models.fields.CharField')(max_length=250)),
        ))
        db.send_create_signal(u'custom_domains', ['DomainMapping'])


    def backwards(self, orm):
        # Deleting model 'DomainMapping'
        db.delete_table(u'custom_domains_domainmapping')


    models = {
        u'custom_domains.domainmapping': {
            'Meta': {'object_name': 'DomainMapping'},
            'domain': ('django.db.models.fields.CharField', [], {'max_length': '250'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'root_path': ('django.db.models.fields.CharField', [], {'max_length': '250'})
        }
    }

    complete_apps = ['custom_domains']