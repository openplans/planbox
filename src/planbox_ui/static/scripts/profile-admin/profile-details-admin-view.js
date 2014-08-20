/*globals Backbone, jQuery, Modernizr, Handlebars */

var Planbox = Planbox || {};

(function(NS, $) {
  'use strict';

  NS.ProfileDetailsAdminView = Backbone.Marionette.ItemView.extend({
    template: '#profile-details-admin-tpl',
    ui: {
      changeProfileBtn: '.profile-edit-button',
      cancelProfileBtn: '.cancel-profile-edit-button'
    },
    events: {
      'click @ui.changeProfileBtn': 'handleOpenProfileForm',
      'click @ui.cancelProfileBtn': 'handleCloseProfileForm'
    },
    handleOpenProfileForm: function(evt) {
      evt.preventDefault();
      $('.profile-details').addClass('hide');
      $('.profile-form').removeClass('hide');
    },
    handleCloseProfileForm: function(evt) {
      evt.preventDefault();
      $('.profile-details').removeClass('hide');
      $('.profile-form').addClass('hide');
    }
  });

}(Planbox, jQuery));