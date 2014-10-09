/*globals Backbone, jQuery, Modernizr, Handlebars */

var Planbox = Planbox || {};

(function(NS, $) {
  'use strict';

  // Exceptions ===============================================================
  NS.profileException = function(message, data) {
    return NS.genericException('ProfileException', message, data);
  };

  // App ======================================================================
  // (NS.app is defined in base-app.js)

  NS.app.addInitializer(function(options) {
    NS.Utils.logEvents('body', 'profile-dashboard');
  });

  NS.app.addInitializer(function(options){
    NS.app.profileModel = new NS.ProfileModel(NS.Data.profile);
    NS.app.projectsCollection = NS.app.profileModel.get('projects');
    NS.app.membersCollection = NS.app.profileModel.get('members');

    NS.app.mainRegion.show(new NS.ProfileAdminView({
      model: NS.app.profileModel
    }));
  });

}(Planbox, jQuery));