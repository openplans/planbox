/*globals Backbone */

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

  NS.ProjectModel = Backbone.RelationalModel.extend({
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
    }
  });

  NS.SectionModel = Backbone.RelationalModel.extend({
    baseAttrs: ['details', 'id', 'created_at', 'updated_at', 'type', 'label', 'menu_label', 'slug'],

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

  NS.FaqsSectionModel = NS.SectionModel.extend({
    relations: [{
      type: Backbone.HasMany,
      key: 'details',
      relatedModel: 'FaqModel',
      collectionType: 'FaqCollection'
    }]
  });

  NS.sectionModelFactory = function(attributes) {
    if (!attributes) {
      return new NS.SectionModel.apply(this, arguments);
    }

    switch (attributes.type) {
    case 'faqs':
      return new NS.FaqsSectionModel.apply(this, arguments);
    default:
      return new NS.SectionModel.apply(this, arguments);
    }
  };

  NS.SectionCollection = NS.ReorderableCollection.extend({
    model: NS.sectionModelFactory
  });

  NS.EventModel = Backbone.RelationalModel.extend({});

  NS.EventCollection = NS.ReorderableCollection.extend({
    model: NS.EventModel
  });

  NS.FaqModel = Backbone.RelationalModel.extend({});

  NS.FaqCollection = NS.ReorderableCollection.extend({
    model: NS.FaqModel
  });

}(Planbox));
