/*globals Backbone, jQuery, Modernizr, Handlebars */

var Planbox = Planbox || {};

(function(NS, $) {
  'use strict';

  NS.ActivityPanelView = Backbone.Marionette.Layout.extend({
    template: '#activity-panel-tpl',
    regions: {
      placeCountWidget: '.place-count-widget',
      commentCountWidget: '.comment-count-widget',
      supportCountWidget: '.support-count-widget'
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

      this.placeCountWidget.show(new NS.DatasetPlaceCountWidgetView({
        model: this.app.plugins[0].dataset
      }));
      this.commentCountWidget.show(new NS.DatasetCommentCountWidgetView({
        model: this.app.plugins[0].dataset
      }));
      this.supportCountWidget.show(new NS.DatasetSupportCountWidgetView({
        model: this.app.plugins[0].dataset
      }));
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