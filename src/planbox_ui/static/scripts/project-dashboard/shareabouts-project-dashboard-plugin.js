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

      this.app.on('show:projectDashboard:after', _.bind(this.onShowProjectDashboard, this));
      this.app.on('show:projectDashboard:activityPanel:after', _.bind(this.onShowActivityPanel, this));
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
    },

    getShareaboutsConfig: function() {
      var projectSections = NS.Data.project.sections,
          shareaboutsSection = _.findWhere(projectSections, {type: 'shareabouts'});
      return shareaboutsSection;
    },

    _addManagerTab: function(view) {
      var tabTemplate = Handlebars.templates['shareabouts-manager-tab-tpl'],
          sectionTemplate = Handlebars.templates['shareabouts-manager-content-tpl'];
      view.$('.tabs').append(tabTemplate());
      view.$('.tabs-content').append('<section role="tabpanel" aria-hidden="true" class="content" id="panel-manage"></section>');

      view.addRegion('shareaboutsManagerRegion', '#panel-manage');
      view.shareaboutsManagerRegion.show(new NS.ManagePlacesView({
        plugin: this
      }));
    },

    onShowProjectDashboard: function(view) {
      this._addManagerTab(view);
    },

    onShowActivityPanel: function() {

    }
  });

}(Planbox, jQuery));