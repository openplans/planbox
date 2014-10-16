/*globals Backbone, jQuery, Modernizr, Handlebars */

var Planbox = Planbox || {};

(function(NS, $) {
  'use strict';

  // Exceptions ===============================================================
  NS.shareaboutsException = function(message, data) {
    return NS.genericException('ShareaboutsException', message, data);
  };

  // App ======================================================================
  // (NS.app is defined in base-app.js)

  var initializePlugin = function() {
    var PluginNS = NS.app.Shareabouts = NS.app.Shareabouts  || {};

    var syncWithCredentials = function(method, model, options) {
      _.defaults(options || (options = {}), {
        xhrFields: {withCredentials: true}
      });

      return Backbone.sync.apply(this, [method, model, options]);
    };

    if (!PluginNS.section) {
      PluginNS.section = NS.app.projectModel.get('sections').findWhere({type: 'shareabouts'});
    }

    if (!PluginNS.dataset) {
      PluginNS.dataset = new Backbone.Model();
      PluginNS.dataset.url = PluginNS.section.get('details').dataset_url;
      PluginNS.dataset.sync = syncWithCredentials;
      PluginNS.dataset.fetch();
    }

    // if (!PluginNS.places) {
    //   PluginNS.places = new Shareabouts.PlaceCollection();
    //   PluginNS.places.url = PluginNS.section.get('dataset_url') + '/places';
    // }
  };

  NS.app.on('show:projectDashboard:activityPanel:after', function() {
    initializePlugin();
  });

}(Planbox, jQuery));