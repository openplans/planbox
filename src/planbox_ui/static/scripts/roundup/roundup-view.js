/*globals Backbone, jQuery, Modernizr, Handlebars */

var Planbox = Planbox || {};

(function(NS, $) {
  'use strict';

  NS.RoundupView = Backbone.Marionette.Layout.extend({
    template: '#roundup-tpl',
    regions: {
      ownerDetailRegion: '.owner-detail'
    },

    onShow: function() {
      this.showRegions();
    },

    showRegions: function() {
      this.ownerDetailRegion.show(new NS.OwnerDetailView({
        model: this.model.get('owner')
      }));
    }
  });

}(Planbox, jQuery));