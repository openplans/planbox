/*globals Backbone jQuery Handlebars Modernizr _ Pen FileAPI chrono L */

var Planbox = Planbox || {};

(function(NS, $) {
  'use strict';

  NS.TextSectionAdminView = Backbone.Marionette.ItemView.extend(
    _.extend({}, NS.ContentEditableMixin, NS.SectionAdminMixin, {
      template: '#text-section-admin-tpl',
      tagName: 'section',
      id: NS.SectionMixin.id,

      ui: {
        editables: '[data-attr]',
        richEditables: '.rich-editable',
        deleteSection: '.delete-section'
      },
      events: {
        'blur @ui.editables': 'handleEditableBlur',
        'input @ui.editables': 'handleEditableBlur',
        'click @ui.deleteSection': 'handleDeleteSectionClick'
      },
      onRender: function() {
        this.initRichEditables();
        // This is so any changes to the menu_label will be reflected in the
        // slug.
        this.model.set('slug', '', {silent: true});
      }
    })
  );

}(Planbox, jQuery));