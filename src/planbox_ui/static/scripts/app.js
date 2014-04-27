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
    modalRegion: '#modal-container'
  });

  NS.app.addInitializer(function(options){
    var projectModel, ProjectView, sectionCollection;

    if (NS.Data.isEditable && !NS.Data.project.owner_id) {
      NS.Data.project.owner = NS.Data.user.username;
    }

    projectModel = new NS.ProjectModel(NS.Data.project);
    sectionCollection = projectModel.get('sections');

    if (!NS.Data.isEditable) {
      ProjectView = NS.ProjectView;
      sectionCollection = new Backbone.Collection(projectModel.get('sections').filter(function(model) {
        return model.get('active');
      }));
    } else if (projectModel.isNew()) {
      ProjectView = NS.ProjectSetupView;
    } else {
      ProjectView = NS.ProjectAdminView;
    }

    NS.app.mainRegion.show(new ProjectView({
      model: projectModel,
      collection: sectionCollection
    }));

    if (window.location.pathname.indexOf('/new/') !== -1 && NS.Data.isEditable) {
      // NS.showProjectSetupModal(projectModel);
      // NS.app.overlayRegion.show(new NS.WelcomeModalView());
    }
  });

  // Init =====================================================================
  $(function() {
    NS.app.start();
  });

}(Planbox, jQuery));