/*globals Backbone, jQuery, Modernizr, Handlebars */

var Planbox = Planbox || {};

(function(NS, $) {
  'use strict';

  NS.TeamListItemAdminView = Backbone.Marionette.ItemView.extend({
    template: '#team-list-item-admin-tpl',
    tagName: 'li'
  });

  NS.TeamListAdminView = Backbone.Marionette.CompositeView.extend({
    template: '#team-list-admin-tpl',
    itemView: NS.TeamListItemAdminView,
    itemViewContainer: '.team-list',

    ui: {
      newTeamButton: '.new-team-button',
      newTeamForm: '.new-team-form',
      newTeamCreateButton: '.new-team-create-button',
      newTeamCancelButton: '.new-team-cancel-button',
      newTeamFields: '[data-attr]'
    },
    events: {
      'click @ui.newTeamButton': 'handleNewTeamButtonClick',
      'click @ui.newTeamCancelButton': 'handleNewTeamCancelButtonClick',
      'submit @ui.newTeamForm': 'handleNewTeamFormSubmit'
    },

    hideNewTeamForm: function() {
      this.ui.newTeamButton.show();
      this.ui.newTeamForm.addClass('hide');
    },

    showNewTeamForm: function() {
      this.ui.newTeamButton.hide();
      this.ui.newTeamForm.removeClass('hide');
    },

    handleNewTeamButtonClick: function(evt) {
      evt.preventDefault();
      this.showNewTeamForm();
    },

    handleNewTeamCancelButtonClick: function(evt) {
      evt.preventDefault();
      this.hideNewTeamForm();
    },

    handleNewTeamFormSubmit: function(evt) {
      evt.preventDefault();

      var self = this,
          teamData = {};

      // Start by adding the current profile (user) as a member.
      teamData.members = [{id: this.model.id}];

      // For each data-attr in the form, add to the team data.
      this.ui.newTeamFields.each(function(i, field) {
        var attrName = field.getAttribute('data-attr'),
            attrVal = field.value;
        teamData[attrName] = attrVal;
      });

      // Create a new team based on the team data.
      this.model.get('teams').create(teamData, {
        wait: true,
        success: function() {
          self.ui.newTeamForm[0].reset();
          self.hideNewTeamForm();
        }
      });
    }
  });

}(Planbox, jQuery));