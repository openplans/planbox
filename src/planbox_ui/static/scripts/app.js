/*globals Backbone jQuery Modernizr */

var Planbox = Planbox || {};

(function(NS, $) {
  'use strict';

  // App ======================================================================
  NS.app = new Backbone.Marionette.Application();

  NS.app.addRegions({
    mainRegion: '#page',
    overlayRegion: '#overlay-container'
  });

  NS.app.addInitializer(function(options){
    var projectModel, ProjectView;

    if (NS.Data.isOwner && !NS.Data.project.owner_id) {
      NS.Data.project.owner = NS.Data.user.username;
    }

    projectModel = new NS.ProjectModel(NS.Data.project);
    ProjectView = NS.Data.isOwner ? NS.ProjectAdminView : NS.ProjectView;

    NS.app.mainRegion.show(new ProjectView({
      model: projectModel,
      collection: projectModel.get('events')
    }));
  });

  // Init =====================================================================
  $(function() {
    NS.app.start();
  });

}(Planbox, jQuery));