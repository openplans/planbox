/*globals Backbone, jQuery, Modernizr, Handlebars */

var Planbox = Planbox || {};

(function(NS, $) {
  'use strict';

  NS.ProfileDetailsAdminView = Backbone.Marionette.ItemView.extend(
    _.extend({}, NS.ImageDropZonesMixin, NS.ContentEditableMixin, NS.FormErrorsMixin, {
      template: '#profile-details-admin-tpl',
      ui: {
        imageDropZones: '.image-dnd',
        editables: '[data-attr]',
        richEditables: '.rich-editable',
        changeProfileBtn: '.profile-edit-button',
        cancelProfileBtn: '.cancel-profile-edit-button',
        form: '.profile-form'
      },
      events: {
        'blur @ui.editables': 'handleEditableBlur',
        'input @ui.editables': 'handleEditableBlur',
        'click @ui.changeProfileBtn': 'handleOpenProfileForm',
        'click @ui.cancelProfileBtn': 'handleCloseProfileForm',
        'submit @ui.form': 'handleProfileFormSubmit'
      },
      modelEvents: {
        'sync': 'handleModelSync'
      },
      handleOpenProfileForm: function(evt) {
        evt.preventDefault();
        $('.profile-details').addClass('hide');
        $('.profile-form').removeClass('hide');
      },
      handleCloseProfileForm: function(evt) {
        evt.preventDefault();
        this.resetForm();
        $('.profile-details').removeClass('hide');
        $('.profile-form').addClass('hide');
      },
      handleProfileFormSubmit: function(evt) {
        evt.preventDefault();
        var self = this;

        // Blur any focussed elements. Otherwise, blur will get called after
        // we call render. This is an issue because any values present in the
        // focussed field will get set on the model, even if it contradicts
        // what's coming down from the sync.
        this.$(':focus').blur();

        // Get rid of any previous errors.
        this.clearErrors();

        // Save the model.
        this.model.save({}, {
          wait: true,
          success: function() {
            self.render();
          },
          error: function(model, $xhr, options) {
            if ($xhr.status === 400) {
              self.showFormErrors($xhr.responseJSON);
            } else {
              alert('Something went wrong while saving the profile details.\n' +
                'We have been notified of the error and will look into it ASAP.');
              throw NS.profileException(
                'Failed to save the profile with id "' + model.get('id') + '". ' +
                'HTTP status ' + $xhr.status + ' ' + $xhr.statusText + '.');
            }
          }
        });
      },
      handleModelSync: function(model, attrs, options) {
        // On any given sync, the slug may have changed. Update the path.
        var path = '/' + model.get('slug') + '/';

        if (window.location.pathname !== path) {
          if (Modernizr.history) {
            window.history.pushState('', '', path);
          } else {
            window.location = path;
          }
        }
      },
      onRender: function() {
        this.initRichEditables();
        this.initDropZones();
      }
    })
  );

}(Planbox, jQuery));