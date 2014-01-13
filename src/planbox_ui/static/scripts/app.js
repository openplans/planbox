/*globals Backbone jQuery Modernizr */

var Planbox = Planbox || {};

(function(NS, $) {
  'use strict';

  // Router ===================================================================
  NS.router = new Backbone.Marionette.AppRouter({
    controller: NS.controller,
    appRoutes: {
      ':slug':        'showProject',
      '*anything':    'anything'
    }
  });

  // App ======================================================================
  NS.app = new Backbone.Marionette.Application();

  NS.app.addRegions({
    mainRegion: 'body'
  });

  NS.app.addInitializer(function(options){
    NS.app.projectCollection = new Backbone.Collection(NS.projects);
    Backbone.history.start({ pushState: Modernizr.history, root: "project/" });
  });

  // Init =====================================================================
  $(function() {
    NS.app.start();
  });

}(Planbox, jQuery));