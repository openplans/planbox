/*globals Backbone, jQuery, Modernizr, Handlebars */

var Planbox = Planbox || {};

(function(NS, $) {
  'use strict';

  // Exceptions ===============================================================
  NS.genericException = function(name, message, data) {
    var exc = {
      name: name,
      message: message,
      data: data,
      toString: function() { return message; }
    };
    return exc;
  };

  // App ======================================================================
  NS.app = new Backbone.Marionette.Application();

  NS.app.addRegions({
    mainRegion: '#page',
    modalRegion: '#modal-container'
  });

  NS.app.addInitializer(function() {
    // Handlebars support for Marionette
    Backbone.Marionette.TemplateCache.prototype.compileTemplate = function(rawTemplate) {
      return Handlebars.compile(rawTemplate);
    };
  });

  // Init =====================================================================
  $(function() {
    NS.app.start();
  });

  $(window).load(function() {
    // Moved this from the BaseProjectView onDomRefresh. This will wait until
    // all of the images have been loaded so that Magellan will funciton as
    // expected. Specifically, "sticking" to the right location when scrolling
    // and not overlapping with section title when someone links directly to
    // a hash.
    $(document).foundation({'magellan': {}});
  });

}(Planbox, jQuery));