/*globals Backbone _ */

var Planbox = Planbox || {};

(function(NS) {
  'use strict';

  Backbone.Relational.store.addModelScope(NS);

  NS.ReorderableCollection = Backbone.Collection.extend({
    moveTo: function(model, index) {
      var currentIndex = this.indexOf(model);

      if (currentIndex === index) {
        return;
      }

      this.remove(model, { silent: true});
      this.add(model, {at: index, silent: true});
      this.trigger('reorder');
    }
  });

  NS.DetailModel = Backbone.RelationalModel.extend({
    set: function(key, val, options) {
      /*
      Assign a value on the model (as Backbone.Model.set). If the attribute
      being set is not one of the top-level attributes listed in baseAttrs,
      assume it belongs in the details document for the section.

      Example:

      > model = new NS.SectionModel();
      > model.set('label', 'Hello!');
      > model.toJSON();
        {"label": "Hello!"}
      > model.set('content', '<p>Hello, world.</p>');
      > model.toJSON();
        {
          "label": "Hello!",
          "details": {"content": "<p>Hello, world.</p>"}
        }

      */
      var attr, attrs, details;

      // Process the initial arguments.
      if (typeof key === 'object') {
        attrs = key;
        options = val;
      } else {
        (attrs = {})[key] = val;
      }

      options = options || {};

      // Build up the details document if there are any attributes being set
      // that belong there.
      for (attr in attrs) {
        if (!_.contains(this.baseAttrs, attr)) {
          details = details || attrs.details || _.clone(this.get('details')) || {};
          details[attr] = attrs[attr];
          delete attrs[attr];
        }
      }

      // If we have built a details document, then set it on the attributes.
      if (details) {
        attrs.details = details;
      }
      return Backbone.RelationalModel.prototype.set.call(this, attrs, options);
    }
  });


  NS.ProjectModel = NS.DetailModel.extend({
    baseAttrs: ['details', 'id', 'created_at', 'updated_at', 'title', 'slug',
                'public', 'status', 'location', 'contact', 'owner',
                'cover_img_url', 'logo_img_url', 'events', 'sections',
                'template', 'theme', 'description',
                'happening_now_description', 'happening_now_link_type',
                'happening_now_link_url', 'get_involved_description',
                'get_involved_link_type', 'get_involved_link_url'],

    relations: [{
      type: Backbone.HasMany,
      key: 'events',
      relatedModel: 'EventModel',
      collectionType: 'EventCollection'
    },
    {
      type: Backbone.HasMany,
      key: 'sections',
      relatedModel: 'SectionModel',
      collectionType: 'SectionCollection',
      reverseRelation: {
        key: 'project'
      }
    }],
    urlRoot: '/api/v1/projects',

    clean: function(options) {
      // Remove empty events
      var events = this.get('events'),
          label, descr;
      events.each(function(evt) {
        label = evt.get('label');
        descr = evt.get('description');
        if ((_.isUndefined(label) || _.isNull(label) || label.trim() === '') &&
            (_.isUndefined(descr) || _.isNull(descr) || descr.trim() === '')) {
          events.remove(evt);
        }
      });
    },

    markAsOpenedBy: function(user, options) {
      var endpoint = this.url() + '/activity';
      $.ajax(_.defaults({
        type: 'POST',
        url: endpoint,
        data: JSON.stringify(user),
        dataType: 'json'
      }, options));
    },

    markAsClosed: function(options) {
      var endpoint = this.url() + '/activity';
      $.ajax(_.defaults({
        type: 'DELETE',
        url: endpoint,
        dataType: 'json'
      }, options));
    }
  });

  NS.SectionModel = NS.DetailModel.extend({
    baseAttrs: ['details', 'id', 'created_at', 'updated_at', 'type', 'label',
                'menu_label', 'slug', 'active']
  });

  NS.SectionCollection = NS.ReorderableCollection.extend({
    model: NS.SectionModel
  });

  NS.AttachmentModel = Backbone.RelationalModel.extend({});

  NS.AttachmentCollection = NS.ReorderableCollection.extend({
    model: NS.AttachmentModel
  });

  NS.EventModel = Backbone.RelationalModel.extend({
    relations: [{
      type: Backbone.HasMany,
      key: 'attachments',
      relatedModel: 'AttachmentModel',
      collectionType: 'AttachmentCollection'
    }]
  });

  NS.EventCollection = NS.ReorderableCollection.extend({
    model: NS.EventModel
  });

  NS.FaqModel = Backbone.RelationalModel.extend({});

  NS.FaqCollection = NS.ReorderableCollection.extend({
    model: NS.FaqModel
  });


  NS.RoundupModel = NS.DetailModel.extend({
    baseAttrs: ['details', 'id', 'created_at', 'updated_at', 'title', 'slug',
                'owner', 'template', 'theme'],

    relations: [],
    urlRoot: '/api/v1/roundups'
  });


  NS.ProfileModel = Backbone.RelationalModel.extend({
    urlRoot: '/api/v1/profiles',
    relations: [{
      type: Backbone.HasMany,
      key: 'projects',
      relatedModel: 'OwnedProjectModel',
      collectionType: 'OwnedProjectCollection',
      reverseRelation: {
        key: 'owner',
        includeInJSON: 'slug'
      }
    }, {
      type: Backbone.HasMany,
      key: 'members',
      relatedModel: 'MemberProfileModel'
    }, {
      type: Backbone.HasMany,
      key: 'teams',
      relatedModel: 'TeamProfileModel',
      collectionType: 'TeamProfileCollection'
    }]
  });

  NS.OwnedProjectModel = Backbone.RelationalModel.extend({});
  NS.OwnedProjectCollection = Backbone.Collection.extend({
    model: NS.OwnedProjectModel,
    url: '/api/v1/projects'
  });

  NS.MemberProfileModel = Backbone.RelationalModel.extend({});

  NS.TeamProfileModel = Backbone.RelationalModel.extend({});
  NS.TeamProfileCollection = Backbone.Collection.extend({
    model: NS.TeamProfileModel,
    url: '/api/v1/profiles'
  });

}(Planbox));
