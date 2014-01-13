var Planbox = Planbox || {};

(function(NS, $) {
  'use strict';

  NS.controller = {
    'showProject': function(slug) {
      var projectModel = NS.app.projectCollection.findWhere({slug: slug});

      NS.app.mainRegion.show(new NS.ProjectView({
        model: projectModel
      }));
    },
    'anything': function() {
      console.log('No route was matched.');
    }
  };
}(Planbox, jQuery));