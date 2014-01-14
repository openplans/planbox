/*globals Backbone jQuery Handlebars */

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
  NS.EventAdminView = Backbone.Marionette.ItemView.extend({
    template: '#event-admin-tpl',
    tagName: 'li',
    className: 'event draggable'
  });

  NS.ProjectAdminView = Backbone.Marionette.CompositeView.extend({
    template: '#project-admin-tpl',
    itemView: NS.EventAdminView,
    itemViewContainer: '.event-list',
    ui: {
      saveBar: '.save-bar',
      saveBtn: '.save-btn',
      editables: '[contenteditable]:not(.event [contenteditable])',
      statusSelector: '.status-selector',
      statusLabel: '.project-status'
    },
    events: {
      'blur @ui.editables': 'handleEditableBlur',
      'change @ui.statusSelector': 'handleStatusChange',
      'click @ui.saveBtn': 'handleSave'

    },
    modelEvents: {
      'change': 'dataChanged'
    },
    collectionEvents: {
      'change': 'dataChanged',
      'add':    'dataChanged',
      'remove': 'dataChanged'
    },
    handleEditableBlur: function(evt) {
      var $target = $(evt.target),
          attr = $target.attr('data-attr'),
          val = $target.text();

      evt.preventDefault();

      // Set the value of what was just blurred. Setting an event to the same
      // value does not trigger a change event.
      this.model.set(attr, val);
    },
    handleStatusChange: function(evt) {
      var $target = $(evt.target),
          attr = $target.attr('data-attr'),
          val = $target.val();

      evt.preventDefault();

      this.ui.statusLabel
        .removeClass('project-status-not-started project-status-active project-status-complete')
        .addClass('project-status-'+val)
        .find('strong').text(val);

      this.model.set(attr, val);
    },
    handleSave: function(evt) {
      evt.preventDefault();
      this.model.save();
      this.ui.saveBar.addClass('is-hidden');
    },
    dataChanged: function() {
      // Show the save button
      this.ui.saveBar.removeClass('is-hidden');
    }
  });


}(Planbox, jQuery));