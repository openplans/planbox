# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Removing unique constraint on 'Project', fields ['owner_type', 'owner_id', 'slug']
        db.delete_unique(u'planbox_data_project', ['owner_type_id', 'owner_id', 'slug'])

        # Deleting model 'Organization'
        db.delete_table(u'planbox_data_organization')

        # Deleting model 'User'
        db.delete_table(u'planbox_data_user')

        # Removing M2M table for field organizations on 'User'
        db.delete_table(db.shorten_name(u'planbox_data_user_organizations'))

        # Deleting field 'Project.owner_type'
        db.delete_column(u'planbox_data_project', 'owner_type_id')

        # Deleting field 'Project.owner_id'
        db.delete_column(u'planbox_data_project', 'owner_id')

        # Renaming field 'Project.profile' to 'Project.owner'
        db.rename_column(u'planbox_data_project', 'profile_id', 'owner_id')

        # Alter the owner column to not be null
        db.alter_column(u'planbox_data_project', 'owner_id', models.ForeignKey(orm['planbox_data.Profile'], related_name='projects', null=False))

        # Adding unique constraint on 'Project', fields ['owner', 'slug']
        db.create_unique(u'planbox_data_project', ['owner_id', 'slug'])


    def backwards(self, orm):
        # Removing unique constraint on 'Project', fields ['owner', 'slug']
        db.delete_unique(u'planbox_data_project', ['owner_id', 'slug'])

        # Alter the owner column to allow null values
        db.alter_column(u'planbox_data_project', 'owner_id', models.ForeignKey(orm['planbox_data.Profile'], related_name='projects', null=True))

        # Renaming field 'Project.owner' to 'Project.profile'
        db.rename_column(u'planbox_data_project', 'owner_id', 'profile_id')

        # Adding field 'Project.owner_id'
        db.add_column(u'planbox_data_project', 'owner_id',
                      self.gf('django.db.models.fields.PositiveIntegerField')(null=True),
                      keep_default=False)

        # Adding field 'Project.owner_type'
        db.add_column(u'planbox_data_project', 'owner_type',
                      self.gf('django.db.models.fields.related.ForeignKey')(null=True, to=orm['contenttypes.ContentType']),
                      keep_default=False)

        # Adding model 'Organization'
        db.create_table(u'planbox_data_organization', (
            ('slug', self.gf('django.db.models.fields.CharField')(max_length=128)),
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=128)),
        ))
        db.send_create_signal(u'planbox_data', ['Organization'])

        # Adding model 'User'
        db.create_table(u'planbox_data_user', (
            ('auth', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['auth.User'], unique=True, null=True)),
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('affiliation', self.gf('django.db.models.fields.CharField')(default=u'', max_length=256, blank=True)),
            ('slug', self.gf('django.db.models.fields.CharField')(max_length=128)),
        ))
        db.send_create_signal(u'planbox_data', ['User'])

        # Adding M2M table for field organizations on 'User'
        m2m_table_name = db.shorten_name(u'planbox_data_user_organizations')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('user', models.ForeignKey(orm[u'planbox_data.user'], null=False)),
            ('organization', models.ForeignKey(orm[u'planbox_data.organization'], null=False))
        ))
        db.create_unique(m2m_table_name, ['user_id', 'organization_id'])

        # Adding unique constraint on 'Project', fields ['owner_type', 'owner_id', 'slug']
        db.create_unique(u'planbox_data_project', ['owner_type_id', 'owner_id', 'slug'])


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
            'Meta': {'unique_together': "[(u'owner', u'slug')]", 'object_name': 'Project'},
            'contact': ('django.db.models.fields.TextField', [], {'default': "u''", 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'default': "u''", 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'location': ('django.db.models.fields.CharField', [], {'default': "u''", 'max_length': '256', 'blank': 'True'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'projects'", 'to': u"orm['planbox_data.Profile']"}),
            'public': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'slug': ('django.db.models.fields.CharField', [], {'max_length': '128', 'blank': 'True'}),
            'status': ('django.db.models.fields.CharField', [], {'default': "u'not-started'", 'max_length': '32'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '1024'})
        }
    }

    complete_apps = ['planbox_data']