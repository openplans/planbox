/*globals Backbone jQuery Handlebars */

var Planbox = Planbox || {};

(function(NS, $) {
  'use strict';

    // Handlebars support for Marionette
  Backbone.Marionette.TemplateCache.prototype.compileTemplate = function(rawTemplate) {
    return Handlebars.compile(rawTemplate);
  };

  NS.ProjectView = Backbone.Marionette.ItemView.extend({
    template: '#project-tpl'
  });

}(Planbox, jQuery));