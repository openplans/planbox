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

  NS.ShareaboutsProjectEditorPlugin = NS.Plugin.extend({
    initialize: function() {
      this.config = this.getShareaboutsConfig();
    },

    getShareaboutsConfig: function() {
      var projectSections = NS.Data.project.sections,
          shareaboutsSection = _.findWhere(projectSections, {type: 'shareabouts'});
      return shareaboutsSection;
    },

    presave: function(project, options) {
      var self = this,
          section = project.get('sections').findWhere({type: 'shareabouts'});

      if (!section.get('details').dataset_url) {
        // Create the dataset and set the dataset url on the section model
        $.ajax({
          url: '/shareabouts/create-dataset',
          type: 'POST',
          data: {
            dataset_slug: NS.Data.owner.slug + '-' + (new Date()).getTime()
          },
          success: function(data) {
            section.set('dataset_url', data['dataset_url']);
            self.shareaboutsAccessData = data;
          },
          error: function(xhr, status, error) {
            NS.showErrorModal('Unable to activate Shareabouts',
              'There was a temporary problem while we were setting up your ' +
              'Shareabouts map.',
              'We\'ve been notified and will investigate it right away. ' +
              'This is likely a temporary issue so please try again shortly.');
          },
          complete: function() {
            options.nextHook();
          }
        });
      } else {
        options.nextHook();
      }
    },

    postsave: function(project, options) {
      var self = this,
          section = project.get('sections').findWhere({type: 'shareabouts'});

      if (self.shareaboutsAccessData) {
        self.shareaboutsAccessData.project_id = project.id;
        $.ajax({
          url: '/shareabouts/authorize-project',
          type: 'POST',
          data: self.shareaboutsAccessData,
          success: function(data) {
            delete self.shareaboutsAccessData;
          },
          error: function(xhr, status, error) {
            NS.showErrorModal('Unable to activate Shareabouts',
              'There was a temporary problem while we were setting up your ' +
              'Shareabouts map.',
              'We\'ve been notified and will investigate it right away. ' +
              'This is likely a temporary issue so please try again shortly.');
          },
          complete: function() {
            options.nextHook();
          }
        });
      } else {
        options.nextHook();
      }
    }
  });

}(Planbox, jQuery));