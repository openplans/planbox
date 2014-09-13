/*globals Backbone, jQuery, Modernizr, Handlebars */

var Planbox = Planbox || {};

(function(NS, $) {
  'use strict';

  NS.OwnerDetailView = Backbone.Marionette.ItemView.extend({
    template: '#owner-detail-tpl'
  });

}(Planbox, jQuery));