/*globals Backbone, jQuery, Modernizr, Handlebars */

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

  NS.app.addInitializer(function() {
    // Handlebars support for Marionette
    Backbone.Marionette.TemplateCache.prototype.compileTemplate = function(rawTemplate) {
      return Handlebars.compile(rawTemplate);
    };
  });

  NS.app.addInitializer(function(options){
    var ProjectView;

    if (NS.Data.isEditable && !NS.Data.project.owner_id) {
      NS.Data.project.owner = NS.Data.user.username;
    }

    NS.app.projectModel = new NS.ProjectModel(NS.Data.project);
    NS.app.sectionCollection = NS.app.projectModel.get('sections');

    if (!NS.Data.isEditable) {
      ProjectView = NS.ProjectView;
      NS.app.sectionCollection = new Backbone.Collection(NS.app.projectModel.get('sections').filter(function(model) {
        return model.get('active');
      }));
    } else {
      ProjectView = NS.ProjectAdminView;
    }

    NS.app.mainRegion.show(new ProjectView({
      model: NS.app.projectModel,
      collection: NS.app.sectionCollection
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

  $(window).load(function() {
    // Moved this from the BaseProjectView onDomRefresh. This will wait until
    // all of the images have been loaded so that Magellan will funciton as
    // expected. Specifically, "sticking" to the right location when scrolling
    // and not overlapping with section title when someone links directly to
    // a hash.
    $(document).foundation({'magellan': {}});
  });

}(Planbox, jQuery));