# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'Project.last_opened_by'
        db.add_column('planbox_data_project', 'last_opened_by',
                      self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'], related_name='+', blank=True, null=True),
                      keep_default=False)

        # Adding field 'Project.last_opened_at'
        db.add_column('planbox_data_project', 'last_opened_at',
                      self.gf('django.db.models.fields.DateTimeField')(blank=True, null=True),
                      keep_default=False)

        # Adding field 'Project.last_saved_by'
        db.add_column('planbox_data_project', 'last_saved_by',
                      self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'], related_name='+', blank=True, null=True),
                      keep_default=False)

        # Adding field 'Project.last_saved_at'
        db.add_column('planbox_data_project', 'last_saved_at',
                      self.gf('django.db.models.fields.DateTimeField')(blank=True, null=True),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting field 'Project.last_opened_by'
        db.delete_column('planbox_data_project', 'last_opened_by_id')

        # Deleting field 'Project.last_opened_at'
        db.delete_column('planbox_data_project', 'last_opened_at')

        # Deleting field 'Project.last_saved_by'
        db.delete_column('planbox_data_project', 'last_saved_by_id')

        # Deleting field 'Project.last_saved_at'
        db.delete_column('planbox_data_project', 'last_saved_at')


    models = {
        'auth.group': {
            'Meta': {'object_name': 'Group'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'blank': 'True', 'symmetrical': 'False'})
        },
        'auth.permission': {
            'Meta': {'object_name': 'Permission', 'ordering': "('content_type__app_label', 'content_type__model', 'codename')", 'unique_together': "(('content_type', 'codename'),)"},
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
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Group']", 'related_name': "'user_set'", 'blank': 'True', 'symmetrical': 'False'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'blank': 'True', 'max_length': '30'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'related_name': "'user_set'", 'blank': 'True', 'symmetrical': 'False'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        'contenttypes.contenttype': {
            'Meta': {'object_name': 'ContentType', 'db_table': "'django_content_type'", 'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'planbox_data.attachment': {
            'Meta': {'object_name': 'Attachment', 'ordering': "('attached_to_type', 'attached_to_id', 'index')"},
            'attached_to_id': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'attached_to_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'created_at': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'index': ('django.db.models.fields.PositiveIntegerField', [], {'blank': 'True'}),
            'label': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'thumbnail_url': ('django.db.models.fields.URLField', [], {'max_length': '2048', 'blank': 'True', 'null': 'True'}),
            'type': ('django.db.models.fields.CharField', [], {'blank': 'True', 'max_length': '256'}),
            'updated_at': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'blank': 'True'}),
            'url': ('django.db.models.fields.URLField', [], {'max_length': '2048'})
        },
        'planbox_data.event': {
            'Meta': {'object_name': 'Event', 'ordering': "('project', 'index')", 'unique_together': "[('project', 'slug')]"},
            'datetime_label': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'default': "''", 'blank': 'True'}),
            'end_datetime': ('django.db.models.fields.DateTimeField', [], {'blank': 'True', 'null': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'index': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'label': ('django.db.models.fields.TextField', [], {}),
            'project': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['planbox_data.Project']", 'related_name': "'events'"}),
            'slug': ('django.db.models.fields.CharField', [], {'blank': 'True', 'max_length': '64'}),
            'start_datetime': ('django.db.models.fields.DateTimeField', [], {'blank': 'True', 'null': 'True'})
        },
        'planbox_data.profile': {
            'Meta': {'object_name': 'Profile'},
            'affiliation': ('django.db.models.fields.CharField', [], {'default': "''", 'blank': 'True', 'max_length': '256'}),
            'auth': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['auth.User']", 'related_name': "'profile'", 'unique': 'True', 'blank': 'True', 'null': 'True'}),
            'avatar_url': ('django.db.models.fields.URLField', [], {'max_length': '200', 'blank': 'True', 'null': 'True'}),
            'created_at': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'default': "''", 'blank': 'True'}),
            'email': ('django.db.models.fields.EmailField', [], {'blank': 'True', 'max_length': '75'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'blank': 'True', 'max_length': '128'}),
            'project_editor_version': ('django.db.models.fields.PositiveIntegerField', [], {'default': '2'}),
            'slug': ('django.db.models.fields.CharField', [], {'unique': 'True', 'blank': 'True', 'max_length': '128'}),
            'teams': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['planbox_data.Profile']", 'related_name': "'members'", 'blank': 'True', 'symmetrical': 'False'}),
            'updated_at': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'blank': 'True'})
        },
        'planbox_data.project': {
            'Meta': {'object_name': 'Project', 'unique_together': "[('owner', 'slug')]"},
            'contact': ('django.db.models.fields.TextField', [], {'default': "''", 'blank': 'True'}),
            'cover_img_url': ('django.db.models.fields.URLField', [], {'blank': 'True', 'max_length': '2048'}),
            'created_at': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'blank': 'True'}),
            'details': ('jsonfield.fields.JSONField', [], {'default': '{}', 'blank': 'True'}),
            'get_involved_description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'get_involved_link_type': ('django.db.models.fields.CharField', [], {'blank': 'True', 'max_length': '16'}),
            'get_involved_link_url': ('django.db.models.fields.CharField', [], {'blank': 'True', 'max_length': '2048'}),
            'happening_now_description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'happening_now_link_type': ('django.db.models.fields.CharField', [], {'blank': 'True', 'max_length': '16'}),
            'happening_now_link_url': ('django.db.models.fields.CharField', [], {'blank': 'True', 'max_length': '2048'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_opened_at': ('django.db.models.fields.DateTimeField', [], {'blank': 'True', 'null': 'True'}),
            'last_opened_by': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']", 'related_name': "'+'", 'blank': 'True', 'null': 'True'}),
            'last_saved_at': ('django.db.models.fields.DateTimeField', [], {'blank': 'True', 'null': 'True'}),
            'last_saved_by': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']", 'related_name': "'+'", 'blank': 'True', 'null': 'True'}),
            'location': ('django.db.models.fields.TextField', [], {'default': "''", 'blank': 'True'}),
            'logo_img_url': ('django.db.models.fields.URLField', [], {'blank': 'True', 'max_length': '2048'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['planbox_data.Profile']", 'related_name': "'projects'"}),
            'public': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'slug': ('django.db.models.fields.CharField', [], {'blank': 'True', 'max_length': '128'}),
            'status': ('django.db.models.fields.CharField', [], {'default': "'not-started'", 'blank': 'True', 'max_length': '32'}),
            'template': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['planbox_data.Project']", 'on_delete': 'models.SET_NULL', 'blank': 'True', 'null': 'True'}),
            'theme': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['planbox_data.Theme']", 'related_name': "'projects'", 'on_delete': 'models.SET_NULL', 'blank': 'True', 'null': 'True'}),
            'title': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'updated_at': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'blank': 'True'})
        },
        'planbox_data.section': {
            'Meta': {'object_name': 'Section', 'ordering': "('project', 'index')", 'unique_together': "[('project', 'slug')]"},
            'active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'created_at': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'blank': 'True'}),
            'details': ('jsonfield.fields.JSONField', [], {'default': '{}', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'index': ('django.db.models.fields.PositiveIntegerField', [], {'blank': 'True'}),
            'label': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'menu_label': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'project': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['planbox_data.Project']", 'related_name': "'sections'"}),
            'slug': ('django.db.models.fields.CharField', [], {'blank': 'True', 'max_length': '30'}),
            'type': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
            'updated_at': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'blank': 'True'})
        },
        'planbox_data.theme': {
            'Meta': {'object_name': 'Theme'},
            'created_at': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'blank': 'True'}),
            'definition': ('jsonfield.fields.JSONField', [], {'default': '{}'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'blank': 'True', 'max_length': '100'}),
            'updated_at': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'blank': 'True'})
        }
    }

    complete_apps = ['planbox_data']