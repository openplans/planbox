/*globals Backbone jQuery Handlebars Modernizr _ */

var Planbox = Planbox || {};

(function(NS, $) {
  'use strict';

    // Handlebars support for Marionette
  Backbone.Marionette.TemplateCache.prototype.compileTemplate = function(rawTemplate) {
    return Handlebars.compile(rawTemplate);
  };

  // View =====================================================================
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
      visibilityToggle: '[name=project-public]'
    },
    events: {
      'blur @ui.editables': 'handleEditableBlur',
      'change @ui.statusSelector': 'handleStatusChange',
      'change @ui.visibilityToggle': 'handleVisibilityChange',
      'click @ui.saveBtn': 'handleSave',
      'click @ui.addBtn': 'handleAddClick'
    },
    modelEvents: {
      'change': 'dataChanged'
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
      var self = this;

      this.model.save(null, {
        success: function(model) {
          var path = '/' + NS.Data.user.username + '/' + model.get('slug') + '/';

          if (window.location.pathname !== path) {
            if (Modernizr.history) {
              window.history.pushState('', '', path);
            } else {
              window.location = path;
            }
          }

          self.render();
        },
        error: function() {
          window.alert('Unable to save your project. Please try again.');
        }
      });
      this.ui.saveBtn.addClass('btn-disabled');
    },
    handleAddClick: function(evt) {
      evt.preventDefault();

      this.collection.add({});

      this.$('.event-title.content-editable').focus();
    },
    dataChanged: function() {
      // Show the save button
      this.ui.saveBtn.removeClass('btn-disabled');
    }
  });


}(Planbox, jQuery));