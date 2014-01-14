/*globals Backbone jQuery Modernizr */

var Planbox = Planbox || {};

(function(NS, $) {
  'use strict';

  // App ======================================================================
  NS.app = new Backbone.Marionette.Application();

  NS.app.addRegions({
    mainRegion: '#page'
  });

  NS.app.addInitializer(function(options){
    var projectModel = new Backbone.Model(NS.Data.project);

    NS.app.mainRegion.show(new NS.ProjectView({
      model: projectModel
    }));
  });

  // Init =====================================================================
  $(function() {
    NS.app.start();
  });

}(Planbox, jQuery));