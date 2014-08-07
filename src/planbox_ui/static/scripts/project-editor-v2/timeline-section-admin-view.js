/*globals Backbone jQuery Handlebars Modernizr _ Pen FileAPI chrono L */

var Planbox = Planbox || {};

(function(NS, $) {
  'use strict';


  NS.TimelineSectionAdminView = NS.SortableListAdminView.extend(
    _.extend({}, NS.ContentEditableMixin, NS.SectionAdminMixin, {
      template: '#timeline-section-admin-tpl',
      tagName: 'section',
      id: NS.SectionMixin.id,

      itemView: NS.EventAdminView,
      itemViewContainer: '.event-list',

      ui: {
        editables: '[data-attr]:not(.event [data-attr])',
        itemList: '.event-list',
        newItemFocus: '.event-title:last',
        addBtn: '.add-event-btn',
        activeToggle: '.active-toggle',
        deleteSection: '.delete-section'
      },
      events: {
        'click @ui.addBtn': 'handleAddClick',
        'blur @ui.editables': 'handleEditableBlur',
        'change @ui.activeToggle': 'handleActivationChange',
        'click @ui.deleteSection': 'handleDeleteSectionClick'
      },
      onRender: function() {
        // We need to do this since SortableListAdminView and ContentEditableMixin
        // both override onRender.

        // ContentEditableMixin
        this.initRichEditables();
        // SortableListAdminView
        this.initSortableItemList();
      }
    })
  );

}(Planbox, jQuery));