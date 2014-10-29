/*globals Backbone, jQuery, Modernizr, Handlebars */

var Planbox = Planbox || {};

(function(NS, $) {
  'use strict';

  NS.DatasetPlaceCountWidgetView = Backbone.Marionette.ItemView.extend({
    template: '#dataset-place-count-widget-tpl',
    modelEvents: {
      'change': 'render'
    }
  });

}(Planbox, jQuery));