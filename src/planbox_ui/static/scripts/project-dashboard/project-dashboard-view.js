/*globals Backbone, jQuery, Modernizr, Handlebars */

var Planbox = Planbox || {};

(function(NS, $) {
  'use strict';

  NS.ProjectDashboardView = Backbone.Marionette.Layout.extend({
    template: '#project-dashboard-tpl',
    regions: {
      // profileDetailsRegion: '.profile',
      // projectListRegion: '.project-list',
      // memberListRegion: '.member-list',
      activityPanel: '#panel-activity'
    },

    initialize: function(options) {
      this.app = options.app;
    },

    initFixedTableHeader: function() {
      $(window).on('load resize', function() {
        if (window.matchMedia(Foundation.media_queries.large).matches) {
          var tbodyHeight = $(window).height() - $('#datatable table').offset().top - 45;
          $('#datatable tbody').css({ maxHeight: tbodyHeight });
        } else {
          $('#datatable tbody').css({ maxHeight: 'none' });
        }
      });
    },

    onShow: function() {
      this.app.triggerMethod('show:projectDashboard:before', this);
      this.showRegions();

      this.initFixedTableHeader();

      // TODO: Don't hardcode this. Loop through project's data to get column classes.
      var options = {
        valueNames: [
         'dataset'
        ,'description'
        ,'geometry'
        ,'id'
        ,'lat'
        ,'lng'
        ,'dragPoint'
        ,'geocodeQuality'
        ,'geocodeQualityCode'
        ,'linkId'
        ,'mapUrl'
        ,'postalCode'
        ,'sideOfStreet'
        ,'street'
        ,'locationtype'
        ,'name'
        ,'notes_public'
        ,'submitter_email'
        ,'submitter'
        ,'avatar_url'
        ,'submitterid'
        ,'submittername'
        ,'updated_datetime'
        ,'url'
        ,'user_token'
        ,'visible'
        ]
      };
      new List('datatable', options);
      this.app.triggerMethod('show:projectDashboard:after', this);
    },

    showRegions: function() {
      // this.profileDetailsRegion.show(new NS.ProfileDetailsAdminView({
      //   model: this.model
      // }));
      // this.projectListRegion.show(new NS.ProjectListAdminView({
      //   model: this.model,
      //   collection: this.model.get('projects')
      // }));
      // this.memberListRegion.show(new NS.MemberListAdminView({
      //   model: this.model,
      //   collection: this.model.get('members')
      // }));
      this.activityPanel.show(new NS.ActivityPanelView({
        model: this.model,
        app: this.app
      }));
    }
  });

}(Planbox, jQuery));