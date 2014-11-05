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
    ui: {
      flavor: '.flavor',
      showFlavorsBtn: '.show-all-flavors'
    },
    events: {
      'click @ui.showFlavorsBtn': 'handleShowFlavors'
    },

    hideCopiousFlavors: function() {
      if ( this.ui.flavor.length > 4 ) {
        this.$('.flavor:gt(3)').hide().addClass('some-padding-top');
        $('<p class="no-margins some-padding-top text-center"><a class="show-all-flavors button tiny radius no-margins less-padding" href="#">&nbsp;SHOW ALL TEMPLATES&nbsp;</a></p>').insertAfter('#flavor-chooser');
      }
    },
    handleShowFlavors: function(evt) {
      evt.preventDefault();
      this.$('.flavor:gt(3)').show();
      this.$('.show-all-flavors').parent('p').hide();
    },

    onShow: function() {
      this.showRegions();
      this.hideCopiousFlavors();
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