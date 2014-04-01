/*globals Backbone jQuery Modernizr */

var Planbox = Planbox || {};

(function(NS, $) {
  'use strict';

  // Exceptions ===============================================================
  NS.projectException = function(message, data) {
    var exc = {
      name: 'ProjectException',
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
    overlayRegion: '#overlay-container'
  });

  NS.app.addInitializer(function(options){
    var projectModel, ProjectView;

    if (NS.Data.isOwner && !NS.Data.project.owner_id) {
      NS.Data.project.owner = NS.Data.user.username;
    }

    projectModel = new NS.ProjectModel(NS.Data.project);
    ProjectView = NS.Data.isOwner ? NS.ProjectAdminView : NS.ProjectView;

    window.projectModel = projectModel;

    NS.app.mainRegion.show(new ProjectView({
      model: projectModel,
      collection: projectModel.get('sections')
    }));

    if (window.location.pathname.indexOf('/new/') !== -1 && NS.Data.isOwner) {
      NS.app.overlayRegion.show(new NS.WelcomeModalView());
    }

  });

  // Init =====================================================================
  $(function() {
    NS.app.start();
  });

}(Planbox, jQuery));