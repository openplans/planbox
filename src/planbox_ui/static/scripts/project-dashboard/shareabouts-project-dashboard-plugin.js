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

  NS.ShareaboutsDashboardPlugin = NS.Plugin.extend({
    initialize: function() {
      this.config = this.getShareaboutsConfig();

      this.dataset = new Backbone.Model();
      this.dataset.url = this.config.details.dataset_url;

      this.places = new Shareabouts.PlaceCollection();
      this.places.url = this.config.details.dataset_url.replace(/^\/|\/$/g, '') + '/places';

      this.submissions = new Shareabouts.PaginatedCollection();
      this.submissions.url = this.config.details.dataset_url.replace(/^\/|\/$/g, '') + '/submissions';

      // Log in to the Shareabouts server
      $.ajax({
        url: '/shareabouts/oauth-credentials',
        data: {'project_id': NS.Data.project.id},
        success: _.bind(this.fetchShareaboutsData, this)
      });
    },

    fetchShareaboutsData: function(credentials) {
      this.credentials = credentials;
      var addAccessToken = function(xhr) {
        xhr.setRequestHeader('Authorization', 'Bearer ' + credentials.access_token);
      };

      this.dataset.fetch({
        beforeSend: addAccessToken
      });

      this.places.fetchAllPages({
        data: {'include_private': true},
        beforeSend: addAccessToken
      });

      this.submissions.fetchAllPages({
        data: {'include_private': true},
        beforeSend: addAccessToken
      });

      this.app.on('show:projectDashboard:activityPanel:after', _.bind(this.onShowActivityPanel, this));
    },

    getShareaboutsConfig: function() {
      var projectSections = NS.Data.project.sections,
          shareaboutsSection = _.findWhere(projectSections, {type: 'shareabouts'});
      return shareaboutsSection;
    },

    onShowActivityPanel: function() {

    }
  });

}(Planbox, jQuery));