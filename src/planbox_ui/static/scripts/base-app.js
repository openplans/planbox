/*globals Backbone, jQuery, Modernizr, Handlebars */

var Planbox = Planbox || {};

(function(NS, $) {
  'use strict';

  // Exceptions ===============================================================
  NS.genericException = function(name, message, data) {
    var exc = new Error(message);
    exc.name = name;
    exc.data = data;
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

  NS.app.addInitializer(function() {
    // Do simple protection against accidental drops of images outside of
    // drop areas (http://stackoverflow.com/a/6756680).
    window.addEventListener('dragover', function(e) {
      e = e || event;
      e.preventDefault();
    }, false);
    window.addEventListener('drop', function(e) {
      e = e || event;
      e.preventDefault();
    }, false);
  });

  NS.app.addInitializer(function(options) {
    NS.Utils.logEvents('body', 'profile-dashboard');
  });

  // Init =====================================================================
  $(function() {
    NS.app.start();
  });

  $(window).load(function() {
    // This will wait until all of the images have been loaded so that Magellan
    // will funciton as expected. Specifically, "sticking" to the right
    // location when scrolling and not overlapping with section title when
    // someone links directly to a hash.
    $(document).foundation({'magellan': {}});
  });

}(Planbox, jQuery));