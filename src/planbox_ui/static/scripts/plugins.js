/*globals Backbone, jQuery, Modernizr, Handlebars */

var Planbox = Planbox || {};

(function(NS, $) {
  'use strict';

  NS.Plugin = function(app) {
    this.app = app;
    this.initialize.apply(this, arguments);
    return this;
  };

  _.extend(NS.Plugin.prototype, Backbone.Events, {
    initialize: function() {}
  });

  NS.Plugin.extend = Backbone.Model.extend;

}(Planbox, jQuery));