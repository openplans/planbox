/*globals Backbone, jQuery, Modernizr, Handlebars */

var Planbox = Planbox || {};

(function(NS, $) {
  'use strict';

  NS.ProfileAdminView = Backbone.Marionette.Layout.extend({
    template: '#profile-admin-tpl',
    regions: {
      profileDetailsRegion: '.profile-details',
      projectListRegion: '.project-list',
      memberListRegion: '.member-list'
    },

    onShow: function() {
      this.showRegions();
    },

    showRegions: function() {
      this.profileDetailsRegion.show(new NS.ProfileDetailsAdminView({
        model: this.model
      }));
      this.projectListRegion.show(new NS.ProjectListAdminView({
        collection: this.model.get('projects')
      }));
      this.memberListRegion.show(new NS.MemberListAdminView({
        collection: this.model.get('members')
      }));
    }
  });

}(Planbox, jQuery));