/*globals Backbone, jQuery, Modernizr, Handlebars */

var Planbox = Planbox || {};

(function(NS, $) {
  'use strict';

  NS.ProfileDetailsAdminView = Backbone.Marionette.ItemView.extend(
    _.extend({}, NS.ImageDropZonesMixin, NS.ContentEditableMixin, {
      template: '#profile-details-admin-tpl',
      ui: {
        imageDropZones: '.image-dnd',
        editables: '[data-attr]',
        richEditables: '.rich-editable',
        changeProfileBtn: '.profile-edit-button',
        cancelProfileBtn: '.cancel-profile-edit-button'
      },
      events: {
        'blur @ui.editables': 'handleEditableBlur',
        'input @ui.editables': 'handleEditableBlur',
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
      },
      onRender: function() {
        this.initRichEditables();
        this.initDropZones();
      }
    })
  );

}(Planbox, jQuery));