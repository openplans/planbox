/*globals Backbone, jQuery, Modernizr, Handlebars */

var Planbox = Planbox || {};

(function(NS, $) {
  'use strict';

  // Exceptions ===============================================================
  NS.projectException = function(message, data) {
    return NS.genericException('ProjectException', message, data);
  };

  // App ======================================================================
  // (NS.app is defined in base-app.js)

  NS.app.addInitializer(function(options) {
    NS.Utils.logEvents('body', 'project-dashboard');
  });

  NS.app.addInitializer(function(options){
    NS.app.projectModel = new NS.ProjectModel(NS.Data.project);
    NS.app.sectionCollection = NS.app.projectModel.get('sections');

    NS.app.mainRegion.show(new NS.ProjectDashboardView({
      className: NS.app.projectModel.get('layout') + '-dashboard project-dashboard',
      model: NS.app.projectModel,
      collection: NS.app.sectionCollection,
      app: NS.app
    }));
  });

}(Planbox, jQuery));