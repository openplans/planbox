/*globals Backbone, jQuery, Modernizr, Handlebars */

var Planbox = Planbox || {};

(function(NS, $) {
  'use strict';

  NS.RoundupView = Backbone.Marionette.Layout.extend({
    template: '#roundup-tpl',
    regions: {
      ownerDetailRegion: '.owner-detail-region',
      projectListRegion: '.project-list-region',
      projectMapRegion: '.project-map-region'
    },

    onShow: function() {
      this.showRegions();
    },

    showRegions: function() {
      this.ownerDetailRegion.show(new NS.OwnerDetailView({
        model: this.model.get('owner')
      }));

      this.projectListRegion.show(new NS.ProjectListView({
        model: this.model,
        collection: this.model.get('projects')
      }));

      this.projectMapRegion.show(new NS.ProjectMapView({
        model: this.model,
        collection: this.model.get('projects')
      }));
    }
  });

}(Planbox, jQuery));