# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'Project.cover_img_url'
        db.add_column('planbox_data_project', 'cover_img_url',
                      self.gf('django.db.models.fields.URLField')(blank=True, default='', max_length=2048),
                      keep_default=False)

        # Adding field 'Project.logo_img_url'
        db.add_column('planbox_data_project', 'logo_img_url',
                      self.gf('django.db.models.fields.URLField')(blank=True, default='', max_length=2048),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting field 'Project.cover_img_url'
        db.delete_column('planbox_data_project', 'cover_img_url')

        # Deleting field 'Project.logo_img_url'
        db.delete_column('planbox_data_project', 'logo_img_url')


    models = {
        'auth.group': {
            'Meta': {'object_name': 'Group'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '80', 'unique': 'True'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'symmetrical': 'False', 'to': "orm['auth.Permission']"})
        },
        'auth.permission': {
            'Meta': {'ordering': "('content_type__app_label', 'content_type__model', 'codename')", 'object_name': 'Permission', 'unique_together': "(('content_type', 'codename'),)"},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'blank': 'True', 'max_length': '75'}),
            'first_name': ('django.db.models.fields.CharField', [], {'blank': 'True', 'max_length': '30'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'symmetrical': 'False', 'related_name': "'user_set'", 'to': "orm['auth.Group']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'blank': 'True', 'max_length': '30'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'symmetrical': 'False', 'related_name': "'user_set'", 'to': "orm['auth.Permission']"}),
            'username': ('django.db.models.fields.CharField', [], {'max_length': '30', 'unique': 'True'})
        },
        'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'object_name': 'ContentType', 'unique_together': "(('app_label', 'model'),)", 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'planbox_data.event': {
            'Meta': {'ordering': "('project', 'index')", 'object_name': 'Event'},
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True', 'default': "''"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'index': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'label': ('django.db.models.fields.CharField', [], {'max_length': '1024'}),
            'project': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['planbox_data.Project']", 'related_name': "'events'"})
        },
        'planbox_data.profile': {
            'Meta': {'object_name': 'Profile'},
            'affiliation': ('django.db.models.fields.CharField', [], {'blank': 'True', 'default': "''", 'max_length': '256'}),
            'auth': ('django.db.models.fields.related.OneToOneField', [], {'blank': 'True', 'unique': 'True', 'to': "orm['auth.User']", 'related_name': "'profile'", 'null': 'True'}),
            'created_at': ('django.db.models.fields.DateTimeField', [], {'blank': 'True', 'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'blank': 'True', 'max_length': '75'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'blank': 'True', 'max_length': '128'}),
            'organizations': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'symmetrical': 'False', 'related_name': "'members'", 'to': "orm['planbox_data.Profile']"}),
            'slug': ('django.db.models.fields.CharField', [], {'max_length': '128', 'unique': 'True'}),
            'updated_at': ('django.db.models.fields.DateTimeField', [], {'blank': 'True', 'default': 'datetime.datetime.now'})
        },
        'planbox_data.project': {
            'Meta': {'object_name': 'Project', 'unique_together': "[('owner', 'slug')]"},
            'contact': ('django.db.models.fields.TextField', [], {'blank': 'True', 'default': "''"}),
            'cover_img_url': ('django.db.models.fields.URLField', [], {'blank': 'True', 'max_length': '2048'}),
            'created_at': ('django.db.models.fields.DateTimeField', [], {'blank': 'True', 'default': 'datetime.datetime.now'}),
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True', 'default': "''"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'location': ('django.db.models.fields.CharField', [], {'blank': 'True', 'default': "''", 'max_length': '256'}),
            'logo_img_url': ('django.db.models.fields.URLField', [], {'blank': 'True', 'max_length': '2048'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['planbox_data.Profile']", 'related_name': "'projects'"}),
            'public': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'slug': ('django.db.models.fields.CharField', [], {'blank': 'True', 'max_length': '128'}),
            'status': ('django.db.models.fields.CharField', [], {'blank': 'True', 'default': "'not-started'", 'max_length': '32'}),
            'template': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'to': "orm['planbox_data.Project']", 'null': 'True'}),
            'theme': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'to': "orm['planbox_data.Theme']", 'related_name': "'projects'", 'null': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'blank': 'True', 'max_length': '1024'}),
            'updated_at': ('django.db.models.fields.DateTimeField', [], {'blank': 'True', 'default': 'datetime.datetime.now'})
        },
        'planbox_data.section': {
            'Meta': {'ordering': "('project', 'index')", 'object_name': 'Section'},
            'created_at': ('django.db.models.fields.DateTimeField', [], {'blank': 'True', 'default': 'datetime.datetime.now'}),
            'details': ('jsonfield.fields.JSONField', [], {'blank': 'True', 'default': '{}'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'index': ('django.db.models.fields.PositiveIntegerField', [], {'blank': 'True'}),
            'label': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'menu_label': ('django.db.models.fields.TextField', [], {}),
            'project': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['planbox_data.Project']", 'related_name': "'sections'"}),
            'slug': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
            'type': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
            'updated_at': ('django.db.models.fields.DateTimeField', [], {'blank': 'True', 'default': 'datetime.datetime.now'})
        },
        'planbox_data.theme': {
            'Meta': {'object_name': 'Theme'},
            'created_at': ('django.db.models.fields.DateTimeField', [], {'blank': 'True', 'default': 'datetime.datetime.now'}),
            'css_url': ('django.db.models.fields.URLField', [], {'blank': 'True', 'max_length': '200'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'updated_at': ('django.db.models.fields.DateTimeField', [], {'blank': 'True', 'default': 'datetime.datetime.now'})
        }
    }

    complete_apps = ['planbox_data']