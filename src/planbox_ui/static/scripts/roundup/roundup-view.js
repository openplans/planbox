/*globals Backbone, jQuery, Modernizr, Handlebars */

var Planbox = Planbox || {};

(function(NS, $) {
  'use strict';

  NS.RoundupView = Backbone.Marionette.Layout.extend({
    template: '#roundup-tpl',
    regions: {}
  });

}(Planbox, jQuery));