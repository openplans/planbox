/*globals Backbone jQuery Handlebars Modernizr _ */

var Planbox = Planbox || {};

(function(NS, $) {
  'use strict';

    // Handlebars support for Marionette
  Backbone.Marionette.TemplateCache.prototype.compileTemplate = function(rawTemplate) {
    return Handlebars.compile(rawTemplate);
  };

  // View =====================================================================
  NS.ModalView = Backbone.Marionette.ItemView.extend({
    template: '#modal-tpl',
    className: 'overlay',
    ui: {
      closeBtn: '.btn-close',
    },
    events: {
      'click @ui.closeBtn': 'handleClose'
    },
    handleClose: function(evt) {
      evt.preventDefault();
      this.close();
    }
  });


  NS.EventView = Backbone.Marionette.ItemView.extend({
    template: '#event-tpl',
    tagName: 'li',
    className: 'event'
  });

  NS.ProjectView = Backbone.Marionette.CompositeView.extend({
    template: '#project-tpl',
    itemView: NS.EventView,
    itemViewContainer: '.event-list'
  });


  // Admin ====================================================================
  NS.ContentEditableMixin = {
    handleEditableBlur: function(evt) {
      var $target = $(evt.target),
          attr = $target.attr('data-attr'),
          val = $target.text();

      evt.preventDefault();

      // Set the value of what was just blurred. Setting an event to the same
      // value does not trigger a change event.
      this.model.set(attr, val);
    }
  };

  NS.showErrorModal = function(resp) {
    var statusCode = resp.status,
        respJSON = resp.responseJSON,
        title, subtitle, description;

    title = 'Unable to save.';
    if (statusCode === 0) {
      // No network connectivity
      subtitle = 'We were unable to reach our server.';
      description = 'It looks like your internet connection may have dropped. ' +
        'Please check your connection and try again.';
    } else if (statusCode === 400) {
      // Bad request (missing title, at this point)
      subtitle = 'You forgot to give your project a title.';
      description = 'Every good project needs a title. Give it a great ' +
        'one and save again. <small>Have a title? That\'s unexpected. ' +
        'Please contact us so we can look into it.</small>';
    } else if (statusCode === 401 || statusCode === 403 || statusCode === 404) {
      // Authentication error
      // NOTE: you get a 404 when trying to access a private project, which
      // could belong to the user but they're now signed out for some reason.
      subtitle = 'It looks like you\'re no longer signed in.';
      description = '<a href="" target="_blank">Click here</a> to sign back ' +
        'in. Then come back to this page and save again';
    } else if (statusCode >= 500) {
      // Unknown server error
      subtitle = 'An unexpected error occurred on our server.';
      description = 'This is usually a temporary problem. Wait a minute or ' +
        'two, then try again. It will probably work.';
    } else {
      // No idea
      subtitle = 'An unexpected error occurred on our server.';
      description = 'This is usually a temporary problem. Wait a minute or ' +
        'two, then try again. If you still have problems, please contact us ' +
        'and we\'ll work to resolve the problem right away.';
    }

    NS.app.overlayRegion.show(new NS.ModalView({
      model: new Backbone.Model({
        title: title,
        subtitle: subtitle,
        description: description
      })
    }));
  };

  NS.ProjectAdminModalView = Backbone.Marionette.ItemView.extend({
    template: '#project-admin-modal-tpl',
    className: 'overlay',
    ui: {
      closeBtn: '.btn-close',
      makePublicBtn: '.btn-public',
      makePublicContent: '.make-public-content',
      shareContent: '.share-content'
    },
    events: {
      'click @ui.closeBtn': 'handleClose',
      'click @ui.makePublicBtn': 'handleMakePublic'
    },
    handleClose: function(evt) {
      evt.preventDefault();
      this.close();
    },
    handleMakePublic: function(evt) {
      var self = this;

      evt.preventDefault();

      this.model.save({public: true}, {
        // We are not interested in change events that come from the server,
        // and it causes the save button to enable after saving a new project
        silent: true,

        success: function() {
          self.ui.makePublicContent.addClass('is-hidden');
          self.ui.shareContent.removeClass('is-hidden');
        },
        error: function(model, resp) {
          NS.showErrorModal(resp);
        }
      });
    }
  });

  NS.EventAdminView = Backbone.Marionette.ItemView.extend({
    template: '#event-admin-tpl',
    tagName: 'li',
    className: 'event',
    ui: {
      editables: '[contenteditable]',
      deleteBtn: '.delete-event-btn'
    },
    events: {
      'blur @ui.editables': 'handleEditableBlur',
      'click @ui.deleteBtn': 'handleDeleteClick'
    },
    initialize: function() {
      this.$el.attr('data-id', this.model.cid);
    },
    handleEditableBlur: NS.ContentEditableMixin.handleEditableBlur,
    handleDeleteClick: function(evt) {
      evt.preventDefault();

      if (window.confirm('Really delete?')) {
        // I know this is weird, but calling destroy on the model will sync,
        // and there's no url to support that since it's related to the project
        // model. So we're just going to do the remove directly.
        this.model.collection.remove(this.model);
      }
    }
  });

  NS.ProjectAdminView = Backbone.Marionette.CompositeView.extend({
    template: '#project-admin-tpl',
    itemView: NS.EventAdminView,
    itemViewContainer: '.event-list',
    ui: {
      editables: '[contenteditable]:not(.event [contenteditable])',
      saveBtn: '.save-btn',
      statusSelector: '.status-selector',
      statusLabel: '.project-status',
      addBtn: '.add-event-btn',
      visibilityToggle: '[name=project-public]',
      userMenuLink: '.user-menu-link',
      userMenu: '.user-menu'
    },
    events: {
      'blur @ui.editables': 'handleEditableBlur',
      'change @ui.statusSelector': 'handleStatusChange',
      'change @ui.visibilityToggle': 'handleVisibilityChange',
      'click @ui.saveBtn': 'handleSave',
      'click @ui.addBtn': 'handleAddClick',
      'click @ui.userMenuLink': 'handleUserMenuClick'
    },
    modelEvents: {
      'change': 'dataChanged',
      'sync': 'onSync'
    },
    collectionEvents: {
      'change':  'dataChanged',
      'add':     'dataChanged',
      'remove':  'dataChanged',
      'reorder': 'dataChanged'
    },
    onRender: function() {
      var self = this;

      this.$('.event-list').sortable({
        handle: '.handle',
        update: function(evt, ui) {
          var id = $(ui.item).attr('data-id'),
              model = self.collection.get(id),
              index = $(ui.item).index();

          // Silent because we don't want the list to rerender
          self.collection.moveTo(model, index);
        }
      });
    },
    onSync: function() {
      // When the model is synced with the server, we're going to rerender
      // the view to match the data.
      this.render();
    },
    handleEditableBlur: NS.ContentEditableMixin.handleEditableBlur,
    handleStatusChange: function(evt) {
      var $target = $(evt.target),
          attr = $target.attr('data-attr'),
          val = $target.val();

      evt.preventDefault();

      this.ui.statusLabel
        // .removeClass('project-status-not-started project-status-active project-status-complete')
        // .addClass('project-status-'+val)
        .find('strong').text(_.findWhere(NS.Data.statuses, {'value': val}).label);

      this.model.set(attr, val);
    },
    handleVisibilityChange: function(evt) {
      var $target = $(evt.target),
          attr = $target.attr('data-attr'),
          val = ($target.val() === 'true');

      evt.preventDefault();

      // For IE8 only
      this.ui.visibilityToggle.removeClass('checked');
      $target.addClass('checked');

      this.model.set(attr, val);
    },
    handleSave: function(evt) {
      evt.preventDefault();
      var self = this,
          $target = $(evt.target);

      if (!$target.hasClass('btn-disabled')) {
        this.model.save(null, {
          // We are not interested in change events that come from the server,
          // and it causes the save button to enable after saving a new project
          silent: true,
          success: function(model) {
            var path = '/' + NS.Data.user.username + '/' + model.get('slug') + '/';

            if (window.location.pathname !== path) {
              if (Modernizr.history) {
                window.history.pushState('', '', path);
              } else {
                window.location = path;
              }
            }

            if (!model.get('public')) {
              // Don't show the model if the project is already public
              NS.app.overlayRegion.show(new NS.ProjectAdminModalView({
                model: model
              }));
            }
          },
          error: function(model, resp) {
            NS.showErrorModal(resp);
          }
        });
      }
    },
    handleAddClick: function(evt) {
      evt.preventDefault();

      this.collection.add({});

      this.$('.event-title.content-editable').focus();
    },
    handleUserMenuClick: function(evt) {
      evt.preventDefault();
      this.ui.userMenu.toggleClass('is-open');
    },
    dataChanged: function() {
      // Show the save button
      this.ui.saveBtn.removeClass('btn-disabled');
    }
  });

}(Planbox, jQuery));