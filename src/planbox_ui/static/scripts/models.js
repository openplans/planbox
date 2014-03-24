/*globals Backbone */

var Planbox = Planbox || {};

(function(NS) {
  'use strict';

  Backbone.Relational.store.addModelScope(NS);

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

  NS.SectionCollection = Backbone.Collection.extend({
    model: NS.SectionModel,
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

  NS.EventModel = Backbone.RelationalModel.extend({});

  NS.EventCollection = Backbone.Collection.extend({
    model: NS.EventModel,
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

}(Planbox));
