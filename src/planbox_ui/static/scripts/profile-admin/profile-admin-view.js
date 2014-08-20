/*globals Backbone, jQuery, Modernizr, Handlebars */

var Planbox = Planbox || {};

(function(NS, $) {
  'use strict';

  NS.ProfileAdminView = Backbone.Marionette.Layout.extend({
    template: '#profile-admin-tpl',
    regions: {
      profileDetailsRegion: '.profile',
      projectListRegion: '.project-list',
      memberListRegion: '.member-list',
      teamListRegion: '.team-list'
    },

    onShow: function() {
      this.showRegions();
    },

    showRegions: function() {
      this.profileDetailsRegion.show(new NS.ProfileDetailsAdminView({
        model: this.model
      }));
      this.projectListRegion.show(new NS.ProjectListAdminView({
        model: this.model,
        collection: this.model.get('projects')
      }));
      this.memberListRegion.show(new NS.MemberListAdminView({
        model: this.model,
        collection: this.model.get('members')
      }));
      this.teamListRegion.show(new NS.TeamListAdminView({
        model: this.model,
        collection: this.model.get('teams')
      }));
    }
  });

}(Planbox, jQuery));