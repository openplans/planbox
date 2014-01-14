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
    }]
  });

  NS.EventModel = Backbone.RelationalModel.extend({});

  NS.EventCollection = Backbone.Collection.extend({
    model: NS.EventModel
  });


}(Planbox));