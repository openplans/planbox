/*globals Backbone, jQuery, Modernizr, Handlebars */

var Planbox = Planbox || {};

(function(NS, $) {
  'use strict';

  NS.ActivityPanelView = Backbone.Marionette.Layout.extend({
    template: '#activity-panel-tpl',
    regions: {
    },

    initialize: function(options) {
      this.app = options.app;
    },

    onShow: function() {
      this.app.triggerMethod('show:projectDashboard:activityPanel:before', this);
      this.showRegions();
      this.app.triggerMethod('show:projectDashboard:activityPanel:after', this);
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
    }
  });

}(Planbox, jQuery));