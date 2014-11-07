/*globals Backbone, jQuery, Modernizr, Handlebars */

var Planbox = Planbox || {};

(function(NS, $) {
  'use strict';

  NS.ProjectListEmptyAdminView = Backbone.Marionette.ItemView.extend({
    template: '#project-list-empty-admin-tpl',
    tagName: 'li'
  });

  NS.ProjectListItemAdminView = Backbone.Marionette.ItemView.extend(
    _.extend({}, NS.FormErrorsMixin, {
      template: '#project-list-item-admin-tpl',
      tagName: 'li',
      className: 'project',
      ui: {
        form: '.slug-form', // FormErrorsMixin expects a `form` ui element
        slugForm: '.slug-form',
        slugField: '.slug-field',
        changeSlugBtn: '.change-slug',
        cancelSlugBtn: '.cancel-slug-change'
      },
      events: {
        'click @ui.changeSlugBtn': 'handleOpenSlugForm',
        'click @ui.cancelSlugBtn': 'handleCloseSlugForm',
        'submit @ui.slugForm': 'handleSlugFormSubmit'
      },
      handleOpenSlugForm: function(evt) {
        evt.preventDefault();
        var slugWidth = this.$('.slug').width();
        this.ui.slugField.width(Math.max(slugWidth, 20));
        this.$('.url').addClass('hide');
        this.$('form').removeClass('hide');
        $('.slug-field').select();
      },
      handleCloseSlugForm: function(evt) {
        evt.preventDefault();
        this.$('.url').removeClass('hide');
        this.$('form').addClass('hide');
        this.render();
      },
      handleSlugFormSubmit: function(evt) {
        evt.preventDefault();
        var self = this;

        self.clearErrors();

        this.model.save({'slug': this.ui.slugField.val()}, {
          patch: true,
          wait: true,
          success: function() {
            self.render();
          },
          error: function(model, $xhr, options) {
            var errors;
            if ($xhr.status === 400) {
              errors = $xhr.responseJSON;
              self.showFormErrors(errors);
            } else {
              alert('Something went wrong while setting the plan slug.\n' +
                'We have been notified of the error and will look into it ASAP.');
              throw NS.profileException(
                'Failed to set project slug for project with id "' + model.get('id') + '". ' +
                'HTTP status ' + $xhr.status + ' ' + $xhr.statusText + '.');
            }
          }
        });
      },
      onRender: function() {
        this.initValidityMessages();
      }
    })
  );

  NS.ProjectListAdminView = Backbone.Marionette.CompositeView.extend({
    template: '#project-list-admin-tpl',
    itemView: NS.ProjectListItemAdminView,
    itemViewContainer: '.project-list',
    emptyView: NS.ProjectListEmptyAdminView,

    // Override Marionette 1.4.1 internal method to use the current model as
    // opposed to a blank model in the view options. This wouldn't be necessary
    // in the latest version, because we'd override emptyViewOptions.
    showEmptyView: function(){
      var EmptyView = this.getEmptyView();

      if (EmptyView && !this._showingEmptyView){
        this._showingEmptyView = true;
        var model = this.model;
        this.addItemView(model, EmptyView, 0);
      }
    },

    modelEvents: {
      'sync': 'handleModelSync'
    },

    handleModelSync: function() {
      this.render();
    },

    onShow: function() {
      $('#teamWelomeModal').foundation('reveal', 'open');
    }
  });

}(Planbox, jQuery));