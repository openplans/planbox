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
    var projectModel = new NS.ProjectModel(NS.Data.project);

    NS.app.mainRegion.show(new NS.ProjectAdminView({
      model: projectModel,
      collection: projectModel.get('events')
    }));
  });

  // Init =====================================================================
  $(function() {
    NS.app.start();
  });

}(Planbox, jQuery));