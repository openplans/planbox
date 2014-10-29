/*globals Backbone, jQuery, Modernizr, Handlebars */

var Planbox = Planbox || {};

(function(NS, $) {
  'use strict';

  NS.DatasetCommentCountWidgetView = Backbone.Marionette.ItemView.extend({
    template: '#dataset-comment-count-widget-tpl',
    modelEvents: {
      'change': 'render'
    }
  });

}(Planbox, jQuery));