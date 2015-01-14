/*globals Backbone, jQuery, Modernizr, Handlebars */

var Planbox = Planbox || {};

(function(NS, $) {
  'use strict';

  // Exceptions ===============================================================
  NS.projectException = function(message, data) {
    return genericException('ProjectException', message, data);
  };

  // App ======================================================================
  NS.app.addInitializer(function(options){
    NS.app.projectModel = new NS.ProjectModel(NS.Data.project);
    NS.app.sectionCollection = NS.app.projectModel.get('sections');

    NS.app.sectionCollection = new Backbone.Collection(NS.app.projectModel.get('sections').filter(function(model) {
      return model.get('active');
    }));

    NS.app.mainRegion.show(new NS.ProjectView({
      className: NS.app.projectModel.get('layout') + '-page',
      model: NS.app.projectModel,
      collection: NS.app.sectionCollection
    }));
  });

  NS.app.addInitializer(function(options) {
    NS.Utils.logEvents('body', 'project-page');
  });

}(Planbox, jQuery));