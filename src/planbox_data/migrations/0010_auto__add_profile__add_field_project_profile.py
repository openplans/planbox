# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Profile'
        db.create_table(u'planbox_data_profile', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=128)),
            ('slug', self.gf('django.db.models.fields.CharField')(unique=True, max_length=128)),
            ('auth', self.gf('django.db.models.fields.related.OneToOneField')(blank=True, related_name=u'profile', unique=True, null=True, to=orm['auth.User'])),
            ('affiliation', self.gf('django.db.models.fields.CharField')(default=u'', max_length=256, blank=True)),
        ))
        db.send_create_signal(u'planbox_data', ['Profile'])

        # Adding M2M table for field members on 'Profile'
        m2m_table_name = db.shorten_name(u'planbox_data_profile_members')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('from_profile', models.ForeignKey(orm[u'planbox_data.profile'], null=False)),
            ('to_profile', models.ForeignKey(orm[u'planbox_data.profile'], null=False))
        ))
        db.create_unique(m2m_table_name, ['from_profile_id', 'to_profile_id'])

        # Adding field 'Project.profile'
        db.add_column(u'planbox_data_project', 'profile',
                      self.gf('django.db.models.fields.related.ForeignKey')(null=True, to=orm['planbox_data.Profile']),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting field 'Project.profile'
        db.delete_column(u'planbox_data_project', 'profile_id')

        # Removing M2M table for field members on 'Profile'
        db.delete_table(db.shorten_name(u'planbox_data_profile_members'))

        # Deleting model 'Profile'
        db.delete_table(u'planbox_data_profile')

        # Alter Project.owner_type and Project.owner_id to not be null
        db.alter_column(u'planbox_data_project', 'owner_type_id', models.ForeignKey(orm['contenttypes.ContentType'], null=False))
        db.alter_column(u'planbox_data_project', 'owner_id', models.PositiveIntegerField(null=False))

    models = {
        u'auth.group': {
            'Meta': {'object_name': 'Group'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        u'auth.permission': {
            'Meta': {'ordering': "(u'content_type__app_label', u'content_type__model', u'codename')", 'unique_together': "((u'content_type', u'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contenttypes.ContentType']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        u'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "u'user_set'", 'blank': 'True', 'to': u"orm['auth.Group']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "u'user_set'", 'blank': 'True', 'to': u"orm['auth.Permission']"}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        u'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        u'planbox_data.event': {
            'Meta': {'ordering': "(u'project', u'index')", 'object_name': 'Event'},
            'description': ('django.db.models.fields.TextField', [], {'default': "u''", 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'index': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'label': ('django.db.models.fields.CharField', [], {'max_length': '1024'}),
            'project': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'events'", 'to': u"orm['planbox_data.Project']"})
        },
        u'planbox_data.organization': {
            'Meta': {'object_name': 'Organization'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'slug': ('django.db.models.fields.CharField', [], {'max_length': '128'})
        },
        u'planbox_data.profile': {
            'Meta': {'object_name': 'Profile'},
            'affiliation': ('django.db.models.fields.CharField', [], {'default': "u''", 'max_length': '256', 'blank': 'True'}),
            'auth': ('django.db.models.fields.related.OneToOneField', [], {'blank': 'True', 'related_name': "u'profile'", 'unique': 'True', 'null': 'True', 'to': u"orm['auth.User']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'members': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "u'organizations'", 'blank': 'True', 'to': u"orm['planbox_data.Profile']"}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'slug': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '128'})
        },
        u'planbox_data.project': {
            'Meta': {'unique_together': "[(u'owner_type', u'owner_id', u'slug')]", 'object_name': 'Project'},
            'contact': ('django.db.models.fields.TextField', [], {'default': "u''", 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'default': "u''", 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'location': ('django.db.models.fields.CharField', [], {'default': "u''", 'max_length': '256', 'blank': 'True'}),
            'owner_id': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'owner_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contenttypes.ContentType']"}),
            'profile': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['planbox_data.Profile']"}),
            'public': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'slug': ('django.db.models.fields.CharField', [], {'max_length': '128', 'blank': 'True'}),
            'status': ('django.db.models.fields.CharField', [], {'default': "u'not-started'", 'max_length': '32'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '1024'})
        },
        u'planbox_data.user': {
            'Meta': {'object_name': 'User'},
            'affiliation': ('django.db.models.fields.CharField', [], {'default': "u''", 'max_length': '256', 'blank': 'True'}),
            'auth': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['auth.User']", 'unique': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'organizations': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "u'members'", 'blank': 'True', 'to': u"orm['planbox_data.Organization']"}),
            'slug': ('django.db.models.fields.CharField', [], {'max_length': '128'})
        }
    }

    complete_apps = ['planbox_data']