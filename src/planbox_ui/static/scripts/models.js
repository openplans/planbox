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
