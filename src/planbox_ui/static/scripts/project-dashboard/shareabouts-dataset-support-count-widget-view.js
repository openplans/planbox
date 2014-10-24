/*globals Backbone, jQuery, Modernizr, Handlebars */

var Planbox = Planbox || {};

(function(NS, $) {
  'use strict';

  NS.DatasetSupportCountWidgetView = Backbone.Marionette.ItemView.extend({
    template: '#dataset-support-count-widget-tpl',
    modelEvents: {
      'change': 'render'
    }
  });

}(Planbox, jQuery));