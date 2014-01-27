# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import DataMigration
from django.db import models

class Migration(DataMigration):

    def forwards(self, orm):
        "Write your forwards methods here."

        ContentType = orm['contenttypes.ContentType']
        try:
            user_ct = ContentType.objects.get(model='user', app_label='planbox_data')
            org_ct = ContentType.objects.get(model='organization', app_label='planbox_data')

        except ContentType.DoesNotExist:
            user_ct = ContentType.objects.create(model='user', app_label='planbox_data', name='User Profile')
            org_ct = ContentType.objects.create(model='organization', app_label='planbox_data', name='Organization Profile')

        user_profile_map = {}
        for user_profile in orm.User.objects.all():
            profile = orm.Profile.objects.create(
                slug=user_profile.slug,
                auth=user_profile.auth,
                affiliation=user_profile.affiliation,
            )

            for project in orm.Project.objects.filter(owner_type_id=user_ct.pk, owner_id=user_profile.pk):
                project.profile = profile
                project.save()

            # Map the profile for adding to organizations later
            user_profile_map[user_profile] = profile

        for org_profile in orm.Organization.objects.all():
            orm.Profile.objects.create(
                name=org_profile.name,
                slug=org_profile.slug,
            )

            for project in orm.Project.objects.filter(owner_type_id=org_ct.pk, owner_id=user_profile.pk):
                project.profile = profile
                project.save()

            for member in org_profile.members.all():
                user_profile_map[member].organizations.add(org_profile)

    def backwards(self, orm):
        "Write your backwards methods here."

        ContentType = orm['contenttypes.ContentType']
        try:
            user_ct = ContentType.objects.get(model='user', app_label='planbox_data')
            org_ct = ContentType.objects.get(model='organization', app_label='planbox_data')

        except ContentType.DoesNotExist:
            user_ct = ContentType.objects.create(model='user', app_label='planbox_data', name='User Profile')
            org_ct = ContentType.objects.create(model='organization', app_label='planbox_data', name='Organization Profile')

        user_profile_map = {}
        for user_profile in orm.Profile.objects.filter(auth__isnull=False):
            profile = orm.User.objects.create(
                slug=user_profile.slug,
                auth=user_profile.auth,
                affiliation=user_profile.affiliation,
            )

            for project in user_profile.projects.all():
                project.owner_id = profile.pk
                project.owner_type = user_ct
                project.save()

            # Map the profile for adding to organizations later
            user_profile_map[user_profile] = profile

        for org_profile in orm.Profile.objects.filter(auth__isnull=True):
            profile = orm.Organization.objects.create(
                name=org_profile.name,
                slug=org_profile.slug,
            )

            for project in org_profile.projects.all():
                project.owner_id = profile.pk
                project.owner_type = org_ct
                project.save()

            for member in org_profile.members.all():
                user_profile_map[member].organizations.add(org_profile)

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
            'profile': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'projects'", 'to': u"orm['planbox_data.Profile']"}),
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
    symmetrical = True
