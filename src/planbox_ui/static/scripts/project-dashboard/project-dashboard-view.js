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

    onShow: function() {
      this.app.triggerMethod('show:projectDashboard:before', this);
      this.showRegions();

      this.$('table').table();
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